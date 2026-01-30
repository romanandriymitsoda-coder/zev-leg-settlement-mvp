@echo off
setlocal
REM Run the ZEV/LEG MVP end-to-end on Windows.
REM Creates .venv if missing, installs requirements, and runs the main script.

pushd %~dp0

if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
)

call ".venv\Scripts\activate.bat"

pip install -r requirements.txt

python scripts\run_mvp.py

REM Copy latest figures to docs/ for GitHub visibility
if not exist docs (
    mkdir docs
)
copy /Y outputs\graph1_bill_change.png docs\graph1_bill_change.png >nul
copy /Y outputs\graph2_fairness_frontier.png docs\graph2_fairness_frontier.png >nul

popd
endlocal
