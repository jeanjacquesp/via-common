#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
import time
from abc import ABCMeta
from abc import abstractmethod
from multiprocessing import Process
from multiprocessing.managers import BaseManager

from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.pipe_adapter import PipeAdapter
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer


class ProcessMixin(metaclass=ABCMeta):
    """
        A helper MixIn to manage sub-process for connecting to a server.

        Each object can spawn only one sub-process.

        The object set-up the necessary plumbing for the sub-process to access the multiprocessing
            system_queue, logger_queue queue and any other queues given as arguments by name.

        Derived classes are responsible for defining:
            - the shutdown mechanism. It can use the system_queue.
            - the logger object must be set by the derived classes.
            - the _run_child_forever interface. For convenience the logger_queue is passed as an
                argument.
    """


    def __init__(self, process_name, config_internal_conn: ConfigMixInServer, config_logger: ConfigMixInLogger, queue_name_list, shutdown_receiver):
        self.process_name = process_name
        self.config_internal_conn = config_internal_conn
        self.config_logger = config_logger
        self.queue_name_list = queue_name_list
        self.shutdown_receiver = shutdown_receiver
        self.shutdown_handler = None
        self.system_queue = None
        self.impl = Process(target=self._run_child_process, args=(config_internal_conn.__class__, config_logger.__class__,), daemon=True)
        self.logger = None
        self._initialise_child_logger()
        if not self.logger:
            raise ValueError('The logger of the process object must be setup')


    @abstractmethod
    def shutdown(self):
        # The mechanism uses a pipe to send a SIGNAL_SHUTDOWN_START command to each process.
        # The pipe is handled by an orchestrator.
        raise NotImplementedError


    @abstractmethod
    def _initialise_child_logger(self):
        # the queue for the logger is set by ProcessMixin,
        # but the derived objects need to set the logger for themselves,
        # otherwise, the class name would be the one of the base class in the log
        raise NotImplementedError


    @abstractmethod
    def _run_child_forever(self):
        # The base class uses _run_child_process to initialise the process, then it passes responsibility
        # to the derived object to do further work is needed.
        raise NotImplementedError


    #
    # Process override
    #


    def start(self):
        self.impl.start()


    def join(self):
        self.impl.join()


    def close(self):
        self.impl.close()


    def get_process(self):
        return self.impl


    #
    # Process.target
    #


    def _run_child_process(self, config_conn_cls, config_logger_cls):
        # All this is to setup the logger_queue to be able to log.
        self.config_internal_conn = config_conn_cls()
        self.config_logger = config_logger_cls()

        # arguments here are passed through pickle. They cannot be class member
        self.shutdown_handler = PipeAdapter(self.shutdown_receiver, self.shutdown)
        self.shutdown_handler.start()

        if self.queue_name_list:
            for queue_name in self.queue_name_list:
                BaseManager.register(queue_name)
            # end for queue_name in queue_name_list
        # end if queue_name_list

        BaseManager.register('logger_queue')
        BaseManager.register('system_queue')
        manager = BaseManager(address=(self.config_internal_conn.host(),
                                       self.config_internal_conn.port()),
                              authkey=self.config_internal_conn.authkey().encode())
        time.sleep(0.5)
        attempt = 5
        while attempt:
            try:
                manager.connect()
                break
            except Exception as e:  # TODO exception: which one(s)
                attempt -= 1
        # end while attempt

        if attempt == 0:
            raise RuntimeError("{} child process FAILED to start".format((self.__class__.__name__)))

        # Create the object fields for the queues
        if self.queue_name_list:
            for queue_name in self.queue_name_list:
                self.__dict__[queue_name] = manager.__getattribute__(queue_name)()
            # end for queue_name in queue_name_list
        # end if queue_name_list

        # Set the queue for the logger
        self.system_queue = manager.system_queue()
        logger_queue = manager.logger_queue()
        LoggerManager.set_child_logger_queue(self.config_logger, logger_queue)
        self.logger = LoggerManager.get_logger(self.process_name)
        self.logger.info('Sub-process [{}] initialized'.format(self.process_name))

        self._run_child_forever(logger_queue)
