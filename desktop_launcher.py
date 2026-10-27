"""Windows launcher used by the installed Mehr Darman application."""
import logging
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path
from wsgiref.simple_server import make_server


APP_NAME = 'Clinita'
PORT = int(os.environ.get('CLINITA_PORT', '8001'))


def app_data_dir():
    root = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    folder_name = 'DarmanSoftDemo' if os.environ.get('DARMANSOFT_EDITION') == 'demo' else APP_NAME
    folder = root / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def configure_environment(data_dir):
    os.environ['CLINITA_DATA_DIR'] = str(data_dir)
    os.environ['CLINITA_DB_PATH'] = str(data_dir / 'db.sqlite3')
    os.environ['CLINITA_PACKAGED'] = '1'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


def ensure_first_admin():
    """Create the initial local administrator only on a fresh installation."""
    from django.contrib.auth.models import User
    from accounts.models import UserProfile

    user, created = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True},
    )
    if created:
        user.set_password('adminadmin')
        user.save(update_fields=['password'])
    UserProfile.objects.get_or_create(user=user, defaults={'role': UserProfile.Role.ADMIN})


def port_is_open():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.settimeout(0.3)
        return connection.connect_ex(('127.0.0.1', PORT)) == 0


def open_browser():
    webbrowser.open_new(f'http://127.0.0.1:{PORT}/login/')


def main():
    data_dir = app_data_dir()
    logging.basicConfig(
        filename=data_dir / 'clinita.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    configure_environment(data_dir)

    if port_is_open():
        open_browser()
        return

    try:
        import django
        django.setup()
        from django.core.management import call_command
        from django.core.wsgi import get_wsgi_application

        call_command('migrate', interactive=False, verbosity=0)
        ensure_first_admin()
        from core.backup import run_scheduled_backup
        try:
            run_scheduled_backup()
        except Exception:
            logging.exception('Scheduled backup failed')
        application = get_wsgi_application()
        server = make_server('127.0.0.1', PORT, application)
        threading.Timer(0.7, open_browser).start()
        logging.info('Clinita server started on port %s', PORT)
        server.serve_forever()
    except Exception:
        logging.exception('Clinita could not start')
        raise


if __name__ == '__main__':
    main()
