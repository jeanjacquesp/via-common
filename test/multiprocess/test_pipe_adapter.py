from multiprocessing import Pipe
from unittest.mock import patch

import pytest

from via_common.multiprocess.pipe_adapter import PipeAdapter


pipe_recved = False
callbacked = False


def pipe_recv_called():
    global pipe_recved
    pipe_recved = True


def callback():
    global callbacked
    callbacked = True


@patch("multiprocessing.connection._ConnectionBase.recv", lambda _: pipe_recv_called())
class TestPipeAdapter:
    pipe = None
    pipe_receiver = None


    @pytest.fixture(scope="class")
    def setup(self):
        self.__class__.pipe_receiver, _ = Pipe(duplex=False)
        self.__class__.pipe = PipeAdapter(self.pipe_receiver, callback)


    @pytest.fixture(scope="function")
    def setup_method(self):
        global pipe_recved
        global callbacked
        pipe_recved = False
        callbacked = False


    def test_listen(self, setup, setup_method):
        global pipe_recved
        global callbacked
        self.pipe.listen(self.pipe_receiver, callback)
        assert pipe_recved
        assert callbacked


    def test_start(self, setup, setup_method):
        global pipe_recved
        global callbacked
        self.pipe.start()
        import time
        time.sleep(0.25)
        assert pipe_recved
        assert callbacked
