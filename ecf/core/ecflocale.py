from sqlalchemy import *
import elixir as el
import ecfpool as pool
from jitutil import *

@nativeclass
class ECFLocale(object):

  def __init__(self):
    self.def_locale = "en"
    self.active_locale = "en"
    self.pool = pool.getCachePool()
    self.def_dict = {}
    self.enable_locale = True
    self.pool.setLOCALEDict(self.def_locale, self.def_dict)
    self.act_dict = self.pool.getLOCALEDict(self.active_locale)

  def get_default_locale(self):
    return self.def_locale

  def set_default_locale(self, locale):
    self.pool.setLOCALEDict(self.def_locale, self.def_dict)
    self.def_locale = locale
    self.def_dict = self.pool.getLOCALEDict(self.def_locale)
    if self.def_dict is None:
      self.def_dict = {}
      self.pool.setLOCALEDict(self.def_locale, self.def_dict)

  def get_active_locale(self):
    return self.active_locale

  def set_active_locale(self, locale):
    self.pool.setLOCALEDict(self.active_locale, self.act_dict)
    self.active_locale = locale
    self.act_dict = self.pool.getLOCALEDict(self.active_locale)
    if self.act_dict is None:
      self.act_dict = {}
      self.pool.setLOCALEDict(self.active_locale, self.act_dict)

  def read_locale_data(self, locale, mod):
    from tbl import EFLOCL
    ret = {}
    query = EFLOCL.query.filter_by(EFLCLCCD = locale.upper())
    objs = query.filter_by(EFLCMDCD = mod).all()
    if objs:
      for obj in objs:
        ret[obj.EFLCMSID] = obj.EFLCMSLS
    return ret

  def update_translation(self, mod_dict, locale, mod, msg):
    from tbl import EFLOCL
    obj = EFLOCL.get((locale.upper(), mod, msg))
    if obj:
      mod_dict[msg] = obj.EFLCMSLS
    return mod_dict


  def get_def_locale_mod(self, locale, mod):
    if self.def_dict.has_key(mod):
      return self.def_dict[mod]
    else:
      aret = self.read_locale_data(locale, mod)
      self.def_dict[mod] = aret
      return aret

  def get_act_locale_mod(self, locale, mod):
    if self.act_dict.has_key(mod):
      return self.act_dict[mod]
    else:
      aret = self.read_locale_data(locale, mod)
      self.act_dict[mod] = aret
      return aret

  def get_def_translation(self, locale, mod, msg):
    mod_dict = self.get_def_locale_mod(locale, mod)
    if mod_dict.has_key(msg):
      return mod_dict[msg]
    else:
      self.update_translation(mod_dict, locale, mod, msg)
      if mod_dict.has_key(msg):
        return mod_dict[msg]
      else:
        return msg

  def get_act_translation(self, locale, mod, msg):
    # print '"%s","%s","%s"' % (locale, mod, msg)
    if self.enable_locale:
      if (self.active_locale != self.def_locale):
        mod_dict = self.get_act_locale_mod(locale, mod)
        if mod_dict.has_key(msg):
          return mod_dict[msg]
        else:
          self.update_translation(mod_dict, locale, mod, msg)
          if mod_dict.has_key(msg):
            return mod_dict[msg]
          else:
            return self.get_def_translation(locale, mod, msg)
      else:
        return self.get_def_translation(locale, mod, msg)
    else:
      return msg

  def translate(self, mod, msg):
    return self.get_act_translation(self.active_locale, mod, msg)

  def translate_list(self, mod, msg):
    try:
      arslt = []
      for amsg in msg:
        arslt.append(self.get_act_translation(self.active_locale, mod, amsg))
    finally:
      el.session.close()
    return arslt

locale = ECFLocale()


