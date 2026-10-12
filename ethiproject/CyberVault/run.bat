@echo off
title BookNest — College Used-Book Marketplace
echo ================================================================
echo   Launching BookNest — College Used-Book Marketplace
echo   Running locally on: http://127.0.0.1:5000
echo ================================================================
py -m pip install -r requirements.txt
py app.py
pause
