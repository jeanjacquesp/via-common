#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import logging
import logging.config
from importlib import reload
from logging.handlers import QueueListener
from multiprocessing import Queue

#
# Logger for multiprocessing
#
from via_common.util.config_mixin_logger import ConfigMixInLogger


class SimpleHandler:
    """
    Simple Handler for the QueueListener to forward records to the root logger handlers
    """


    def handle(self, record):
        logger = logging.getLogger(record.name)
        logger.handle(record)


class LoggerManager:
    """
    Root logger for the main process to aggregate the logs from all the sub-processes.

    LoggerManager works in conjunction with the ConfigMixInLogger.

    The main process initialise a QueueListener, while the multiprocessing logger queue
        is injected to each sub-process's config during the fork (spawn) initialisation by
        the ConfigMixInLogger.

    The logging config for sub-processes must be defined under 'subprocess' key in the config.

    The main process must call the init_root_logger to be able to catch any log messages from
        the sub-processes.
    """
    #: The config for the loggers
    config_logger = None

    #: The multiprocessing queue used to share log records between processes
    logger_queue = None

    #: The main process hold the unique instance of the logger QueueListener
    logger_queue_listener = None

    #: A trick to check if the get_logger is called by the main process or a child one
    # The trick works because we spawn the process, fork + execve on linux for a clean process
    pid = None

    config = None


    def __del__(self):
        LoggerManager.config_logger = None
        LoggerManager.logger_queue = None
        LoggerManager.logger_queue_listener = None
        LoggerManager.pid = None
        LoggerManager.config = None
        logging.shutdown()
        reload(logging)


    @classmethod
    def init_root_logger(cls, config: ConfigMixInLogger):
        """
        Called once by the main process only to initialise the queue and to set the PID for a trick
        """
        import os

        cls.pid = os.getpid()
        cls.logger_queue = Queue()
        cls.set_child_logger_queue(config, cls.logger_queue)


    @classmethod
    def set_child_logger_queue(cls, config: ConfigMixInLogger, logger_queue):
        """
        Each child process need to manually set the logger_queue once the multiprocessing base
        manager has started and queue is retrieved.
        """
        cls.logger_queue = logger_queue
        cls.config = config
        cls.config.set_logger_queue(cls.logger_queue)
        cls.config_logger = cls.config.get_config_dict()


    @classmethod
    def get_logger_queue(cls):
        return cls.logger_queue


    @classmethod
    def get_logger(cls, name):
        """
        This uses a trick to identify the main process from its children so that only the main one set up the config.
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            if cls.config:
                cls.config.set_logger_queue(cls.logger_queue)
                if cls.pid:  # main process
                    # it is time to create the log directories if they do not exist
                    cls._check_or_create_directory()
                    try:
                        logging.config.dictConfig(cls.config_logger['root'])
                    except ValueError as e:
                        raise Exception('Error while processing logger for Error: {}'.format(e))
                    # end try/except ValueError

                    # set up queue listener
                    if not cls.logger_queue_listener:
                        cls.logger_queue_listener = QueueListener(cls.logger_queue, SimpleHandler())
                        cls.logger_queue_listener.start()
                    # end if not cls.logger_queue_listener
                # end clause if cls.config, doing else now
                else:
                    # this is called by a child process.
                    logging.config.dictConfig(cls.config_logger['subprocess'])
                # end if cls.pid
            # end if cls.config
        # end if not logger.handlers
        return logger


    @classmethod
    def _check_or_create_directory(cls):
        if cls.config:
            def _check_or_create(file_path):
                import os
                directory = os.path.dirname(file_path)
                if not os.path.exists(directory):
                    os.makedirs(directory)


            # end def _check_or_create

            log_path = cls.config_logger['root']['handlers']['file']['filename']
            if log_path:
                _check_or_create(log_path)
            else:
                raise ValueError('Missing filename for logger|root|handlers|file')
            # if log_path
            error_path = cls.config_logger['root']['handlers']['errors']['filename']
            if error_path:
                _check_or_create(error_path)
            else:
                raise ValueError('Missing filename for logger|root|handlers|errors')
            # end if error_path
