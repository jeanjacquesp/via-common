#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


class Error:
    """
    A very simple class to hold error messages.

    This class is used for concatenating succession of errors that don't stop the
    flow.
    """


    def __init__(self):
        # prev_frame = inspect.currentframe().f_back
        # try:
        #     self.class_name = prev_frame.f_locals["self"].__class__.__name__
        # except KeyError:
        #     # it is a global function
        #     self.class_name = '<module>'
        # self.function_name = prev_frame.f_code.co_name
        # # TODO
        self._msg = []


    def __add__(self, other):
        # prev_frame = inspect.currentframe().f_back
        # try:
        #     class_name = prev_frame.f_locals["self"].__class__.__name__
        # except KeyError:
        #     # it is a global function
        #     class_name = '<module>'
        # function_name = prev_frame.f_code.co_name
        res = Error()
        # res.class_name = class_name
        # res.function_name = function_name
        res._msg.extend(self._msg)
        res._msg.extend(other._msg)
        return res


    def __str__(self):
        if self._msg:
            return '||'.join(self._msg)
        # if self._msg
        return ''


    def __bool__(self):
        return bool(self._msg)


    def __eq__(self, other):
        if self.__str__() == str(other):
            return True
        return False


    def add(self, message):
        if message:
            self._msg.append(message)


    def msg(self):
        return self.__str__()


    def render(self, prefix='||'):
        return '{}'.format(prefix).join(self._msg)


    def do_raise(self, type: Exception = RuntimeError):
        raise type(str(self))
