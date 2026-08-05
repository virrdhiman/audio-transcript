@echo off
setlocal
cd /d "%~dp0.."
git status -sb
git log -3 --oneline
pause
