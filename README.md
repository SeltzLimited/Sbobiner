# Sbobiner

> Sempre più difficile trascrivere un audio. Tutti i servizi sono a pagamento o funzionano male.
> Questo non sarà perfetto, ma fa il suo. E il file resta sul tuo pc.
> Fatto per MAC perché è quello che uso al momento. Liberi di contribuire.
>
> Installi una sola volta. Carichi il file. Trascrivi. Scarichi la trascrizione. Fine.
> N.B.: Non puoi trascrivere un concerto.

Pipeline di trascrizione per **lezioni e riunioni**, costruita su Whisper.
Gira interamente **offline** dopo il setup iniziale. Nessun account, nessun token.

Motore: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples/tree/main/whisper)
Diarization: [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (modelli liberi, senza gating).

---

**Guida per chi non usa il terminale:** [`GUIDA.md`](GUIDA.md).

## Setup iniziale (una volta sola, serve internet)

Doppio click su **`setup.command`**.

Questo crea l'ambiente virtuale, installa le dipendenze e scarica i modelli
(~460 MB per Whisper + ~35 MB per la diarization). `ffmpeg` è incluso, non va installato.
Ingombro totale dell'installazione: **~1,1 GB** (`.venv` + modelli).

## Uso quotidiano (Offline)

Doppio click su **`start.command`** dal Finder.
Si apre il browser su `http://127.0.0.1:5000`: trascina il file, scegli le opzioni, premi **Trascrivi**.
A fine elaborazione scarichi in **TXT**, **SRT**, **VTT** o **DOCX**.

Formati in ingresso: qualsiasi cosa `ffmpeg` sappia leggere (mp3, wav, m4a, aac, ogg, flac,
e anche video mp4/mkv/mov — l'audio viene estratto in automatico).

N.B. la finestra del terminale deve rimanere aperta per permettere a Sbobiner di funzionare nella pagina web.

---

## Configurazione — `config.yaml`

Tutto si può regolare da lì, senza toccare il codice.

### Cambiare lingua

```yaml
language: it        # italiano (default)
```

- Un'altra lingua: metti il codice ISO 639-1 (`en`, `fr`, `de`, `es`, `pt`, ...).
- `auto`: Whisper rileva la lingua da solo (più lento, meno preciso).
- Si può anche scegliere dal menu **Lingua** nella pagina web, senza modificare il file.

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

Dopo aver cambiato `name`, riesegui `python download_models.py` (con la `.venv` attiva) per scaricarlo:
stampa anche il comando per cancellare il modello vecchio dalla cache e recuperare spazio.

Perché il turbo (e non `large-v3`): è `large-v3` distillato (8 layer di decoder invece di 32),
precisione in trascrizione quasi identica ma molto più veloce. La variante `-q4` dimezza
ancora il peso su disco con una perdita di qualità minima; la velocità resta simile.

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

## Note

- Velocità misurata su Mac 8 GB con `large-v3-turbo-q4`: ~12× il tempo reale
  (38 min di audio → ~3,5 min di trascrizione). Senza diarization.
- Tutto resta in locale, nella cartella `work/`. Contiene anche il
  `.wav` intermedio (~2 MB/min): svuotala quando vuoi.

## Crediti

Sviluppato con [Claude](https://claude.ai) (Claude Code) usando il plugin
**[ponytail](https://github.com/DietrichGebert/ponytail)** in modalità `ultra`, che spinge
verso la soluzione più semplice che funziona: libreria standard e funzionalità native
prima di aggiungere dipendenze o codice custom.

Componenti di terze parti: [`mlx-whisper`](https://github.com/ml-explore/mlx-examples)
(MIT) · [`sherpa-onnx`](https://github.com/k2-fsa/sherpa-onnx) (Apache-2.0) ·
[Whisper](https://github.com/openai/whisper) (MIT) · [Flask](https://flask.palletsprojects.com)
(BSD-3) · [python-docx](https://github.com/python-openxml/python-docx) (MIT).
I pesi dei modelli scaricati da `download_models.py` hanno licenze proprie dei rispettivi autori.

## Changelog

Vedi [CHANGELOG.md](CHANGELOG.md).

## Licenza

[MIT](LICENSE).
