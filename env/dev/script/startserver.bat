@echo off
::
:: app management
::

@for /f "delims=" %%a in ('@cd') do (set CURR_PATH=%%a)
cd "%CURR_PATH%"\..\..\..\bin
"%CURR_PATH%"\..\..\..\bin\ecfsrv "-conf:%CURR_PATH%\..\conf\ecfserver.properties"
cd "%CURR_PATH%"
@goto :END

:END
