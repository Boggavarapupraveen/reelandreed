@echo off
REM Portable Windows launcher. Uses .vendor when present, otherwise the active
REM Python environment. For a standard install: streamlit run app.py
setlocal
set MPLCONFIGDIR=%~dp0.cache\matplotlib
set HF_HOME=%~dp0.cache\huggingface
set TMP=%~dp0.cache\tmp
set TEMP=%~dp0.cache\tmp
if exist "%~dp0.vendor" (
    set PYTHONPATH=%~dp0.vendor;%~dp0
)
python -m streamlit run "%~dp0app.py" --global.developmentMode false %*
endlocal
