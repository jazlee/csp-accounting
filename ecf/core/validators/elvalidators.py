"""
ElixirValidations - provide model-level validations of fields

currently the following are available:
--------------------------------------
validates_presence_of(fieldname) - checks that the field is not empty
validates_range_of(fieldname,min,max) - checks that the field is between min and max (not only for numbers)
validates_format_of(fieldname,regex) - validates against a given regex
validates_uniqueness_of(fieldname) - like a unique index
validates_numericality_of(fieldname,integer_only=False) - checks that the field can be converted to a number

usage:
------
from elvalidators import *
class Person(Entity):
    username=Field(Unicode(30),nullable=False,index=True)
    email=Field(Unicode,nullable=False)
    age=Field(Integer,nullable=False)

    validates_uniqueness_of('username')
    validates_presence_of('username', 'email')
    validates_format_of('email',re.compile("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])"))
    validates_numericality_of('age',integer_only = True)
"""

from savalidators import *
from elixir.statements import Statement

class ElixirValidatesPresenceOf(object):
    def __init__(self, entity, *args):
        for fieldname in args:
            entity._descriptor.add_mapper_extension(Validator(presence_of(fieldname)))

class ElixirValidatesRangeOf(object):
    def __init__(self, entity, fieldname, min, max):
        entity._descriptor.add_mapper_extension(Validator(range_of(fieldname, min, max)))

class ElixirValidatesFormatOf(object):
    def __init__(self, entity, fieldname, regex):
        entity._descriptor.add_mapper_extension(Validator(format_of(fieldname, regex)))

class ElixirValidatesUniquenessOf(object):
    def __init__(self, entity, *args):
        for fieldname in args:
            entity._descriptor.add_mapper_extension(Validator(uniqueness_of(fieldname)))

class ElixirValidatesNumericalityOf(object):
    def __init__(self, entity, fieldname, integer_only=False):
        entity._descriptor.add_mapper_extension(Validator(numericality_of(fieldname,integer_only)))

validates_presence_of       = Statement(ElixirValidatesPresenceOf)
validates_range_of          = Statement(ElixirValidatesRangeOf)
validates_format_of         = Statement(ElixirValidatesFormatOf)
validates_uniqueness_of     = Statement(ElixirValidatesUniquenessOf)
validates_numericality_of   = Statement(ElixirValidatesNumericalityOf)

__all__ = ['ValidationException', 'validates_presence_of', 'validates_format_of',
           'validates_range_of', 'validates_uniqueness_of', 'validates_numericality_of',
           ]