#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import threading
from multiprocessing import Pipe


SIGNAL_SHUTDOWN_START = '#shutdown'
SIGNAL_SHUTDOWN_DONE = '#shutdown_done'


class PipeAdapter:
    """
    A simple helper class used for managing shutdown through Pipe
    """


    def __init__(self, pipe_receiver: Pipe, callback):
        self.pipe_receiver = pipe_receiver
        self.callback = callback
        self.worker = None


    @classmethod
    def listen(cls, pipe_receiver, callback):
        try:
            pipe_receiver.recv()
            callback()
        except EOFError:
            pass


    def start(self):
        self.worker = threading.Thread(target=self.listen,
                                       args=(self.pipe_receiver,
                                             self.callback,))
        self.worker.start()
