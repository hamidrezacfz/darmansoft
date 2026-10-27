"""Local backup utilities for the installed application."""
import json
import os
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings


def data_dir():
    root = Path(os.environ.get('CLINITA_DATA_DIR', settings.BASE_DIR))
    root.mkdir(parents=True, exist_ok=True)
    return root


def settings_path(): return data_dir() / 'backup-settings.json'


def default_backup_dir():
    folder = data_dir() / 'backups'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def load_settings():
    defaults = {'enabled': False, 'interval_days': 1, 'folder': str(default_backup_dir()), 'last_backup': ''}
    try:
        return {**defaults, **json.loads(settings_path().read_text(encoding='utf-8'))}
    except (OSError, ValueError, json.JSONDecodeError):
        return defaults


def save_settings(values):
    current = load_settings(); current.update(values)
    settings_path().write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding='utf-8')
    return current


def backup_database(destination=None):
    config = load_settings()
    folder = Path(destination or config['folder']).expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    db_path = Path(settings.DATABASES['default']['NAME'])
    if not db_path.exists(): raise FileNotFoundError('فایل اطلاعات برنامه پیدا نشد.')
    archive = folder / f"DarmanSoft-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.zip"
    with tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False) as temp: snapshot = Path(temp.name)
    try:
        source, target = sqlite3.connect(db_path), sqlite3.connect(snapshot)
        with target: source.backup(target)
        target.close(); source.close()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
            bundle.write(snapshot, 'db.sqlite3')
            bundle.writestr('info.txt', f'درمان‌سافت\nزمان تهیه: {datetime.now().isoformat()}\n')
    finally: snapshot.unlink(missing_ok=True)
    save_settings({'last_backup': datetime.now().isoformat(), 'folder': str(folder)})
    return archive


def run_scheduled_backup():
    config = load_settings()
    if not config.get('enabled'): return None
    try:
        last = datetime.fromisoformat(config['last_backup']) if config.get('last_backup') else None
        interval = max(1, int(config.get('interval_days', 1)))
    except (ValueError, TypeError): last, interval = None, 1
    if last and datetime.now() < last + timedelta(days=interval): return None
    return backup_database()
