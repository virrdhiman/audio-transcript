@echo off
setlocal
title Build EXE - Transcript Maker
cd /d "%~dp0"

echo.
echo ========================================
echo   Building EXE: TranscriptMaker
echo   Project     : Transcript Maker
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\..\..\tools\BuildExe\Build-One.ps1" -RepoFolder "%CD%" -EntryScript "transcribe.py" -ExeName "TranscriptMaker" -Console 
set ERR=%ERRORLEVEL%

echo.
if %ERR% NEQ 0 (
  echo BUILD FAILED
  pause
  exit /b %ERR%
)

echo.
echo EXE is in: "%CD%\dist\TranscriptMaker.exe"
explorer "%CD%\dist"
pause
endlocal
