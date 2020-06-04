#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import traceback

import redis as redis

# TODO code from https://github.com/aio-libs/aioredis/issues/439
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.pipe_adapter import SIGNAL_SHUTDOWN_START
from via_common.network.middleware import Middleware
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer


class MiddlewareRedis(Middleware):
    """
    MiddlewareRedis manages access to the redis middleware.

    The method subscribe_one_forever is blocking on redis. It uses a callback to forward
        the responsibility of handling messages to the caller object.

    The pub/sub workflow is: lpush on Channel <- brpoplpush on Channel and Channel + "_r",
        then a lrem on Channel + "_r".
        This implements a very basic fail-over mechanism by saving messages under Channel + "_r"
        until confirmation of processing
        It can be served on the main sync or async.

    The method register_shutdown_channel allows to add a chanel to the list called back on shutdown.
    """
    _SHUTDOWN = object()


    def __init__(self,
                 config: ConfigMixInServer,
                 config_logger: ConfigMixInLogger,
                 logger_queue=None) -> None:
        super().__init__(config)
        LoggerManager.set_child_logger_queue(config_logger, logger_queue)
        self.logger = LoggerManager.get_logger(__class__.__name__)
        self.conn = None
        self.registered_channel = []
        self.connected = False
        self.disconnecting = False


    def connect(self):
        """
        Ex.:
        def process(self, channel, callback):
            listener = MiddlewareRedis(host, port)
            listener.connect()
            for message in listener.subscribe('channel'):
                callback(message)
            forwarder = MiddlewareRedis(host, port)
            publish
        """
        self.conn = redis.Redis(host=self.host, port=self.port, password=self.password, encoding="utf-8", decode_responses=False)
        self._check_conn()
        if self.connected:
            self.disconnecting = False


    def shutdown(self):
        self.disconnecting = True
        for channel in self.registered_channel:
            try:
                self.conn.lpush(channel, SIGNAL_SHUTDOWN_START)
            except redis.TimeoutError as e:
                self.logger.error('Shutdown propagation (lpush) FAILED. Timeout on %s', channel)
                raise TimeoutError(e)
            except redis.ConnectionError as e:
                self.logger.error('Shutdown propagation (lpush) FAILED. Connection error on %s', channel)
                raise ConnectionError(e)


    def register_shutdown_channel(self, channel: str):
        self.registered_channel.append(channel)


    def publish(self, channel: str, message: str):
        if not self.disconnecting:
            self.logger.debug('Publishing message on %s: %s', channel, message[:64])
            try:
                self.conn.lpush(channel, message)
            except redis.TimeoutError as e:
                self.logger.error('Publish (lpush) FAILED. Timeout on %s', channel)
                raise TimeoutError(e)
            except redis.ConnectionError as e:
                self.logger.error('Publish (lpush) FAILED. Connection error on %s', channel)
                raise ConnectionError(e)
        else:
            raise RuntimeError('Disconnecting')


    def subscribe_one_forever(self, channel: str, callback_handle_message):
        while True:
            channel_r = "{}_r".format(channel)
            try:
                message = self.conn.brpoplpush(channel, channel_r)
            except redis.TimeoutError as e:
                self.logger.error('Subscribe brpoplpush FAILED. Timeout on %s', channel)
                raise TimeoutError(e)
            except redis.ConnectionError as e:
                self.logger.error('Subscribe brpoplpush FAILED. Connection error on %s', channel)
                raise ConnectionError(e)
            # Check if shutting down
            if message == SIGNAL_SHUTDOWN_START:
                self.logger.warning('Shutting down middleware channel %s', channel)
                break
            # end if message == SIGNAL_SHUTDOWN_START
            try:
                if callback_handle_message:
                    callback_handle_message(message)
            except Exception as ignore:
                self.logger.warning('Got a message but Exception on callback on channel {}. Error:\n'.format(str(channel), traceback.print_exc()))
            else:  # remove the backup message on redis
                try:
                    self.conn.lrem(channel_r, -1, message)
                except redis.TimeoutError as e:
                    self.logger.error('Subscribe processing of lrem FAILED. Timeout on %s', channel)
                    raise TimeoutError(e)
                except redis.ConnectionError as e:
                    self.logger.error('Subscribe processing of lrem FAILED. Connection error on %s', channel)
                    raise ConnectionError(e)


    def _check_conn(self):
        try:
            self.conn.ping()
            self.connected = True
            self.logger.warning('Ping to middleware {}:{} is a SUCCESS'.format(self.host, self.port))
        except redis.ConnectionError as e:
            self.logger.error('Ping to middleware {}:{} is a FAILURE'.format(self.host, self.port))
            raise ConnectionError(e)
        except Exception as e:
            self.logger.error('Ping to middleware {}:{} is a FAILURE, with unknown exception: {}'.format(self.host, self.port, e))
            raise ConnectionError(e)
