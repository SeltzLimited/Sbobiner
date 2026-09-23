# Sbobiner — guida rapida (uso senza terminale)

Funziona su **Mac con Apple Silicon** e su **Windows 10 / 11** (64 bit).

---

## Mac

### Cosa c'è da scaricare

1. Dalla pagina GitHub del progetto: **Code → Download ZIP**.
2. Doppio click sullo ZIP per estrarlo e sposta la cartella dove preferisci
   (per esempio in `Documenti`).

### Installazione

1. Apri la cartella nel Finder e fai doppio click su **`setup.command`**.
2. Se macOS lo blocca (*"sviluppatore non identificato"* o *"Apple non può verificare…"*):
   apri **Impostazioni di Sistema → Privacy e sicurezza**, scorri in basso e clicca
   **Apri comunque**, poi rifai doppio click. Serve una volta sola, anche per `start.command`.
3. Si apre una finestra del Terminale: aspetta che scriva
   **"Puoi chiudere questa finestra"**, poi premi Invio e chiudila.

Serve internet solo adesso (scarica ~500 MB di modelli). Dopo funziona **offline**.

Per spostarlo su un altro Mac: copia l'intera cartella e rifai l'installazione su quel Mac.

### Uso

Doppio click su **`start.command`**: si apre da solo il browser su `http://127.0.0.1:5000`.
Poi segui [Come si usa](#come-si-usa).

**Per fermare il programma**: chiudi la finestra del Terminale.

---

## Windows

### Cosa c'è da scaricare

1. Dalla pagina GitHub del progetto: **Code → Download ZIP**.
2. Tasto destro sullo ZIP → **Estrai tutto…** in una cartella, per esempio `C:\Sbobiner`.

> Meglio un percorso **senza lettere accentate** (`C:\Sbobiner` va benissimo).

### Installazione

1. Apri la cartella e fai doppio click su **`setup.bat`**.
2. Se compare **"Windows ha protetto il PC"**: clicca **Ulteriori informazioni** →
   **Esegui comunque**. Succede con i file scaricati da internet.
3. Se Python manca, il setup propone di installarlo: premi **S**. Alla fine
   **chiudi la finestra e rifai doppio click su `setup.bat`**.
4. Aspetta che scriva **"Pronto"**, poi premi un tasto per chiudere.

Serve internet solo adesso (scarica ~1,6 GB di modello). Dopo funziona **offline**.

### Uso

Doppio click su **`start.bat`**: si apre una **finestra di Edge dedicata a Sbobiner**
(o di Chrome, se Edge non c'è). Poi segui [Come si usa](#come-si-usa).

La **finestra nera** deve restare aperta mentre usi Sbobiner.
**Per fermare il programma**: chiudi la finestra nera.

Consiglio: tasto destro su `start.bat` → **Mostra altre opzioni → Crea collegamento**
e sposta il collegamento sul Desktop.

---

## Come si usa

1. **Trascina il file audio o video** dentro il riquadro tratteggiato
   (oppure cliccaci sopra per sceglierlo).
   Vanno bene mp3, wav, m4a, aac, ogg, e anche video mp4/mkv/mov.
2. Scegli le opzioni:
   - **Lingua**: Italiano (o "Rileva automaticamente")
   - **Tipo**: *Lezione* o *Riunione*
   - **Riconosci chi parla**: spuntalo solo se parlano più persone (è più lento).
     Compaiono allora **Contesto** (*Aula* = tante persone, *Riunione* = poche) e
     **N. persone** (lascialo vuoto, o scrivi il numero se lo sai).
3. Premi **Trascrivi** e guarda la barra di avanzamento.
   - Mac: un'ora di audio richiede grosso modo 5 minuti.
   - Windows: circa 20-25 minuti per un'ora di audio su un PC recente, fino a un'ora su quelli datati.
4. A fine lavoro compaiono i pulsanti di download:
   - **.txt** — testo semplice
   - **.srt** / **.vtt** — sottotitoli con tempi
   - **.docx** — Word formattato

Puoi trascrivere un file dopo l'altro senza chiudere niente.

---

## Se una parola esce sempre sbagliata

Apri **`config.yaml`** (con TextEdit sul Mac, con il Blocco note su Windows) e aggiungi
il termine giusto sotto `glossary`, oppure la coppia sbagliato → giusto sotto `corrections`.
Salva. Vale dalla trascrizione successiva: basta chiudere e riaprire Sbobiner.

---

## Problemi comuni

| Sintomo | Cosa fare |
|---|---|
| Mac: "sviluppatore non identificato" / "Apple non può verificare…" | **Impostazioni di Sistema → Privacy e sicurezza → Apri comunque** |
| Mac: `start.command` dà errore "no such file .venv" | Non hai fatto il setup: doppio click su `setup.command` |
| Windows: "Sbobiner non e' ancora installato" | Doppio click su `setup.bat` |
| Windows: "Windows ha protetto il PC" | **Ulteriori informazioni → Esegui comunque** |
| Windows: "Manca il runtime Microsoft Visual C++" | Rispondi **S**, oppure installalo da https://aka.ms/vs/17/release/vc_redist.x64.exe |
| Windows: la trascrizione non parte e la cartella ha lettere accentate nel percorso | Sposta la cartella in `C:\Sbobiner` e rifai il setup |
| Trascrizione troppo lenta | In `config.yaml`, `model: name:` → prova `small` (più veloce, un po' meno preciso), poi riesegui il setup |
