import pytest

from via_common.util.error import Error


class TestError:

    def test_add(self):
        a = Error()
        a.add('A')
        # assert str(a) == '[TestError][test_msg]: A'
        assert a._msg == ['A']
        a.add('B')
        assert a._msg == ['A', 'B']


    def test_msg(self):
        a = Error()
        a.add('A')
        assert a.msg() == 'A'
        assert str(a) == 'A'
        a.add('B')
        assert a.msg() == 'A||B'
        assert str(a) == 'A||B'


    def test_addition(self):
        def test():
            f = Error()
            f.add('F')
            return f


        a = Error()
        a.add('A')
        b = Error()
        b.add('B')
        b.add('BB')
        c = Error()
        c += a
        d = a + b
        e = test()
        e.add('E')
        e += test()
        assert str(a) == 'A'
        assert str(b) == 'B||BB'
        assert str(c) == 'A'
        assert str(d) == 'A||B||BB'
        assert str(e) == 'F||E||F'


    def test_render(self):
        a = Error()
        a.add('A')

        assert a.render('<br>') == 'A'
        a.add('B')
        assert a.render() == 'A||B'
        assert a.render('<br>') == 'A<br>B'


    def test_do_raise(self):
        class SomeException(Exception):
            pass


        with pytest.raises(SomeException) as ctx:
            a = Error()
            a.add('A')
            a.do_raise(SomeException)
        assert ctx.errisinstance(SomeException)
        assert 'A' in ctx.exconly()
