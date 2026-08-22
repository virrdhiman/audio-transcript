@echo off
REM PRJs runner | platform: windows | scope: repo-local
setlocal
cd /d "%~dp0.."
git status -sb
git log -3 --oneline
pause
