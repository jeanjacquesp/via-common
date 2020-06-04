#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import time
from functools import partial
from multiprocessing import Queue
from multiprocessing.managers import BaseManager

from via_common.multiprocess.logger_manager import LoggerManager
from via_common.util.config_mixin_server import ConfigMixInServer


class QueueManager:
    """
    Helper object to manage the life cycle of the multiprocessing queues and
        the multiprocessing BaseManager.

    It uses a BaseManager for a specific host, port and authkey.

    The main process should instantiate only one QueueManager. In theory multiple
        instances could be used, but it was not intended to be used this way.
    """


    def __init__(self, config_internal_conn: ConfigMixInServer, queue_name_list=[]):
        self.config_internal_conn = config_internal_conn
        self.queue_name_list = queue_name_list
        #
        self.logger = LoggerManager.get_logger(__class__.__name__)
        self.system_queue = Queue()
        self.logger_queue = LoggerManager.get_logger_queue()
        self.manager = None
        #
        self._init_queue()


    def get_system_queue(self):
        """
        A callable for registering the system queue.
        """
        return self.system_queue


    def get_logger_queue(self):
        """
        A callable for registering the logger queue.
        """
        return self.logger_queue


    def get_queue_by_name(self, queue_name):
        return self.__dict__[queue_name]


    def _init_queue(self):
        """
        Creates and registers the multiprocessing queues.
        """
        self.logger.info('Creating the root queue manager to {},{}'
                         .format(self.config_internal_conn.host(), self.config_internal_conn.port()))

        self.manager = BaseManager(address=(self.config_internal_conn.host(),
                                            self.config_internal_conn.port()),
                                   authkey=self.config_internal_conn.authkey().encode())
        is_error = False
        try:
            self.manager.register('system_queue', callable=self.get_system_queue)
        except EOFError as e:
            self.logger.fatal('Exception while setting the publication_queue: {}'.format(e))
            is_error = True
        try:
            self.manager.register('logger_queue', callable=self.get_logger_queue)
        except EOFError as e:
            self.logger.fatal('Exception while setting the publication_queue: {}'.format(e))
            is_error = True
        if self.queue_name_list:
            for queue_name in self.queue_name_list:
                self.__dict__[queue_name] = Queue()
                try:
                    self.manager.register(queue_name, callable=partial(self.get_queue_by_name, queue_name=queue_name))
                except EOFError as e:
                    self.logger.fatal('Exception while setting the queue {}. Error: {}'.format(queue_name, e))
                    is_error = True
            # end for queue_name in queue_name_list
        # end if queue_name_list
        if is_error:
            raise ConnectionError('Cannot start the broker because of previous exception (cf. logs)')
        self.manager.start()
        self.logger.info('Queue manager initialised')
        time.sleep(0.25)
