# Changelog

Tutte le modifiche rilevanti a Sbobiner.
Formato ispirato a [Keep a Changelog](https://keepachangelog.com/it/1.1.0/).

## [1.6.0] - 2026-09-23

### Funzionalità

- **Supporto Windows 10 e 11** (64 bit): `setup.bat` e `start.bat` a doppio click.
  Il setup trova Python o propone di installarlo tramite winget, e controlla il
  runtime Visual C++.
- Su Windows la trascrizione usa **faster-whisper** su CPU (int8) con lo stesso
  modello Whisper; la barra mostra l'avanzamento reale, non una stima.
- Su Windows l'interfaccia si apre in una **finestra dedicata di Edge** (o di
  Chrome, se Edge manca), senza schede né barra degli indirizzi; la barra del
  titolo prende i colori di Sbobiner.
- Su Windows i modelli restano nella cartella del programma: cancellandola si
  disinstalla tutto.
- Icona dell'applicazione (scheda del browser, finestra, barra delle applicazioni).

### Modifiche

- Dopo un cambio di modello, il setup propone di eliminare quelli non più usati
  e lo fa tramite l'API di `huggingface_hub`: le versioni recenti condividono i
  file grossi tra modelli e cancellare la cartella a mano non liberava spazio.
- Guida e README aggiornati con l'installazione su Windows; corretti i link tra
  la parte italiana e quella inglese del README.

### Correzioni

- Un file trascinato fuori dal riquadro non sostituisce più la pagina.
- Il selettore file mostra anche `.m4a`, `.opus`, `.wma` e simili, che su
  Windows il filtro `audio/*` poteva nascondere.
- Il server non si blocca più se si clicca dentro la finestra nera su Windows
  (niente più log a ogni richiesta).

## [1.5.0] - 2026-08-27

Prima release pubblica.

### Funzionalità

- Trascrizione audio **completamente offline** dopo il setup iniziale, su Mac
  Apple Silicon: motore Whisper via MLX/Metal.
- Interfaccia web locale con drag & drop; `setup.command` e `start.command` a
  doppio click, nessun uso del terminale.
- Ingresso: qualsiasi formato audio o video leggibile da ffmpeg (mp3, wav, m4a,
  aac, ogg, mp4, mkv, …); ffmpeg incluso, nessuna installazione.
- Esportazione in **TXT, SRT, VTT, DOCX**. I file scaricati prendono il nome
  della traccia audio.
- Trascrizione come **testo continuo per turno di parola**: intestazione e
  timestamp solo al cambio di interlocutore, non a ogni frase.
- Riconoscimento di chi parla (speaker diarization) tramite sherpa-onnx, senza
  account né token. **Opzionale**, disattivato di default.
- Glossario e correzioni personalizzabili in `config.yaml` per la terminologia
  ricorrente.
- Post-elaborazione per lezioni e riunioni: divisione in sezioni, estrazione di
  action item e decisioni (solo in modalità riunione), pulizia degli intercalari.
- Barra di avanzamento con fase corrente e percentuale durante l'elaborazione.
- Modello Whisper predefinito `large-v3-turbo-q4`; installazione complessiva
  ~1,1 GB.

### Modifiche

- Riconoscimento di chi parla reso opt-in nell'interfaccia: i parametri
  "Contesto" e "Numero di persone" compaiono solo quando viene attivato.
- Segmentazione della diarization su modello quantizzato **int8** e inferenza
  ONNX **multi-thread**: circa il 25% più veloce, nessun calo di qualità
  rilevato. Valutata l'accelerazione CoreML/Neural Engine e scartata perché
  più lenta su questo modello.
- `mlx-whisper` installato senza `torch` e dipendenze correlate (dichiarate ma
  mai importate): circa 600 MB in meno nell'ambiente virtuale.

### Correzioni

- Risolto il blocco apparente durante il riconoscimento di chi parla su
  registrazioni lunghe (oltre un'ora): l'inferenza girava su un solo thread
  senza alcun riscontro di avanzamento.
- Download dei modelli: uso della CA bundle di `certifi` per l'HTTPS con il
  Python di python.org; corretto l'URL della release upstream di sherpa-onnx.
- La trascrizione non richiede più un `ffmpeg` di sistema: l'audio normalizzato
  viene passato direttamente ai motori come array.

[1.6.0]: https://github.com/SeltzLimited/Sbobiner/releases/tag/v1.6.0
[1.5.0]: https://github.com/SeltzLimited/Sbobiner/releases/tag/v1.5.0
