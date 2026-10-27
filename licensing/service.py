"""Offline, device-bound licensing helpers for the packaged application."""
import base64
import hashlib
import hmac
import json
import os
import platform
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


# This value is intentionally not stored with customer data.  The matching issuer
# secret is kept in the seller-only tool and must never be delivered to customers.
_VERIFY_KEY = b'DarmanSoft-v1|offline-license|replace-before-commercial-release'


def data_dir():
    root = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    folder = root / 'Clinita'
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def license_path():
    return data_dir() / 'license.dslic'


def machine_id():
    raw = '|'.join([platform.node(), platform.system(), platform.machine(), str(uuid.getnode())])
    return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()[:24]


def _canonical(payload):
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sign_payload(payload):
    return hmac.new(_VERIFY_KEY, _canonical(payload), hashlib.sha256).hexdigest()


def encode_license(payload):
    wrapped = {'payload': payload, 'signature': sign_payload(payload)}
    return base64.urlsafe_b64encode(json.dumps(wrapped, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode('ascii')


def decode_license(code):
    try:
        raw = base64.urlsafe_b64decode(code.strip().encode('ascii'))
        wrapped = json.loads(raw.decode('utf-8'))
        payload = wrapped['payload']
        signature = wrapped['signature']
    except (ValueError, KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('کد فعال‌سازی معتبر نیست.') from exc
    if not hmac.compare_digest(signature, sign_payload(payload)):
        raise ValueError('امضای کد فعال‌سازی معتبر نیست.')
    if payload.get('machine_id') != machine_id():
        raise ValueError('این کد برای دستگاه دیگری صادر شده است.')
    expires_on = payload.get('expires_on')
    if expires_on and date.fromisoformat(expires_on) < date.today():
        raise ValueError('اعتبار این لایسنس پایان یافته است.')
    return payload


def current_license():
    if not license_path().exists():
        return None, 'لایسنس فعال‌سازی نشده است.'
    try:
        return decode_license(license_path().read_text(encoding='utf-8')), ''
    except (OSError, ValueError) as exc:
        return None, str(exc)


def activate(code, *, required_plan=None, require_expiry=False, demo_days=None):
    payload = decode_license(code)
    if required_plan and payload.get('plan') != required_plan:
        raise ValueError(f'این نسخه فقط با لایسنس {required_plan} فعال می‌شود.')
    if demo_days is not None:
        payload = dict(payload)
        payload['expires_on'] = (date.today() + timedelta(days=demo_days)).isoformat()
        code = encode_license(payload)
    if require_expiry and not payload.get('expires_on'):
        raise ValueError('این لایسنس باید تاریخ انقضا داشته باشد.')
    license_path().write_text(code.strip(), encoding='utf-8')
    return payload


def _trial_marker_path():
    return data_dir() / 'demo-trial.json'


def _trial_signature(payload):
    return hmac.new(_VERIFY_KEY, _canonical(payload), hashlib.sha256).hexdigest()


def _registry_trial():
    """Read/write a second marker in HKCU; failure is handled safely."""
    try:
        import winreg
        key_path = r'Software\\DarmanSoft\\Demo'
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        try:
            started_at, _ = winreg.QueryValueEx(key, 'StartedAt')
            device, _ = winreg.QueryValueEx(key, 'MachineId')
            return {'started_at': started_at, 'machine_id': device}
        except FileNotFoundError:
            return None
        finally:
            winreg.CloseKey(key)
    except OSError:
        return None


def _write_registry_trial(payload):
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\\DarmanSoft\\Demo')
        winreg.SetValueEx(key, 'StartedAt', 0, winreg.REG_SZ, payload['started_at'])
        winreg.SetValueEx(key, 'MachineId', 0, winreg.REG_SZ, payload['machine_id'])
        winreg.CloseKey(key)
    except OSError:
        pass


def demo_trial_status(hours=72):
    """Return automatic demo availability, device-bound for a short period."""
    marker_path = _trial_marker_path()
    file_payload = None
    if marker_path.exists():
        try:
            wrapped = json.loads(marker_path.read_text(encoding='utf-8'))
            payload = wrapped['payload']
            if not hmac.compare_digest(wrapped['signature'], _trial_signature(payload)):
                return False, 'اطلاعات نسخه نمایشی معتبر نیست.'
            file_payload = payload
        except (OSError, KeyError, ValueError, json.JSONDecodeError):
            return False, 'اطلاعات نسخه نمایشی خوانده نشد.'

    registry_payload = _registry_trial()
    if file_payload is None and registry_payload is None:
        file_payload = {
            'machine_id': machine_id(),
            'started_at': datetime.now(timezone.utc).isoformat(),
        }
        marker_path.write_text(
            json.dumps({'payload': file_payload, 'signature': _trial_signature(file_payload)}, ensure_ascii=False),
            encoding='utf-8',
        )
        _write_registry_trial(file_payload)
        registry_payload = _registry_trial()
    elif file_payload is None or registry_payload is None:
        return False, 'اطلاعات زمان نسخه نمایشی تغییر کرده است.'

    if (
        file_payload.get('machine_id') != machine_id()
        or registry_payload.get('machine_id') != machine_id()
        or registry_payload.get('started_at') != file_payload.get('started_at')
    ):
        return False, 'این نسخه نمایشی برای دستگاه دیگری است یا اطلاعات آن تغییر کرده است.'
    try:
        started_at = datetime.fromisoformat(file_payload['started_at'])
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)
    except (KeyError, ValueError):
        return False, 'تاریخ شروع نسخه نمایشی معتبر نیست.'
    now = datetime.now(timezone.utc)
    if now < started_at - timedelta(minutes=5):
        return False, 'زمان سیستم به عقب تغییر کرده است.'
    remaining = started_at + timedelta(hours=hours) - now
    if remaining <= timedelta(0):
        return False, 'اعتبار سه‌روزه نسخه نمایشی پایان یافته است.'
    return True, remaining
