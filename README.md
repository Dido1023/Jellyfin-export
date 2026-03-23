# Jellyfin Export for Letterboxd

Script Python che legge tutti i film dalla tua libreria Jellyfin tramite API e genera un CSV compatibile con l'import di Letterboxd.

## Requisiti

- Python 3.10+ installato
- URL del server Jellyfin
- API key Jellyfin

## Configurazione con `.env`

Puoi tenere i dati in un file `.env` nella cartella del progetto.

1. Crea il file partendo da [`.env.example`](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env.example)
2. Rinominane una copia in `.env`
3. Inserisci i tuoi valori

Esempio:

```env
JELLYFIN_SERVER_URL=http://localhost:8096
JELLYFIN_API_KEY=LA_TUA_API_KEY
JELLYFIN_USERNAME=tuo_utente
LETTERBOXD_OUTPUT=letterboxd-import.csv
```

Poi puoi lanciare semplicemente:

```powershell
python .\export_jellyfin_to_letterboxd.py
```

Il file `.env` e' ignorato da git, quindi non finira' nel repository.

## Uso rapido

```powershell
python .\export_jellyfin_to_letterboxd.py `
  --server-url "http://localhost:8096" `
  --api-key "LA_TUA_API_KEY" `
  --output ".\letterboxd-import.csv"
```

Se vuoi usare un utente specifico Jellyfin:

```powershell
python .\export_jellyfin_to_letterboxd.py `
  --server-url "http://localhost:8096" `
  --api-key "LA_TUA_API_KEY" `
  --username "tuo_utente" `
  --output ".\letterboxd-import.csv"
```

Se il server usa HTTPS con certificato self-signed:

```powershell
python .\export_jellyfin_to_letterboxd.py `
  --server-url "https://jellyfin.lan" `
  --api-key "LA_TUA_API_KEY" `
  --insecure
```

## Variabili d'ambiente

Lo script legge automaticamente anche un file `.env` locale. In alternativa puoi impostare variabili d'ambiente manuali nella shell:

Puoi evitare di passare ogni volta URL e API key:

```powershell
$env:JELLYFIN_SERVER_URL = "http://localhost:8096"
$env:JELLYFIN_API_KEY = "LA_TUA_API_KEY"
python .\export_jellyfin_to_letterboxd.py
```

Se vuoi usare un file diverso da `.env`:

```powershell
python .\export_jellyfin_to_letterboxd.py --env-file ".env.prod"
```

## Parametri principali

- `--server-url`: URL base del server Jellyfin
- `--api-key`: API key Jellyfin
- `--env-file`: percorso di un file `.env` alternativo
- `--output`: percorso del CSV finale
- `--username`: risolve automaticamente l'utente e usa `/Users/{userId}/Items`
- `--user-id`: usa direttamente un ID utente Jellyfin
- `--parent-id`: limita l'export a una specifica libreria/cartella
- `--page-size`: numero di film per pagina API
- `--timeout`: timeout HTTP in secondi
- `--insecure`: disabilita la verifica TLS/SSL

## Colonne esportate

Lo script produce queste colonne nel CSV:

- `Title`
- `Year`
- `Directors`
- `tmdbID`
- `imdbID`

Letterboxd accetta queste intestazioni nel proprio formato CSV e usa `tmdbID` o `imdbID` per un match esatto quando disponibili; altrimenti prova a riconoscere il film con titolo, anno e regista.

## Import su Letterboxd

1. Apri la pagina di import di Letterboxd:
   https://letterboxd.com/importing-data/
2. Carica il CSV generato.
3. Se vuoi creare o aggiornare una lista, avvia l'import dalla pagina di modifica di una lista Letterboxd.
4. Controlla l'anteprima dei match prima di confermare.

## Note utili

- Jellyfin deve avere valorizzati i provider ID (`Tmdb` e/o `Imdb`) per ottenere i match migliori.
- Se alcuni film non hanno ID esterni, Letterboxd fara' un best guess usando `Title`, `Year` e `Directors`.
- Letterboxd impone un limite file di circa 1 MB sull'upload CSV; se la tua libreria e' molto grande, potrebbe essere necessario dividere il file.
- I valori passati via CLI hanno priorita' rispetto a quelli nel file `.env`.
