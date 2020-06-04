#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import threading
import time
from abc import ABCMeta
from abc import abstractmethod
from multiprocessing.managers import BaseManager

from via_common.multiprocess.pipe_adapter import SIGNAL_SHUTDOWN_START
from via_common.network.middleware_redis import Middleware
from via_common.util.config_mixin_server import ConfigMixInServer


class BackgroundThread(metaclass=ABCMeta):
    """
    A helper MixIn to manage background threads for connecting to a middleware.

    Several threads can be started calling back on the "target" argument of the start method.

    The BackgroundThread setup the necessary plumbing for accessing in the multiprocessing
        system_queue to manage shutdown and other command if necessary.

    Derived classes are responsible for defining:
        - the shutdown mechanism. It can use the system_queue.
        - the logger object must be set by the derived classes.
    """


    def __init__(self, config_internal_conn: ConfigMixInServer, middleware: Middleware):
        self.config_internal_conn = config_internal_conn
        self.middleware = middleware
        self.logger = None
        self._initialise_thread_logger()
        if not self.logger:
            raise ValueError('The logger of the background thread must be setup')
        self.running = True
        self.system_queue = None
        #
        self._setup_system_queue()


    @abstractmethod
    def shutdown(self):
        # The mechanism uses a pipe to send a SIGNAL_SHUTDOWN_START command to each process.
        # The pipe is handled by an orchestrator.
        raise NotImplementedError


    @abstractmethod
    def _initialise_thread_logger(self):
        raise NotImplementedError


    def _start_background_async(self, target, args):
        # TODO log
        thread = threading.Thread(target=self._run_thread_forever, args=(target, args,), daemon=True)
        thread.start()
        self.logger.info('Background Thread started for connection to {}:{}'.format(self.middleware.host, self.middleware.port))


    def _run_thread_forever(self, target, args):
        self.logger.info('Connecting to middleware {}:{}'.format(self.middleware.host, self.middleware.port))
        try:
            self.middleware.connect()
        except ConnectionError:
            self.logger.fatal('Connection to middleware failed')
            if self.system_queue:
                self.system_queue.put(SIGNAL_SHUTDOWN_START)
                self.shutdown()
                return
        self.logger.info('Running target {}({})'.format(str(target), str(args)))
        target(*args)
        while True:
            # this part of the code might never be reach as target might be blocking
            command = self.system_queue.get()
            self.logger.info('Received a system command: {}'.format(command))
            if command == SIGNAL_SHUTDOWN_START:
                self.logger.info('Shutting down background thread')
                self.shutdown()
                break
            # end if command == SIGNAL_SHUTDOWN_START
        # end while True


    def _setup_system_queue(self):
        BaseManager.register('system_queue')
        manager = BaseManager(address=(self.config_internal_conn.host(),
                                       self.config_internal_conn.port()),
                              authkey=self.config_internal_conn.authkey().encode())
        time.sleep(0.25)
        attempt = 5
        while attempt:
            try:
                self.logger.debug('Connecting to the manager')
                manager.connect()
                break
            except Exception as e:
                self.logger.warning('Background thread BaseManager connect failed with exception: {}'.format(e))
                self.logger.warning('Retrying connect on background thread, attempt: {}'.format(6 - attempt))
                attempt -= 1
        # end while attempt

        if attempt == 0:
            raise ConnectionError("{} child process FAILED to start".format(self.__class__.__name__))

        # Create the object fields for the queues
        self.system_queue = manager.system_queue()
        self.logger.debug('Background thread initialised after attempt: {}'.format(6 - attempt))
