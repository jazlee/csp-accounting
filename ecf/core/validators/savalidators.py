"""
SqlAlchemy validations - provide validation extensions for the sqlalchemy models:
people_table = Table(....)
class Person(object)
    pass

mapper(Person, people_table,
       extension=[Validator(
                            range_of('age', 0, 150),
                            format_of('phone', re.compile(r'\d{4}-?\d{4}'))
                            numericality_of('foo','bar','some_next_field')
                           )
                 ]
      )
"""

from sqlalchemy.orm import MapperExtension, EXT_CONTINUE
import warnings

class ValidationException(Exception):
    def __init__(self,*args,**kwargs):
        self.errors = {}
        Exception.__init__(self,*args,**kwargs)

class Validator(MapperExtension):
    def __init__(self, *args):
        MapperExtension.__init__(self)
        self.validations_to_perform = args

    def before_insert(self, mapper, connection, instance):
        for validation in self.validations_to_perform:
            if not validation.validate(instance):
                msg = validation.get_error_message(instance)
                exc = ValidationException(msg)
                exc.errors[validation.field_to_validate] = msg
                raise exc

        return EXT_CONTINUE

    before_update = before_insert

class Validation(object):
    def validate(self):
        raise NotImplementedError

    def get_error_message(self):
        raise NotImplementedError

class FieldValidation(Validation):
    def __init__(self, field_to_validate, validation_rule):
        Validation.__init__(self)
        self.field_to_validate = field_to_validate
        self.validation_rule = validation_rule

    def validate(self, instance):
        return self.validation_rule(self.get_field_value(instance),instance)

    def get_error_message(self, instance):
        return "Validation of field %s (with rule %s) failed." % (self.field_to_validate, self.validation_rule)

    def get_field_value(self, instance):
        return getattr(instance, self.field_to_validate)

class FieldRangeValidation(FieldValidation):
    def __init__(self, field_to_validate, min, max):
        FieldValidation.__init__(self, field_to_validate, self._validate_field)
        self.min = min
        self.max = max

    def _validate_field(self, field_value):
        return self.min <= field_value <= self.max

    def get_error_message(self, instance):
        return 'Range validation of field "%s" of instance of class "%s" failed! %s.%s = %s (min=%d, max=%d)' % (self.field_to_validate, instance.__class__.__name__, instance.__class__.__name__, self.field_to_validate, self.get_field_value(instance), self.min, self.max)

class FieldFormatValidation(FieldValidation):
    def __init__(self, field_to_validate, regex):
        FieldValidation.__init__(self, field_to_validate, self._validate_field)
        self.regex = regex

    def _validate_field(self, field_value, instance):
        return not (self.regex.match(field_value) is None)

    def get_error_message(self, instance):
        return 'Format validation of field "%s" of instance of class "%s" failed! %s.%s = %s (regex=%s)' \
            % (self.field_to_validate, instance.__class__.__name__, instance.__class__.__name__, self.field_to_validate, \
             self.get_field_value(instance), self.regex.pattern)

class FieldPresenceValidation(FieldValidation):
    def __init__(self, field_to_validate):
        FieldValidation.__init__(self, field_to_validate, self._validate_field)

    def _validate_field(self, field_value, instance):
        if field_value:
            return True
        else:
            return False

    def get_error_message(self, instance):
        return 'Presence validation of field "%s" of instance of class "%s" failed! %s.%s = %s' \
            % (self.field_to_validate, instance.__class__.__name__, instance.__class__.__name__, \
               self.field_to_validate, self.get_field_value(instance))

class FieldUniquenessValidation(FieldValidation):
    def __init__(self,field_to_validate):
        FieldValidation.__init__(self, field_to_validate, self._validate_field)

    def _validate_field(self, field_value, instance):
        field = self.field_to_validate
        parms = {field:field_value}
        if not instance._sa_class_manager.mapper.c[field].index:
            warnings.warn('you are validating uniqueness of a possibly non-indexed field, this may cause '\
                          'performance issues',DeprecationWarning,2)
        #first should be faster than count
        if instance.__class__.query.filter_by(**parms).first():
            return False
        else:
            return True

    def get_error_message(self, instance):
        return 'Uniqueness validation of field "%s" failed! %s.%s = "%s" is not unique!' \
            % (self.field_to_validate, instance.__class__.__name__, \
               self.field_to_validate, self.get_field_value(instance))

class FieldNumericality(FieldValidation):
    def __init__(self,field_to_validate,integer_only):
        FieldValidation.__init__(self, field_to_validate, self._validate_field)
        self.integer_only = integer_only

    def _validate_field(self, field_value, instance):
        field = self.field_to_validate
        try:
            number = int(field_value)
            return True
        except ValueError:
            if self.integer_only:
                return false
            else:
                try:
                    number = float(field_value)
                    return True
                except ValueError:
                    return False
    def get_error_message(self, instance):
        return 'Numericality validation of field "%s" failed! %s.%s = "%s" is not numeric!' \
            % (self.field_to_validate, instance.__class__.__name__, \
               self.field_to_validate, self.get_field_value(instance))

def range_of(field_to_validate, min, max):
    '''validates that the values of the field are between min and max (note that this does
       not imply that the field is integer or numeric for that matter!)'''
    return FieldRangeValidation(field_to_validate, min, max)

def format_of(field_to_validate, regex):
    '''validates contents of the field against a given regex'''
    return FieldFormatValidation(field_to_validate, regex)

def presence_of(field_to_validate):
    '''validates that the field is not empty'''
    return FieldPresenceValidation(field_to_validate)

def uniqueness_of(field_to_validate):
    '''validates that the model doesn't contain another entry with the same field
       contents (like a unique index, but at the model level)'''
    return FieldUniquenessValidation(field_to_validate)

def numericality_of(field_to_validate, integer_only=False):
    '''validates that the model is a number (integer or float depending on the parameter)'''
    return FieldNumericality(field_to_validate, integer_only)

__all__=['ValidationException', 'Validator', 'range_of', 'format_of', 'presence_of', \
         'uniqueness_of', 'numericality_of']