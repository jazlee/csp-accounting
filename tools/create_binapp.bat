@echo off
attrib ..\binapp\*.* -R /s
del ..\binapp\* /s /q
rmdir ..\binapp /s /q
python .\create_binapp.py