import tools
import ecfdbcon
import services, tbl, api, mvc, job, bo
from jitutil import *

#----------------------------------------------------------
# init ecf.core service
#----------------------------------------------------------

job_enabled = tools.config['ecfserver.job.enabled']

import ecflocale
ecflocale.locale.set_default_locale(tools.config['system.systemlanguage'])
ecflocale.locale.set_active_locale(tools.config['system.activelanguage'])
if tools.config['system.enablelocale'].upper() == 'TRUE':
  ecflocale.locale.enable_locale = True
else:
  ecflocale.locale.enable_locale = False

tbl.registerClasses()
ecfdbcon.configure()

import ecflocale as ecf
import elixir as elx
for entity in elx.entities:
  for field in entity._descriptor.builders:
    if (field.tlabel) and (field.tlabel == field.label):
      field.tlabel = ecf.locale.translate(entity._descriptor.tablename, \
                      field.label)

bo.registerClasses()
mvc.registerClasses()
api.registerClasses()

if job_enabled.upper() == 'TRUE':
  job.registerClasses()

import ecfcmn
import init
init.doInitProc()


