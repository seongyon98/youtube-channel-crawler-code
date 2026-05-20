@echo off
setlocal
pushd "%~dp0"

:: 1. Force UTF-8 Mode for this session
chcp 65001 >nul

:: 2. Failsafe: Force switch to feature/openai-filter branch before running
git checkout feature/openai-filter >nul 2>&1
git pull --rebase origin feature/openai-filter >nul 2>&1

:: 3. Launch PowerShell with explicit script path and working directory
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_and_sync.ps1"

popd
pause
