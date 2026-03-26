# Jellyfin Export for Letterboxd

Export the movies in your Jellyfin library to a CSV file that can be imported into Letterboxd.

This project is built for a simple and practical use case: fetch your movie collection from a Jellyfin server through the API and generate a CSV file that is ready to upload to Letterboxd as a list.

## What it does

- Fetches all `Movie` items from Jellyfin
- Supports automatic API pagination
- Exports a Letterboxd-compatible CSV file
- Splits the export into numbered files after 1800 movies per file
- Uses `tmdbID` and `imdbID` provider IDs when available
- Supports configuration through a `.env` file
- Does not require external Python dependencies

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or later
- A Jellyfin server URL
- A Jellyfin API key

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/jellyfin-export.git
cd jellyfin-export
```

If you are on Windows and do not have Python installed yet, you can install it with:

```powershell
winget install Python.Python.3.12
```

Then verify the installation:

```powershell
python --version
```

## Configuration

Copy [`.env.example`](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env.example) to `.env`:

```powershell
Copy-Item .\.env.example .\.env
```

Then edit [`.env`](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env) with your values:

```env
JELLYFIN_SERVER_URL=http://localhost:8096
JELLYFIN_API_KEY=YOUR_JELLYFIN_API_KEY
JELLYFIN_USERNAME=your_username
LETTERBOXD_OUTPUT=letterboxd-import.csv
LETTERBOXD_MAX_MOVIES_PER_FILE=1800
```

The `.env` file is ignored by git, so it will not be pushed to GitHub. All `.csv` files are also ignored in this project.

## Quick Start

With configuration stored in `.env`:

```powershell
python .\export_jellyfin_to_letterboxd.py
```

Or by passing parameters directly:

```powershell
python .\export_jellyfin_to_letterboxd.py `
  --server-url "http://localhost:8096" `
  --api-key "YOUR_JELLYFIN_API_KEY" `
  --username "your_username" `
  --output ".\letterboxd-import.csv"
```

If your server uses HTTPS with a self-signed certificate:

```powershell
python .\export_jellyfin_to_letterboxd.py --insecure
```

If more than 1800 movies are exported, the script automatically creates numbered files such as:

- `letterboxd-import-1.csv`
- `letterboxd-import-2.csv`
- `letterboxd-import-3.csv`

## Supported Parameters

- `--server-url`: Jellyfin base server URL
- `--api-key`: Jellyfin API key
- `--env-file`: path to an alternative `.env` file
- `--output`: output CSV file path
- `--max-movies-per-file`: maximum number of movies per CSV file before splitting
- `--username`: Jellyfin username to resolve automatically
- `--user-id`: Jellyfin user ID
- `--parent-id`: limit the export to a specific library or folder
- `--page-size`: number of results requested per page
- `--timeout`: HTTP timeout in seconds
- `--insecure`: disable TLS/SSL certificate verification

CLI arguments take priority over values defined in the `.env` file.

## Supported `.env` Variables

- `JELLYFIN_SERVER_URL`
- `JELLYFIN_API_KEY`
- `JELLYFIN_USERNAME`
- `JELLYFIN_USER_ID`
- `JELLYFIN_PARENT_ID`
- `JELLYFIN_PAGE_SIZE`
- `JELLYFIN_TIMEOUT`
- `JELLYFIN_INSECURE`
- `LETTERBOXD_OUTPUT`
- `LETTERBOXD_MAX_MOVIES_PER_FILE`

## Exported CSV Format

The generated CSV includes these columns:

- `Title`
- `Year`
- `Directors`
- `tmdbID`
- `imdbID`

Letterboxd uses `tmdbID` and `imdbID` for precise matching when available. If they are missing, it tries to match by title, year, and director.

## Importing into Letterboxd

1. Generate the CSV file with the script
2. Go to `https://letterboxd.com/importing-data/`
3. Upload the CSV file
4. Review the match preview before confirming

If you want to import the movies into a specific list, you can start the import from that list's edit page in Letterboxd.

## Notes

- For the best results, make sure Jellyfin has `Tmdb` and/or `Imdb` provider IDs in its metadata
- If some movies do not have external IDs, Letterboxd will fall back to best-guess matching
- Letterboxd applies an upload limit of about 1 MB for CSV files
- The export is automatically split into multiple numbered files after 1800 movies per file

## Limitations

- The script exports movies currently available in Jellyfin, not your full activity history
- Final matching quality also depends on the metadata quality in your Jellyfin library

## Repository Structure

- [export_jellyfin_to_letterboxd.py](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/export_jellyfin_to_letterboxd.py): main script
- [.env.example](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.env.example): configuration template
- [.gitignore](c:/Users/Dionigi/Documents/GitHub/Jellyfin-export/.gitignore): ignored files configuration

## References

- Letterboxd import docs: https://letterboxd.com/importing-data/
- Jellyfin API docs: https://api.jellyfin.org/
