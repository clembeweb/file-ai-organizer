
@echo off
REM Costruisce l'eseguibile standalone con PyInstaller
pip install --upgrade pip
pip install pyinstaller
pip install -r requirements.txt
cd src
pyinstaller --onefile --noconsole --name "FileAIOrganizer" main.py
echo Build completata. Troverai l'eseguibile in dist\FileAIOrganizer.exe
pause
