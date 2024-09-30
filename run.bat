:: Derived from https://github.com/oobabooga/text-generation-webui/blob/main/start_windows.bat

@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo This script relies on Miniconda which can not be silently installed under a path with spaces. && goto end

@rem Check for special characters in installation path
set "SPCHARMESSAGE="WARNING: Special characters were detected in the installation path!" "         This can cause the installation to fail!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
	call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

@rem fix failed install when installing to a separate drive
set TMP=%cd%\installer_files
set TEMP=%cd%\installer_files

@rem deactivate existing conda envs as needed to avoid conflicts
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set INSTALL_DIR=%cd%\installer_files
set CONDA_ROOT_PREFIX=%cd%\installer_files\conda
set INSTALL_ENV_DIR=%cd%\installer_files\env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe
set conda_exists=F

@rem figure out whether git and conda needs to be installed
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

@rem (if necessary) install git and conda into a contained environment
@rem download conda
if "%conda_exists%" == "F" (
	echo Downloading Miniconda from %MINICONDA_DOWNLOAD_URL% to %INSTALL_DIR%\miniconda_installer.exe

	mkdir "%INSTALL_DIR%"
	call curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo Miniconda failed to download. && goto end )

	echo Installing Miniconda to %CONDA_ROOT_PREFIX%
	start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%

	@rem test the conda binary
	echo Miniconda version:
	call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo Miniconda not found. && goto end )
)

@rem create the installer env
if not exist "%INSTALL_ENV_DIR%" (
	echo Packages to install: %PACKAGES_TO_INSTALL%
	call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.10 || ( echo. && echo Conda environment creation failed. && goto end )
)

@rem check if conda environment was actually created
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Conda environment is empty. && goto end )

@rem environment isolation
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem activate installer env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Miniconda hook not found. && goto end )
echo "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%"
echo Virtual environment activated.

:: Path to the expected installation directory of the Build Tools
set VSBUILDTOOLS_DIR=%cd%\BuildTools

echo checking C++ Build Tools.
:: Check if the Build Tools are installed
if exist "%VSBUILDTOOLS_DIR%\VC\Auxiliary\Build\vcvars64.bat" (
    echo Visual Studio Build Tools are already installed.
    goto :SkipCPPInstallation
)

:: Path to the Visual Studio Build Tools bootstrapper file
set BOOTSTRAPPER_PATH=vs_buildtools.exe

echo installing C++ Build Tools, this should take a minute...
:: Run the bootstrapper with arguments to install C++ build tools
"%BOOTSTRAPPER_PATH%" --quiet --wait --norestart --nocache ^
    --installPath "%VSBUILDTOOLS_DIR%" ^
    --add Microsoft.VisualStudio.Workload.VCTools ^
    --includeRecommended

echo C++ Build Tools installed successfully.

:SkipCPPInstallation

:: Check if long path support is already enabled
reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo LongPathsEnabled registry key not found, enabling long path support...
	:: Check if script is running as administrator
	net session >nul 2>&1
	if %ERRORLEVEL% neq 0 (
		echo Need administrative privileges to enable long path support...
		powershell -Command "Start-Process '%~f0' -Verb RunAs"
		exit /b
	)
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" /t REG_DWORD /d 1 /f
    if %ERRORLEVEL% equ 0 (
        echo Long path support has been successfully enabled.
    ) else (
        call :PrintBigMessage "ERROR: Failed to enable long path support. Please run this script as administrator."
    )
) else (
    for /f "tokens=3" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" 2^>nul') do set LongPathsEnabled=%%A
    if "%LongPathsEnabled%"=="0x1" (
        echo Long path support is already enabled.
    ) else (
        echo Long path support is disabled. Enabling it now...
		:: Check if script is running as administrator
		net session >nul 2>&1
		if %ERRORLEVEL% neq 0 (
			echo Need administrative privileges to enable long path support...
			powershell -Command "Start-Process '%~f0' -Verb RunAs"
			exit /b
		)
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" /t REG_DWORD /d 1 /f
        if %ERRORLEVEL% equ 0 (
            echo Long path support has been successfully enabled.
        ) else (
            call :PrintBigMessage "ERROR: Failed to enable long path support. Please run this script as administrator."
        )
    )
)


echo Installing dependencies...
CALL python -m pip install pip==24.0
CALL python -m pip install -r requirements.txt
CALL python -m pip install llama-cpp-python==0.3.0
CALL python -m pip install torch torchaudio

:: Workaround for llama-cpp-python loading paths in CUDA env vars even if they do not exist
set "conda_path_bin=%INSTALL_ENV_DIR%\bin"
if not exist "%conda_path_bin%" (
    :: Create the directory if it does not exist
    mkdir "%conda_path_bin%"
)

:startmain
echo Starting main.py...
python main.py

@rem below are functions for the script   next line skips these during normal execution
goto end

:PrintBigMessage
echo. && echo.
echo *******************************************************************
for %%M in (%*) do echo * %%~M
echo *******************************************************************
echo. && echo.
pause


:end
pause
