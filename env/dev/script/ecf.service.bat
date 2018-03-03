@echo off
::
:: Service management
::

@for /f "delims=" %%a in ('@cd') do (set CURR_PATH=%%a)

@if /I "%1"=="-h" (goto :HELP & goto :EOF)
@if /I "%1"=="/h" (goto :HELP & goto :EOF)
@if /I "%1"=="-?" (goto :HELP & goto :EOF)
@if /I "%1"=="/?" (goto :HELP & goto :EOF)
@@if /I "%1"=="/i" (goto :INSTALL_SVC & goto :EOF)
@@if /I "%1"=="-i" (goto :INSTALL_SVC & goto :EOF)
@@if /I "%1"=="/u" (goto :UNINSTALL_SVC & goto :EOF)
@@if /I "%1"=="-u" (goto :UNINSTALL_SVC & goto :EOF)


@goto :HELP

:INSTALL_SVC
cd "%CURR_PATH%"\..\..\..\bin
"%CURR_PATH%"\..\..\..\bin\ecfsrv -install -silent "-conf:%CURR_PATH%\..\conf\ecfserver.properties"
"%CURR_PATH%"\..\..\..\bin\ecfguard -install -silent
cd "%CURR_PATH%"
@goto :END

:UNINSTALL_SVC
cd "%CURR_PATH%"\..\..\..\bin
"%CURR_PATH%"\..\..\..\bin\ecfguard -uninstall -silent
"%CURR_PATH%"\..\..\..\bin\ecfsrv -uninstall -silent "-conf:%CURR_PATH%\..\conf\ecfserver.properties"
cd "%CURR_PATH%"
@goto :END

::===========
:HELP
@echo   ecf.service version 1.0
@echo.
@echo   Syntax:
@echo     ecf.service option
@echo.
@echo   option list:
@echo     -i   = install service
@echo     -u   = uninstall service
@echo.
@goto :END

:: ========= END General SECTION =========

:END
