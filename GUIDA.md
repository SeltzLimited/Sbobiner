# Sbobiner — guida rapida (uso senza terminale)

## Cosa c'è da scaricare

**Niente.** Il programma è già sul tuo Mac, nella cartella:

```
~/Documents/Sbobiner
```

Anche i modelli (Whisper + riconoscimento voci, ~500 MB) sono già scaricati.
Da qui in poi funziona **offline**.

Per spostarlo su un altro Mac: copia l'intera cartella e ripeti l'installazione qui sotto
su quel Mac (i modelli si riscaricano).

---

## Installazione

1. Apri la cartella `Sbobiner` nel Finder.
2. Doppio click su **`setup.command`**.
3. Si apre una finestra del Terminale, aspetta che scriva
   **"Puoi chiudere questa finestra"**, poi premi Invio e chiudila.

Al primo setup serve internet per scaricare i modelli.
Dopo, mai più.

---

## Uso di tutti i giorni

1. Doppio click su **`start.command`**.
2. Si apre da solo il browser su `http://127.0.0.1:5000`.
3. **Trascina il file audio o video** dentro il riquadro tratteggiato.
   Vanno bene mp3, wav, m4a, aac, ogg, e anche video mp4/mkv/mov.
4. Scegli le opzioni:
   - **Lingua**: Italiano (o "Rileva automaticamente")
   - **Tipo**: *Lezione* o *Riunione*
   - **Riconosci chi parla**: *Sì* se parlano più persone, *No* se è una voce sola
   - **Contesto**: *Aula* (tante persone) o *Riunione* (poche) — conta solo se hai messo "Sì" sopra
   - **N. persone**: lascialo vuoto, oppure scrivi il numero se lo sai (aiuta il riconoscimento)
5. Premi **Trascrivi**.
   Un'ora di audio richiede grosso modo 5 minuti (variabile).
6. A fine lavoro compaiono i pulsanti di download:
   - **.txt** — testo semplice
   - **.srt** / **.vtt** — sottotitoli con tempi
   - **.docx** — Word formattato

Puoi trascrivere un file dopo l'altro senza chiudere niente.

**Per fermare il programma**: chiudi la finestra nera del Terminale.

---

## Se una parola esce sempre sbagliata

Apri **`config.yaml`** (con TextEdit va bene) e aggiungi il termine giusto sotto
`glossary`, oppure la coppia sbagliato → giusto sotto `corrections`. Salva.
Vale dalla trascrizione successiva. Non serve reinstallare.

---

## Problemi comuni

| Sintomo | Cosa fare |
|---|---|
| `start.command` dà errore "no such file .venv" | Non hai fatto il setup: doppio click su `setup.command` |
| Trascrizione lentissima / Mac che arranca | In `config.yaml`, `model: name:` → prova `large-v3-turbo-q4`, poi `medium` |
