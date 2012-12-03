import unittest
from mock import MagicMock, Mock, sentinel
from nose.tools import *

from gutter.client.arguments.variables import *
from gutter.client.arguments import Base

from exam.decorators import fixture


class MyArgument(Base):

    class_var = True

    def __init__(self, *args, **kwargs):
        self.instance_var = True
        super(MyArgument, self).__init__(*args, **kwargs)

    def instance_method(self):
        pass

    @staticmethod
    def static_method(self):
        pass

    @property
    def property(self):
        pass


class TestBase(unittest.TestCase):

    argument = fixture(Base, sentinel.input)

    def test_applies_is_false_if_compatible_type_is_none(self):
        eq_(self.argument.COMPATIBLE_TYPE, None)
        eq_(self.argument.applies, False)

    def applies_is_true_if_input_type_is_compatible_type(self):
        self.argument.COMPATIBLE_TYPE = int
        ok_(type(self.argument.input) is not int)

        self.assertFalse(self.argument.applies)
        self.argument.input = 9
        self.assertTrue(self.argument.applies)

    def test_arguments_defaults_to_nothing(self):
        eq_(self.argument.variables, [])

    def test_only_returns_valid_instance_methods_for_subclasses(self):
        eq_(MyArgument(sentinel.input).variables, [MyArgument.instance_method])


class BaseVariableTest(object):

    interface_functions = ['__cmp__', '__hash__', '__nonzero__']

    @fixture
    def argument(self):
        return self.klass(self.valid_comparison_value)

    @fixture
    def interface_methods(self):
        return [getattr(self.argument, f) for f in self.interface_functions]

    def test_implements_comparison_methods(self):
        map(ok_, self.interface_methods)


class DelegateToValue(object):

    def test_delegates_all_interface_function_to_the_value_passed_in(self):
        value_passed_in = MagicMock()
        value_passed_in.__cmp__ = Mock()
        argument = self.klass(value_passed_in)

        for function in self.interface_functions:
            values_function = getattr(value_passed_in, function)
            arguments_function = getattr(argument, function)

            arguments_function(self.valid_comparison_value)
            values_function.assert_called_once_with(self.valid_comparison_value)


class ValueTest(BaseVariableTest, DelegateToValue, unittest.TestCase):

    klass = Value
    valid_comparison_value = 'marv'


class BooleanTest(BaseVariableTest, DelegateToValue, unittest.TestCase):

    klass = Boolean
    valid_comparison_value = True
    interface_functions = ['__cmp__', '__nonzero__']

    def test_hashes_its_hash_value_instead_of_value(self):
        boolean = Boolean(True, hash_value='another value')
        assert_not_equals(hash(True), hash(boolean))
        assert_equals(hash('another value'), hash(boolean))

    def test_creates_random_hash_value_if_not_provided(self):
        boolean = Boolean(True)
        assert_not_equals(hash(True), hash(boolean))
        assert_not_equals(hash(None), hash(boolean))

        assert_not_equals(hash(boolean), hash(Boolean(True)))


class StringTest(BaseVariableTest, DelegateToValue, unittest.TestCase):

    klass = String
    valid_comparison_value = 'foobazzle'
    interface_functions = ['__hash__']

    def test_cmp_compares_with_other_value(self):
        eq_(self.argument.__cmp__('zebra'), -1)
        eq_(self.argument.__cmp__('aardvark'), 1)
        eq_(self.argument.__cmp__('foobazzle'), 0)

    def test_nonzero_returns_if_truthy(self):
        ok_(String('hello').__nonzero__() is True)
        ok_(String('').__nonzero__() is False)
        ok_(String('0').__nonzero__() is True)
