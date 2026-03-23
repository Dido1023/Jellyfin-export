#!/usr/bin/env python3
"""Export Jellyfin movies to a Letterboxd-compatible CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import os
import ssl
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request


DEFAULT_OUTPUT = "letterboxd-import.csv"
DEFAULT_TIMEOUT = 30
DEFAULT_PAGE_SIZE = 200
DEFAULT_ENV_FILE = ".env"


def parse_bool(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def unquote_env_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def load_env_file(env_file: str) -> None:
    path = Path(env_file)
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        os.environ.setdefault(key, unquote_env_value(value))


def parse_args() -> argparse.Namespace:
    bootstrap = argparse.ArgumentParser(add_help=False)
    bootstrap.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    bootstrap_args, remaining_argv = bootstrap.parse_known_args()
    load_env_file(bootstrap_args.env_file)

    parser = argparse.ArgumentParser(
        description=(
            "Recupera tutti i film da Jellyfin e genera un CSV compatibile con "
            "l'import di Letterboxd."
        )
    )
    parser.add_argument(
        "--server-url",
        default=os.environ.get("JELLYFIN_SERVER_URL"),
        help="URL base del server Jellyfin, es. http://192.168.1.10:8096",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("JELLYFIN_API_KEY"),
        help="API key di Jellyfin. In alternativa usa la variabile JELLYFIN_API_KEY.",
    )
    parser.add_argument(
        "--env-file",
        default=bootstrap_args.env_file,
        help=f"Percorso del file .env da caricare. Default: {DEFAULT_ENV_FILE}",
    )
    parser.add_argument(
        "--output",
        default=os.environ.get("LETTERBOXD_OUTPUT", DEFAULT_OUTPUT),
        help=f"Percorso del CSV da generare. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--user-id",
        default=os.environ.get("JELLYFIN_USER_ID"),
        help=(
            "ID utente Jellyfin da usare per l'endpoint /Users/{userId}/Items. "
            "Se omesso, lo script usa /Items."
        ),
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("JELLYFIN_USERNAME"),
        help=(
            "Nome utente Jellyfin da risolvere automaticamente in user-id. "
            "Se specificato, ha priorita' su --user-id."
        ),
    )
    parser.add_argument(
        "--parent-id",
        default=os.environ.get("JELLYFIN_PARENT_ID"),
        help=(
            "ID opzionale di una libreria/cartella Jellyfin per limitare "
            "l'esportazione a quella sorgente."
        ),
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=int(os.environ.get("JELLYFIN_PAGE_SIZE", DEFAULT_PAGE_SIZE)),
        help=f"Numero di elementi richiesti per pagina. Default: {DEFAULT_PAGE_SIZE}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("JELLYFIN_TIMEOUT", DEFAULT_TIMEOUT)),
        help=f"Timeout in secondi per richiesta HTTP. Default: {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        default=parse_bool(os.environ.get("JELLYFIN_INSECURE")),
        help="Disabilita la verifica TLS/SSL. Utile con certificati self-signed.",
    )
    return parser.parse_args(remaining_argv)


def require_args(args: argparse.Namespace) -> None:
    missing = []
    if not args.server_url:
        missing.append("--server-url")
    if not args.api_key:
        missing.append("--api-key")
    if missing:
        raise SystemExit(f"Parametri mancanti: {', '.join(missing)}")


def make_ssl_context(insecure: bool) -> ssl.SSLContext | None:
    if insecure:
        return ssl._create_unverified_context()
    return None


def build_headers(api_key: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "User-Agent": "jellyfin-letterboxd-export/1.0",
        "X-Emby-Token": api_key,
    }


def api_get_json(
    base_url: str,
    path: str,
    api_key: str,
    timeout: int,
    insecure: bool,
    query: dict[str, Any] | None = None,
) -> Any:
    safe_base_url = base_url.rstrip("/")
    url = f"{safe_base_url}{path}"
    if query:
        filtered_query = {key: value for key, value in query.items() if value not in (None, "")}
        url = f"{url}?{parse.urlencode(filtered_query, doseq=True)}"

    req = request.Request(url, headers=build_headers(api_key))
    ssl_context = make_ssl_context(insecure)

    try:
        with request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            payload = response.read().decode(charset)
            return json.loads(payload)
    except error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Richiesta fallita ({exc.code}) su {url}\nDettagli: {message or exc.reason}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(f"Impossibile raggiungere Jellyfin su {url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Risposta JSON non valida da {url}") from exc


def first_present(obj: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in obj:
            return obj[key]
    return None


def resolve_user_id(
    base_url: str,
    api_key: str,
    username: str,
    timeout: int,
    insecure: bool,
) -> str:
    users = api_get_json(
        base_url=base_url,
        path="/Users",
        api_key=api_key,
        timeout=timeout,
        insecure=insecure,
    )

    if not isinstance(users, list):
        raise RuntimeError("La risposta di /Users non ha il formato atteso.")

    normalized = username.casefold()
    for user in users:
        candidate_name = str(first_present(user, "Name", "name") or "")
        if candidate_name.casefold() == normalized:
            user_id = first_present(user, "Id", "id")
            if user_id:
                return str(user_id)

    available = ", ".join(
        sorted(
            str(first_present(user, "Name", "name") or "")
            for user in users
            if first_present(user, "Name", "name")
        )
    )
    details = f" Utenti disponibili: {available}" if available else ""
    raise RuntimeError(f"Utente Jellyfin '{username}' non trovato.{details}")


def fetch_movies(
    base_url: str,
    api_key: str,
    timeout: int,
    insecure: bool,
    page_size: int,
    user_id: str | None,
    parent_id: str | None,
) -> list[dict[str, Any]]:
    if page_size <= 0:
        raise RuntimeError("--page-size deve essere maggiore di zero.")

    path = f"/Users/{user_id}/Items" if user_id else "/Items"
    start_index = 0
    total_count: int | None = None
    movies: list[dict[str, Any]] = []

    while True:
        payload = api_get_json(
            base_url=base_url,
            path=path,
            api_key=api_key,
            timeout=timeout,
            insecure=insecure,
            query={
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "Fields": "ProviderIds,People,PremiereDate",
                "SortBy": "SortName",
                "SortOrder": "Ascending",
                "EnableTotalRecordCount": "true",
                "StartIndex": start_index,
                "Limit": page_size,
                "ParentId": parent_id,
            },
        )

        if not isinstance(payload, dict):
            raise RuntimeError(f"La risposta di {path} non ha il formato atteso.")

        items = first_present(payload, "Items", "items") or []
        total_count = first_present(payload, "TotalRecordCount", "totalRecordCount", "total_count")

        if not isinstance(items, list):
            raise RuntimeError("Il campo Items della risposta Jellyfin non e' una lista.")

        movies.extend(item for item in items if isinstance(item, dict))

        if not items:
            break

        start_index += len(items)
        if total_count is not None and start_index >= int(total_count):
            break

    return movies


def infer_year(item: dict[str, Any]) -> str:
    production_year = first_present(item, "ProductionYear", "productionYear")
    if production_year:
        return str(production_year)

    premiere_date = first_present(item, "PremiereDate", "premiereDate")
    if isinstance(premiere_date, str) and premiere_date:
        try:
            return str(datetime.fromisoformat(premiere_date.replace("Z", "+00:00")).year)
        except ValueError:
            return premiere_date[:4]

    return ""


def extract_directors(item: dict[str, Any]) -> str:
    people = first_present(item, "People", "people") or []
    if not isinstance(people, list):
        return ""

    directors: list[str] = []
    for person in people:
        if not isinstance(person, dict):
            continue
        role = str(first_present(person, "Type", "type") or "")
        if role.lower() != "director":
            continue
        name = str(first_present(person, "Name", "name") or "").strip()
        if name:
            directors.append(name)

    # Deduplica conservando l'ordine.
    unique_directors: list[str] = []
    seen: set[str] = set()
    for director in directors:
        marker = director.casefold()
        if marker in seen:
            continue
        seen.add(marker)
        unique_directors.append(director)

    return ", ".join(unique_directors)


def movie_to_letterboxd_row(item: dict[str, Any]) -> dict[str, str]:
    provider_ids = first_present(item, "ProviderIds", "providerIds") or {}
    if not isinstance(provider_ids, dict):
        provider_ids = {}

    title = str(first_present(item, "Name", "name") or "").strip()
    tmdb_id = str(first_present(provider_ids, "Tmdb", "tmdb") or "").strip()
    imdb_id = str(first_present(provider_ids, "Imdb", "imdb") or "").strip()

    return {
        "Title": title,
        "Year": infer_year(item),
        "Directors": extract_directors(item),
        "tmdbID": tmdb_id,
        "imdbID": imdb_id,
    }


def write_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["Title", "Year", "Directors", "tmdbID", "imdbID"]

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    require_args(args)

    try:
        user_id = args.user_id
        if args.username:
            user_id = resolve_user_id(
                base_url=args.server_url,
                api_key=args.api_key,
                username=args.username,
                timeout=args.timeout,
                insecure=args.insecure,
            )

        movies = fetch_movies(
            base_url=args.server_url,
            api_key=args.api_key,
            timeout=args.timeout,
            insecure=args.insecure,
            page_size=args.page_size,
            user_id=user_id,
            parent_id=args.parent_id,
        )

        rows = [movie_to_letterboxd_row(movie) for movie in movies]
        output_path = Path(args.output).resolve()
        write_csv(output_path, rows)

        with_ids = sum(1 for row in rows if row["tmdbID"] or row["imdbID"])
        print(
            f"Esportati {len(rows)} film in '{output_path}'. "
            f"{with_ids} righe hanno almeno un ID tra TMDB o IMDb."
        )
        return 0
    except RuntimeError as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
