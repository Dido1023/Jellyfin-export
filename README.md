# Jellyfin Export for Letterboxd

Esporta i film della tua libreria Jellyfin in un file CSV compatibile con l'import di Letterboxd.

Il progetto nasce per un caso semplice e utile: recuperare l'elenco dei film dal proprio server Jellyfin tramite API e generare un CSV pronto da caricare su Letterboxd come lista.

## Cosa fa

- Recupera tutti gli elementi `Movie` da Jellyfin
- Supporta paginazione automatica delle API
- Esporta un CSV compatibile con Letterboxd
- Usa i provider ID `tmdbID` e `imdbID` quando disponibili
- Supporta configurazione tramite file `.env`
- Non richiede dipendenze Python esterne

## Requisiti

- Windows, macOS o Linux
- Python 3.10 o superiore
- URL del server Jellyfin
- API key Jellyfin

## Installazione

Clona il repository:

```bash
git clone https://github.com/tuo-utente/jellyfin-export.git
cd jellyfin-export
```

Se sei su Windows e non hai Python, puoi installarlo con:

```powershell
winget install Python.Python.3.12
```

Verifica poi l'installazione:

```powershell
python --version
```

## Configurazione

Copia [`.env.example`](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env.example) in `.env`:

```powershell
Copy-Item .\.env.example .\.env
```

Poi modifica [`.env`](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env) con i tuoi dati:

```env
JELLYFIN_SERVER_URL=http://localhost:8096
JELLYFIN_API_KEY=YOUR_JELLYFIN_API_KEY
JELLYFIN_USERNAME=your_username
LETTERBOXD_OUTPUT=letterboxd-import.csv
```

Il file `.env` viene ignorato da git, quindi non finira' su GitHub.

## Utilizzo rapido

Con la configurazione nel file `.env`:

```powershell
python .\export_jellyfin_to_letterboxd.py
```

Oppure passando i parametri direttamente:

```powershell
python .\export_jellyfin_to_letterboxd.py `
  --server-url "http://localhost:8096" `
  --api-key "YOUR_JELLYFIN_API_KEY" `
  --username "your_username" `
  --output ".\letterboxd-import.csv"
```

Se il tuo server usa HTTPS con certificato self-signed:

```powershell
python .\export_jellyfin_to_letterboxd.py --insecure
```

## Parametri supportati

- `--server-url`: URL base del server Jellyfin
- `--api-key`: API key Jellyfin
- `--env-file`: percorso di un file `.env` alternativo
- `--output`: percorso del CSV generato
- `--username`: nome utente Jellyfin da risolvere automaticamente
- `--user-id`: ID utente Jellyfin
- `--parent-id`: limita l'export a una libreria/cartella specifica
- `--page-size`: numero di risultati richiesti per pagina
- `--timeout`: timeout HTTP in secondi
- `--insecure`: disabilita la verifica TLS/SSL

I valori passati via CLI hanno priorita' rispetto a quelli definiti nel file `.env`.

## Variabili `.env` supportate

- `JELLYFIN_SERVER_URL`
- `JELLYFIN_API_KEY`
- `JELLYFIN_USERNAME`
- `JELLYFIN_USER_ID`
- `JELLYFIN_PARENT_ID`
- `JELLYFIN_PAGE_SIZE`
- `JELLYFIN_TIMEOUT`
- `JELLYFIN_INSECURE`
- `LETTERBOXD_OUTPUT`

## Formato CSV esportato

Il CSV contiene queste colonne:

- `Title`
- `Year`
- `Directors`
- `tmdbID`
- `imdbID`

Letterboxd usa `tmdbID` e `imdbID` per un match preciso quando presenti. Se mancano, prova a riconoscere il film tramite titolo, anno e regista.

## Import su Letterboxd

1. Genera il file CSV con lo script
2. Vai su `https://letterboxd.com/importing-data/`
3. Carica il CSV
4. Controlla l'anteprima dei match prima di confermare

Se vuoi importare i film dentro una lista specifica, puoi avviare l'import dalla pagina di modifica della lista su Letterboxd.

## Note utili

- Per ottenere i match migliori, conviene che Jellyfin abbia valorizzati i provider ID `Tmdb` e/o `Imdb`
- Se alcuni film non hanno ID esterni, Letterboxd fara' un best guess
- Letterboxd applica un limite di circa 1 MB ai file CSV caricati
- Se la tua libreria e' molto grande, potrebbe essere necessario dividere il file in piu' parti

## Sicurezza

- Non committare mai il tuo file `.env`
- Usa `.env.example` come template pubblico
- Tieni privata la tua API key Jellyfin

## Limitazioni

- Lo script esporta i film presenti in Jellyfin, non lo storico completo delle attivita'
- Il match finale dipende anche dalla qualita' dei metadati presenti nella tua libreria

## Repository structure

- [export_jellyfin_to_letterboxd.py](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/export_jellyfin_to_letterboxd.py): script principale
- [.env.example](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env.example): template di configurazione
- [.gitignore](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.gitignore): file ignorati da git

## Riferimenti

- Letterboxd import docs: https://letterboxd.com/importing-data/
- Jellyfin API docs: https://api.jellyfin.org/
