# Trascrizione offline

Pipeline di trascrizione per **lezioni e riunioni**, costruita sopra Whisper.
Gira interamente **offline** dopo il setup iniziale. Nessun account, nessun token.

Motore: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
(accelerazione Metal su Apple Silicon).
Diarization: [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (modelli liberi, senza gating).

---

## Setup iniziale (una volta sola, serve internet)

```bash
cd ~/Documents/trascrizione-offline
./setup.sh
```

Lo script crea l'ambiente virtuale, installa le dipendenze e scarica i modelli
(~1.5 GB per Whisper + ~30 MB per la diarization). `ffmpeg` è incluso, non va installato.

## Uso quotidiano (offline)

Doppio click su **`start.command`** dal Finder.
Si apre il browser su `http://127.0.0.1:5000`: trascina il file, scegli le opzioni, premi **Trascrivi**.
A fine elaborazione scarichi in **TXT**, **SRT**, **VTT** o **DOCX**.

> Primo avvio: macOS può bloccare `start.command` ("sviluppatore non identificato").
> Tasto destro sul file → **Apri** → **Apri**. Solo la prima volta.

Formati in ingresso: qualsiasi cosa `ffmpeg` sappia leggere (mp3, wav, m4a, aac, ogg, flac,
e anche video mp4/mkv/mov — l'audio viene estratto in automatico).

---

## Configurazione — `config.yaml`

Tutto si regola da lì, senza toccare il codice.

### Cambiare lingua

```yaml
language: it        # italiano (default)
```

- Un'altra lingua: metti il codice ISO 639-1 (`en`, `fr`, `de`, `es`, `pt`, ...).
- `auto`: Whisper rileva la lingua da solo (più lento, un po' meno preciso).
- Si può anche scegliere al volo dal menu **Lingua** nella pagina web, senza modificare il file.

### Modello Whisper (importante con 8 GB di RAM)

```yaml
model:
  name: large-v3-turbo
```

| Valore | Peso | Note |
|---|---|---|
| `large-v3-turbo` | ~1.5 GB | **default**. Ottimo compromesso, va bene su 8 GB. |
| `large-v3-turbo-q4` | ~0.5 GB | usalo se noti swap / lentezza da memoria piena |
| `medium` | ~1.5 GB | fallback se turbo dà problemi |
| `small` | ~0.5 GB | veloce, meno preciso |
| `large-v3` | ~3 GB | massima precisione, consigliato con 16 GB+ |

Dopo aver cambiato `name`, riesegui `python download_models.py` (con la `.venv` attiva) per scaricarlo.

Perché `large-v3-turbo`: è `large-v3` distillato (8 layer di decoder invece di 32).
Precisione in trascrizione quasi identica, ma 4–8× più veloce e con impronta di memoria
paragonabile a `medium` — quindi conviene anche su una macchina da 8 GB.

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
| `test_pipeline.py` | self-check: `python test_pipeline.py` |

## Fine-tuning (in futuro)

Non incluso: serve materiale già trascritto. Quando lo avrai, `mlx` supporta il
fine-tuning LoRA leggero di Whisper; si aggiunge come script separato senza toccare la pipeline.

## Note

- Prima esecuzione della trascrizione su 8 GB: un'ora di lezione può richiedere
  ~30–60 min. È batch, si può lasciar girare.
- Tutto resta in locale, nella cartella `work/` (ignorata da git). Svuotala quando vuoi.
