#
# Copyright (c) 2009 PT. Ungaran Sari Garments. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#

__author__    = 'Jaimy Azle'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2009 PT. UNGARAN SARI GARMENTS'

import os
import shutil
import zipfile

class CreateBinApp(object):
  """
  Create Binary application for distribution
  NOTE: this script is run on Python 3.x
  """

  def __init__(self):
    pass

  def runApp(self):
    def_path = os.path.abspath('.')
    binapp_root = os.path.abspath('..\\binapp')
    serverapp_root = binapp_root + '\\bin'
    clientapp_root = binapp_root + '\\client'
    archive_file = '..\\binapp.zip'
    if not os.path.exists(binapp_root): os.makedirs(binapp_root)
    print("preparing files...")
    shutil.copytree('..\\bin', serverapp_root, ignore=shutil.ignore_patterns('.svn', 'config', 'readme.txt', 'licgen.*'))
    shutil.copytree('..\\client', clientapp_root, ignore=shutil.ignore_patterns('.svn', '*.po', '*.idx', '*.rpt', 'readme.txt','*.mvc', 'reports', 'welcome'))
    print("creating archive file: "+archive_file)
    if os.path.exists(archive_file):
      os.remove(archive_file)
    archive = zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED)
    os.chdir(binapp_root)
    tree = os.walk('./')
    for directory in tree:
      for file in directory[2]:
        file_to_add = directory[0]+'/'+file
        if os.path.exists(file_to_add):
          rel_file = os.path.relpath(file_to_add)
          archive.write(rel_file)
          print('adding '+rel_file)
          os.remove(file_to_add)
    archive.close()
    os.chdir(def_path)
    shutil.rmtree(binapp_root)
    print("Done!!! archive file could be found in "+archive_file)

binapp = CreateBinApp()
binapp.runApp()
