@echo off
setlocal
cd /d "%~dp0.."
git status -sb
set /p DOCOMMIT=Commit? (Y/n): 
if /i not "%DOCOMMIT%"=="n" (
  git add -A
  git reset HEAD -- .env .env.* 2>nul
  git reset HEAD -- scripts/strip-* 2>nul
  set /p MSG=Commit message: 
  if not "%MSG%"=="" git commit -m "%MSG%"
)
set /p DOPUSH=Push? (Y/n): 
if /i not "%DOPUSH%"=="n" git push origin HEAD
pause
