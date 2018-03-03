from decimal import *
import sys
import types

CurrencyContext = Context(
        prec=32, rounding=ROUND_HALF_EVEN,
        traps=[DivisionByZero, Overflow, InvalidOperation, Clamped, Underflow],
        flags=[],
        Emax=9999999999999999999999999999999,
        Emin=-9999999999999999999999999999999,
)

DigitScaleTwo = Decimal(10) ** -2
DigitScaleThree = Decimal(10) ** -3

def _decimalToCurrencyString(value):
  global CurrencyContext
  return value.__str__(context=CurrencyContext)

def _currencyStringToDecimal(value):
  global CurrencyContext
  return Decimal(value, context=CurrencyContext)

def decimalToCurrencyString(value):
  return _decimalToCurrencyString(value)

def currencyStringToDecimal(value):
  return _currencyStringToDecimal(value)

def extractIntDate(adt):
  day = adt % 100
  res = adt / 100
  mon = res % 100
  yr  = res / 100
  return (day, mon, yr)

def get_refcounts():
    d = {}
    sys.modules
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = map (lambda x: (x[1],x[0]), d.items())
    pairs.sort()
    pairs.reverse()
    return pairs

def print_top_100():
    lst = get_refcounts()
    print 'there are %d objects, top 100 list:' % len(lst)
    for n, c in lst[:100]:
        print '%10d %s' % (n, c.__name__)
