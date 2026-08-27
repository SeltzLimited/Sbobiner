# Guida rapida — uso senza terminale

## Cosa c'è da scaricare

**Niente.** Il programma è già sul tuo Mac, nella cartella:

```
~/Documents/trascrizione-offline
```

Anche i modelli (Whisper + riconoscimento voci, ~1,5 GB) sono già scaricati.
Da qui in poi funziona **offline**.

Per spostarlo su un altro Mac: copia l'intera cartella e ripeti l'installazione qui sotto
su quel Mac (i modelli si riscaricano).

---

## Installazione (una volta sola)

1. Apri la cartella `trascrizione-offline` nel Finder.
2. Doppio click su **`setup.command`**.
3. Si apre una finestra nera (Terminale): parte da sola, aspetta che scriva
   **"Puoi chiudere questa finestra"**, poi premi Invio e chiudila.

> **Primo avvio bloccato da macOS?**
> Se compare *"impossibile aprire perché proviene da uno sviluppatore non identificato"*:
> tasto destro sul file → **Apri** → **Apri**. Va fatto una volta sola, sia per
> `setup.command` sia per `start.command`.

Se non hai fatto il setup una prima volta serve internet (scarica i modelli).
Dopo, mai più.

---

## Uso di tutti i giorni

1. Doppio click su **`start.command`**.
2. Si apre da solo il browser su `http://127.0.0.1:5000`.
   (se non si apre, apri tu il browser e scrivi quell'indirizzo)
3. **Trascina il file audio o video** dentro il riquadro tratteggiato.
   Vanno bene mp3, wav, m4a, aac, ogg, e anche video mp4/mkv/mov.
4. Scegli le opzioni:
   - **Lingua**: Italiano (o "Rileva automaticamente" se non sai)
   - **Tipo**: *Lezione* o *Riunione*
   - **Riconosci chi parla**: *Sì* se parlano più persone, *No* se è una voce sola (più veloce)
   - **Contesto**: *Aula* (tante persone) o *Riunione* (poche) — conta solo se hai messo "Sì" sopra
   - **N. persone**: lascialo vuoto, oppure scrivi il numero se lo sai (aiuta il riconoscimento)
5. Premi **Trascrivi**. Compare l'avanzamento ("Trascrizione…", "Post-elaborazione…").
   Un'ora di audio richiede grosso modo 5 minuti.
6. A fine lavoro compaiono i pulsanti di download:
   - **.txt** — testo semplice
   - **.srt** / **.vtt** — sottotitoli con tempi
   - **.docx** — Word formattato (titoli per sezione; in modalità *Riunione* anche
     tabella action item e decisioni)

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
| Il browser non si apre | Aprilo a mano su `http://127.0.0.1:5000` |
| "sviluppatore non identificato" | Tasto destro sul `.command` → **Apri** → **Apri** |
| `start.command` dà errore "no such file .venv" | Non hai fatto il setup: doppio click su `setup.command` |
| Trascrizione lentissima / Mac che arranca | In `config.yaml`, `model: name:` → prova `large-v3-turbo-q4`, poi `medium` |
| La finestra nera si chiude subito | Aprila da sola: tasto destro → Apri; leggi l'errore mostrato |
