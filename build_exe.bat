@echo off
REM PRJs runner | platform: windows | scope: repo-local
setlocal
title Build EXE - Audio Transcript
cd /d "%~dp0"

echo.
echo ========================================
echo   Building EXE: AudioTranscript
echo   Project     : Audio Transcript
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\tools\BuildExe\Build-One.ps1" -RepoFolder "%CD%" -EntryScript "main.py" -ExeName "AudioTranscript" -Console 
set ERR=%ERRORLEVEL%

echo.
if %ERR% NEQ 0 (
  echo BUILD FAILED
  pause
  exit /b %ERR%
)

echo.
echo EXE is in: "%CD%\dist\AudioTranscript.exe"
explorer "%CD%\dist"
pause
endlocal
