# Sbobiner

*🇬🇧 [English version below](#english).*

> Sempre più difficile trascrivere un audio. Tutti i servizi sono a pagamento o funzionano male.
> Questo non sarà perfetto, ma fa il suo. E il file resta sul tuo pc.
> Fatto per MAC perché è quello che uso al momento. Liberi di contribuire.
>
> Installi una sola volta. Carichi il file. Trascrivi (nel frattempo fai altro). Salvi la trascrizione. Fine.
> N.B.: Non puoi trascrivere un concerto.

<p align="center">
  <img src="static/SBOB.png" alt="Interfaccia di Sbobiner" width="620">
</p>

<p align="center">
  <a href="https://ko-fi.com/E7D425WCX9"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Offrimi un caffè su Ko-fi"></a>
</p>
<p align="center">
"If it works, I'm a genius. If it doesn't, it's the AI's fault."
</p>

Funziona su **Mac con Apple Silicon** e su **Windows 10 / 11** (64 bit).

Pipeline di trascrizione per **lezioni e riunioni**, costruita su Whisper.
Gira interamente **offline** dopo il setup iniziale. Nessun account, nessun token.

Motore: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples/tree/main/whisper) su Mac (GPU),
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) su Windows (CPU).
Diarization: [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (modelli liberi, senza gating).

---

## Setup iniziale (solo la prima volta, serve internet)

**Mac** — scarica lo ZIP (**Code → Download ZIP**), estrailo e fai doppio click su **`setup.command`**.
- Se macOS lo blocca: **Impostazioni di Sistema → Privacy e sicurezza → Apri comunque**
  (una volta sola, anche per `start.command`).
- Scarica ~460 MB per Whisper + ~35 MB per la diarization. Ingombro totale **~1,1 GB**.

**Windows** — scarica lo ZIP (**Code → Download ZIP**), estrailo (es. in `C:\Sbobiner`,
meglio un percorso senza lettere accentate) e fai doppio click su **`setup.bat`**.
- Se compare *"Windows ha protetto il PC"*: **Ulteriori informazioni → Esegui comunque**.
- Se Python manca, il setup propone di installarlo (winget): poi chiudi e riapri `setup.bat`.
- Scarica ~1,6 GB di modello. Ingombro totale **~2 GB**, tutto dentro la cartella del
  programma: cancellandola disinstalli tutto.

Il setup crea l'ambiente virtuale, installa le dipendenze e scarica i modelli.
`ffmpeg` è incluso, non va installato.

## Uso quotidiano (Offline)

**Mac** — doppio click su **`start.command`** dal Finder: si apre il browser su `http://127.0.0.1:5000`.

**Windows** — doppio click su **`start.bat`**: si apre una **finestra dedicata di Edge**
(o di Chrome, se Edge manca), senza schede né barra degli indirizzi.

Trascina il file, scegli le opzioni, premi **Trascrivi**.
A fine elaborazione scarichi in **TXT**, **SRT**, **VTT** o **DOCX**.

Formati in ingresso: qualsiasi cosa `ffmpeg` sappia leggere (mp3, wav, m4a, aac, ogg, flac,
e anche video mp4/mkv/mov — l'audio viene estratto in automatico).

N.B. la finestra del terminale (la finestra nera su Windows) deve rimanere aperta per permettere
a Sbobiner di funzionare nella pagina web.

---

## Configurazione — `config.yaml`

Tutto si può regolare da lì, senza toccare il codice.

### Cambiare lingua

```yaml
language: it        # italiano (default)
```

- Cambio lingua tramite codice ISO 639-1 (`en`, `fr`, `de`, `es`, `pt`, ...).
- `auto`: Whisper rileva la lingua da solo (più lento, meno preciso).

### Modello Whisper

```yaml
model:
  name: large-v3-turbo-q4
```

| Valore | Peso | Note |
|---|---|---|
| `large-v3-turbo-q4` | ~460 MB | **default**. turbo quantizzato a 4 bit: leggero, qualità vicina al turbo pieno. |
| `large-v3-turbo` | ~1.5 GB | un filo più preciso, occupa 3× lo spazio. |
| `medium` | ~1.5 GB | fallback. |
| `small` | ~500 MB | ~2× più veloce, meno preciso. |
| `large-v3` | ~3 GB | massima precisione, consigliato con 16 GB+ di RAM. |

Dopo aver cambiato `name`, rifai il setup (`setup.command` / `setup.bat`) per scaricarlo:
alla fine propone di eliminare il modello vecchio e recuperare spazio.

Perché il turbo (e non `large-v3`): è `large-v3` distillato (8 layer di decoder invece di 32),
precisione in trascrizione quasi identica ma molto più veloce. La variante `-q4` dimezza
ancora il peso su disco con una perdita di qualità minima; la velocità resta simile.

Su **Windows** i pesi indicati sono quelli del Mac: lì non esiste il 4 bit, quindi
`large-v3-turbo-q4` e `large-v3-turbo` sono lo stesso modello (~1,6 GB, quantizzato int8 al caricamento).

### Glossario e correzioni

```yaml
glossary:            # iniettati come bias: aiutano su nomi propri e termini tecnici
  - Kubernetes
  - "Rossi"          # cognomi ricorrenti del corso/team
corrections:         # sostituzione esatta a valle, se un termine esce comunque sbagliato
  "cuber netes": Kubernetes
```

### Diarization (chi parla) per contesto

```yaml
diarization:
  preset: riunione   # oppure: aula
  aula:      { num_speakers: null, cluster_threshold: 0.70 }
  riunione:  { num_speakers: null, cluster_threshold: 0.50 }
```

- `aula`: molte persone, soglia più alta (raggruppa di più, evita di inventare voci).
- `riunione`: poche persone, soglia più bassa (separa meglio 2–6 parlanti).
- Se sai quante persone parlano, imposta `num_speakers` (es. `3`) o usa il campo
  **N. persone** nella pagina web: la diarization diventa più stabile.

### Post-elaborazione lezioni/riunioni

In `config.yaml` → `postprocess`: lista di intercalari da togliere, soglia di pausa per
i cambi di sezione, frasi-chiave per sezioni / action item / decisioni. Tutte modificabili.

> Sezioni e action item sono **euristici** (pause + frasi-trigger), non ML.
> Se un domani la precisione non basta, il punto di aggancio per un passaggio LLM locale
> è in `postprocess.py` (`_split_sections` / `_extract`), segnato con un commento `ponytail:`.

---

## Struttura

| File | Responsabilità |
|---|---|
| `audio.py` | normalizzazione di qualsiasi input → wav 16 kHz mono |
| `transcribe.py` | motore Whisper + iniezione glossario |
| `diarize.py` | riconoscimento di chi parla (sherpa-onnx), preset per contesto |
| `merge.py` | allineamento testo ↔ speaker |
| `postprocess.py` | pulizia, sezioni, action item, decisioni |
| `export.py` | TXT / SRT / VTT / DOCX |
| `app.py` + `templates/index.html` | server locale e pagina web |
| `config.yaml` | tutta la configurazione |
| `download_models.py` | scarica i modelli una volta |
| `setup.command` / `setup.bat` | installazione (Mac / Windows) |
| `start.command` / `start.bat` | avvio quotidiano (Mac / Windows) |
| `test_pipeline.py` | self-check: `python test_pipeline.py` |

## Note

- Velocità misurata su Mac 8 GB con `large-v3-turbo-q4`
  (38 min di audio → ~3,5 min di trascrizione). Senza diarization.
- Su Windows la trascrizione gira sul processore: circa 20-25 minuti per un'ora di audio
  su un PC recente, fino a un'ora su processori datati. Per andare più veloci: `model.name: small`.
- Tutto resta in locale, nella cartella `work/`. Contiene anche il
  `.wav` intermedio (~2 MB/min): svuotala quando vuoi.

## Crediti

Sviluppato con [Claude](https://claude.ai) (Claude Code) usando il plugin
**[ponytail](https://github.com/DietrichGebert/ponytail)** in modalità `ultra`, che spinge
verso la soluzione più semplice che funziona: libreria standard e funzionalità native
prima di aggiungere dipendenze o codice custom.

Componenti di terze parti: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples)
(MIT) · [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (MIT) ·
[`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (Apache-2.0) ·
[Whisper](https://github.com/openai/whisper) (MIT) · [Flask](https://flask.palletsprojects.com)
(BSD-3) · [python-docx](https://github.com/python-openxml/python-docx) (MIT).
I pesi dei modelli scaricati da `download_models.py` hanno licenze proprie dei rispettivi autori.

## Sostieni il progetto

Se ti è utile: [offrimi un caffè su Ko-fi](https://ko-fi.com/E7D425WCX9). Grazie.

## Changelog

Vedi [CHANGELOG.md](CHANGELOG.md).

## Licenza

[MIT](LICENSE).

---
---

<a id="english"></a>

# Sbobyner — in English

*🇮🇹 [Versione italiana sopra](#sbobiner).*

> Transcribing audio keeps getting harder. Every service is paid or works badly.
> This won't be perfect, but it does the job. And the file stays on your computer.
> Built for Mac because that's what I use right now. Contributions welcome.
>
> Install once. Drop in the file. Transcribe (do something else meanwhile). Save the transcript. Done.
> N.B.: you can't transcribe a concert.

Works on **Mac with Apple Silicon** and **Windows 10 / 11** (64-bit).

Transcription pipeline for **lectures and meetings**, built on Whisper.
Runs entirely **offline** after the initial setup. No account, no token.

Engine: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples/tree/main/whisper) on Mac (GPU),
[`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) on Windows (CPU).
Diarization: [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx).

---

## Initial setup (first time only, needs internet)

**Mac** — download the ZIP (**Code → Download ZIP**), extract it and double-click **`setup.command`**.
- If macOS blocks it: **System Settings → Privacy & Security → Open Anyway**
  (only once, also for `start.command`).
- Downloads ~460 MB for Whisper + ~35 MB for diarization. Total footprint **~1.1 GB**.

**Windows** — download the ZIP (**Code → Download ZIP**), extract it (e.g. to `C:\Sbobiner`,
preferably a path without accented letters) and double-click **`setup.bat`**.
- If *"Windows protected your PC"* shows up: **More info → Run anyway**.
- If Python is missing, the setup offers to install it (winget): then close and reopen `setup.bat`.
- Downloads a ~1.6 GB model. Total footprint **~2 GB**, all inside the program folder:
  deleting it uninstalls everything.

The setup creates the virtual environment, installs the dependencies and downloads the models.
`ffmpeg` is bundled, nothing to install.

## Daily use (offline)

**Mac** — double-click **`start.command`** from Finder: the browser opens at `http://127.0.0.1:5000`.

**Windows** — double-click **`start.bat`**: a **dedicated Edge window** opens
(or Chrome, if Edge is missing), with no tabs and no address bar.

Drop the file, pick the options, press **Trascrivi** ("Transcribe").
When it's done you download as **TXT**, **SRT**, **VTT** or **DOCX**.

Input formats: anything `ffmpeg` can read (mp3, wav, m4a, aac, ogg, flac,
and video mp4/mkv/mov too — the audio is extracted automatically).

N.B. the terminal window (the black window on Windows) must stay open for Sbobyner to keep
serving the web page.

---

## Configuration — `config.yaml`

Everything can be tuned there, without touching the code.

### Change language

```yaml
language: it        # italian (default)
```

- Change language via ISO 639-1 code (`en`, `fr`, `de`, `es`, `pt`, ...).
- `auto`: Whisper detects the language on its own (slower, less accurate).

### Whisper model

```yaml
model:
  name: large-v3-turbo-q4
```

| Value | Size | Notes |
|---|---|---|
| `large-v3-turbo-q4` | ~460 MB | **default**. 4-bit quantized turbo: light, quality close to the full turbo. |
| `large-v3-turbo` | ~1.5 GB | slightly more accurate, 3× the disk space. |
| `medium` | ~1.5 GB | fallback. |
| `small` | ~500 MB | ~2× faster, less accurate. |
| `large-v3` | ~3 GB | maximum accuracy, recommended with 16 GB+ of RAM. |

After changing `name`, run the setup again (`setup.command` / `setup.bat`) to fetch it:
at the end it offers to delete the old model and reclaim space.

Why turbo (and not `large-v3`): it's `large-v3` distilled (8 decoder layers instead of 32),
transcription accuracy almost identical but faster. The `-q4` variant halves the disk
size again with minimal quality loss; speed stays about the same.

On **Windows** the sizes above are the Mac ones: there is no 4-bit there, so
`large-v3-turbo-q4` and `large-v3-turbo` are the same model (~1.6 GB, quantized to int8 at load).

### Glossary and corrections

```yaml
glossary:            # injected as bias: helps with proper nouns and technical terms
  - Kubernetes
  - "Rossi"          # surnames that recur in the course/team
corrections:         # exact downstream replacement, if a term still comes out wrong
  "cuber netes": Kubernetes
```

### Diarization (who's speaking) by context

```yaml
diarization:
  preset: riunione   # or: aula
  aula:      { num_speakers: null, cluster_threshold: 0.70 }
  riunione:  { num_speakers: null, cluster_threshold: 0.50 }
```

- `aula` (classroom): many people, higher threshold (groups more, avoids inventing voices).
- `riunione` (meeting): few people, lower threshold (separates 2–6 speakers better).
- If you know how many people speak, set `num_speakers` (e.g. `3`) or use the
  **N. persone** field on the web page: diarization becomes more stable.

### Lecture/meeting post-processing

In `config.yaml` → `postprocess`: list of filler words to strip, pause threshold for
section breaks, trigger phrases for sections / action items / decisions. All editable.

> Sections and action items are **heuristic** (pauses + trigger phrases), not ML.
> If one day the accuracy isn't enough, the hook for a local LLM pass is in
> `postprocess.py` (`_split_sections` / `_extract`), marked with a `ponytail:` comment.

---

## Layout

| File | Responsibility |
|---|---|
| `audio.py` | normalize any input → 16 kHz mono wav |
| `transcribe.py` | Whisper engine + glossary injection |
| `diarize.py` | speaker diarization (sherpa-onnx), presets by context |
| `merge.py` | align text ↔ speaker |
| `postprocess.py` | cleanup, sections, action items, decisions |
| `export.py` | TXT / SRT / VTT / DOCX |
| `app.py` + `templates/index.html` | local server and web page |
| `config.yaml` | all configuration |
| `download_models.py` | download the models once |
| `setup.command` / `setup.bat` | installation (Mac / Windows) |
| `start.command` / `start.bat` | daily launch (Mac / Windows) |
| `test_pipeline.py` | self-check: `python test_pipeline.py` |

## Notes

- Speed measured on an 8 GB Mac with `large-v3-turbo-q4`
  (38 min of audio → ~3.5 min of transcription). Without diarization.
- On Windows transcription runs on the processor: roughly 20-25 minutes per hour of audio
  on a recent PC, up to an hour on older processors. To go faster: `model.name: small`.
- Everything stays local, in the `work/` folder. It also holds the intermediate
  `.wav` (~2 MB/min): empty it whenever you want.

## Credits

Built with [Claude](https://claude.ai) (Claude Code) using the
**[ponytail](https://github.com/DietrichGebert/ponytail)** plugin in `ultra` mode, which pushes
toward the simplest thing that works: standard library and native features
before adding dependencies or custom code.

Third-party components: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples)
(MIT) · [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) (MIT) ·
[`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (Apache-2.0) ·
[Whisper](https://github.com/openai/whisper) (MIT) · [Flask](https://flask.palletsprojects.com)
(BSD-3) · [python-docx](https://github.com/python-openxml/python-docx) (MIT).
The model weights downloaded by `download_models.py` have their own licenses from their respective authors.

## Support the project

If you find it useful: [buy me a coffee on Ko-fi](https://ko-fi.com/E7D425WCX9). Thanks.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE).
