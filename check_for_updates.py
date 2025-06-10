import requests
import argparse
import tarfile
import zipfile
from packaging import version
from urllib.parse import unquote
import re
import os

def get_download_url(release_info, asset_index=0):
    """Ermittelt Download-URL aus Release-Informationen"""
    # 1. Prüfe Assets
    assets = release_info.get("assets", [])
    if assets:
        try:
            return assets[asset_index]["browser_download_url"]
        except IndexError:
            raise SystemExit(f"❌ Ungültiger Asset-Index: {asset_index}")

    # 2. Prüfe Source-Archive
    if "tarball_url" in release_info:
        return release_info["tarball_url"]

    # 3. Fallback auf Zipball
    if "zipball_url" in release_info:
        return release_info["zipball_url"]

    raise SystemExit("❌ Keine Download-Quelle gefunden")

def get_latest_release_info(owner, repo, token=None):
    """Holt Release-Informationen von GitHub"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"❌ API-Fehler: {e}")


def is_update_available(local_version, latest_version):
    """Vergleicht zwei Versionen auf SemVer-Basis"""
    try:
        # Entferne 'v'-Präfix für Vergleich
        local_clean = local_version.lstrip('v')
        latest_clean = latest_version.lstrip('v')

        return version.parse(local_clean) < version.parse(latest_clean)
    except Exception as e:
        raise SystemExit(f"❌ Versionsvergleich fehlgeschlagen: {e}")

def get_local_version():
    file1 = open("VERSION")
    line=file1.read()
    file1.close()
    return line


def download_asset(asset_info, download_dir=".", token=None):
    """Lädt eine Datei von GitHub herunter"""
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'

        # Dateiname extrahieren
        if "name" in asset_info:
            filename = asset_info["name"]
        else:
            # Fallback: Aus URL extrahieren
            filename = unquote(asset_info["browser_download_url"].split("/")[-1])
            filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)  # Sonderzeichen entfernen

        filepath = os.path.join(download_dir, filename)

        print(f"⬇️ Lade herunter: {filename}")
        with requests.get(asset_info["url"], headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0

            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = min(100, int(100 * downloaded / total_size))
                        print(f"\rFortschritt: {progress}%", end='')
            print("\n✅ Download abgeschlossen!")
        return filepath
    except Exception as e:
        raise SystemExit(f"❌ Download fehlgeschlagen: {e}")


def download_file(url, filepath, token=None):
    """Lädt eine Datei herunter mit Fortschrittsanzeige"""
    try:
        headers = {}
        if token:
            headers['Authorization'] = f'token {token}'

        print(f"⬇️ Lade herunter: {os.path.basename(filepath)}")
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded = 0

            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = min(100, int(100 * downloaded / total_size))
                        print(f"\rFortschritt: {progress}%", end='')
            print("\n✅ Download abgeschlossen!")
        return filepath
    except Exception as e:
        raise SystemExit(f"❌ Download fehlgeschlagen: {e}")


def CheckForUpdates():

    local_version=get_local_version()
    local_version="0.2"

    try:
        latest_version = get_latest_release_info("StephanMrak", "HM01")
        # Download-URL ermitteln
        try:
            download_url = get_download_url(latest_version, 0)
        except SystemExit as e:
            print(e)
            return
        if is_update_available(local_version, latest_version["tag_name"]):
            print(f"✅ Update verfügbar! Lokal: {local_version} | Neueste: {latest_version["tag_name"]}")
            home_directory = os.path.expanduser("~")
            if download_url.find("tarball")>0:
                downloaded_file = download_file(download_url, home_directory+"/Downloads/HM01-source.tar.gz", None)
                tar = tarfile.open(downloaded_file)
                tar.extractall(home_directory+"/Downloads/HM01-source")
                tar.close()
            else:
                downloaded_file = download_file(download_url, home_directory + "/Downloads/HM01-source.zip", None)
                with zipfile.ZipFile(downloaded_file, 'r') as zip_ref:
                    zip_ref.extractall(home_directory+"/Downloads/HM01-source")
            print(f"💾 Datei gespeichert unter: {downloaded_file}")
        else:
            print(f"✔️ Kein Update verfügbar. Version {local_version} ist aktuell.")
            return


    except KeyboardInterrupt:
        print("\n⛔ Skript abgebrochen")


if __name__ == "__main__":
    CheckForUpdates()