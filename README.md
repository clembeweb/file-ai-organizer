
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
* Estrazione testo da immagini (OCR) per analisi del contenuto dei file.
* Raggruppamento intelligente dei file basato sul contenuto (clustering semantico tramite modelli AI locali).
* Suggerimento di rinominazione file in base al testo estratto (rinomina intelligente).

## Requisiti aggiuntivi
* Installare **Tesseract OCR** e assicurarsi che sia nel PATH di sistema.
* Al primo utilizzo verrà scaricato il modello `sentence-transformers/all-MiniLM-L6-v2` (richiede connessione Internet).
* Tutte le librerie necessarie sono elencate in `requirements.txt`.
