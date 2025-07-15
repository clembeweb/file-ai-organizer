
# File AI Organizer – GUI

Applicazione Windows con interfaccia grafica (Tkinter) per organizzare file.

## Avvio rapido (da sorgenti)
```powershell
cd src
python main.py
```

## Compilazione in EXE
Basta eseguire `build.bat` (richiede PyInstaller):
```powershell
build.bat
```
Al termine avrai `dist\FileAIOrganizer.exe` utilizzabile su qualsiasi PC Windows senza Python installato.

## Funzionalità
* Scansione di una cartella scelta.
* Individua duplicati, file temporanei, e propone spostamenti per estensione.
* Tabella di revisione con pulsante “Applica azioni”.
* Impostazioni di base per estensioni da eliminare e soglia giorni.
