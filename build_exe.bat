@echo off
setlocal
cd /d "%~dp0"

echo Installing / updating dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo Building AudioTranscript.exe ...
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --name AudioTranscript ^
  --collect-all faster_whisper ^
  --collect-all ctranslate2 ^
  --hidden-import faster_whisper ^
  --hidden-import ctranslate2 ^
  --hidden-import docx ^
  main.py

if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo.
echo Done: dist\AudioTranscript.exe
endlocal
