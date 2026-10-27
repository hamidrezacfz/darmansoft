from pathlib import Path

from django.contrib import messages
from django.shortcuts import redirect, render

from .backup import backup_database, default_backup_dir, load_settings, save_settings


def home(request):
    return render(request, 'core/home.html')


def backups(request):
    config = load_settings()
    if request.method == 'POST':
        try:
            if request.POST.get('action') == 'manual':
                archive = backup_database(request.POST.get('folder', '').strip() or None)
                messages.success(request, f'نسخه پشتیبان ساخته شد: {archive.name}')
            else:
                folder = Path(request.POST.get('folder', '').strip() or default_backup_dir()).expanduser().resolve()
                folder.mkdir(parents=True, exist_ok=True)
                save_settings({'enabled': request.POST.get('enabled') == 'on', 'interval_days': max(1, int(request.POST.get('interval_days', 1))), 'folder': str(folder)})
                messages.success(request, 'تنظیمات بکاپ خودکار ذخیره شد.')
        except (OSError, ValueError) as exc:
            messages.error(request, f'عملیات انجام نشد: {exc}')
        return redirect('backups')
    folder = Path(config['folder'])
    archives = sorted(folder.glob('DarmanSoft-backup-*.zip'), key=lambda item: item.stat().st_mtime, reverse=True)[:8] if folder.exists() else []
    return render(request, 'core/backups.html', {'config': config, 'archives': archives})

# Create your views here.
