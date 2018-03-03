from _ecfprops import *

class configmanager(object):
  def __init__(self, ECFProps):
    self.__ECFProps__ = ECFProps

  def __getattr__(self, key):
    return self.__dict__['__ECFProps__'].Value[key]

  def __setattr__(self, key, value):
    if key == "__ECFProps__":
      self.__dict__['__ECFProps__'] = value
    else:
      self.__ECFProps__.Value[key] = value
      self.__ECFProps__.Value = Self.__ECFProps__.Value

  def __repr__(self):
    return str(self.__ECFProps__.Value)

  def __str__(self):
    return str(self.__ECFProps__.Value)

  def get(self, key, default=None):
    return self.__ECFProps__.get(key, default)

  def __setitem__(self, key, value):
    self.__ECFProps__.Value[key] = value

  def __getitem__(self, key):
    return self.__ECFProps__.Value[key]

config = configmanager(ServerProperties)

