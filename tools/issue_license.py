"""Seller-only helper: issue an offline, device-bound درمان‌سافت activation code.

Example:
  .venv\\Scripts\\python tools\\issue_license.py --machine-id ABCD... --customer "نام مشتری" --plan pro
"""
import argparse
import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path(__file__).resolve().with_name('license-registry.csv')
sys.path.insert(0, str(ROOT))

from licensing.service import encode_license  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description='صدور کد فعال‌سازی درمان‌سافت')
    parser.add_argument('--machine-id', required=True, help='کد دستگاهی که مشتری ارسال کرده است')
    parser.add_argument('--customer', default='', help='نام مشتری یا مرکز')
    parser.add_argument('--plan', choices=('demo', 'base', 'support', 'custom'), default='base', help='نوع پکیج')
    parser.add_argument('--expires-on', default='', help='تاریخ انقضا میلادی، مانند 2027-10-18؛ خالی یعنی دائمی')
    args = parser.parse_args()
    if args.expires_on:
        date.fromisoformat(args.expires_on)
    if args.plan == 'demo' and not args.expires_on:
        parser.error('لایسنس demo باید تاریخ انقضا داشته باشد.')
    payload = {
        'product': 'DarmanSoft',
        'machine_id': args.machine_id.strip().upper(),
        'customer': args.customer.strip(),
        'plan': args.plan,
        'expires_on': args.expires_on,
        'issued_on': date.today().isoformat(),
    }
    code = encode_license(payload)
    registry_exists = REGISTRY_PATH.exists()
    with REGISTRY_PATH.open('a', newline='', encoding='utf-8-sig') as registry:
        writer = csv.DictWriter(
            registry,
            fieldnames=['issued_on', 'customer', 'plan', 'expires_on', 'machine_id', 'activation_code'],
        )
        if not registry_exists:
            writer.writeheader()
        writer.writerow({
            'issued_on': payload['issued_on'],
            'customer': payload['customer'],
            'plan': payload['plan'],
            'expires_on': payload['expires_on'],
            'machine_id': payload['machine_id'],
            'activation_code': code,
        })
    print(code)
    print(f'REGISTRY_SAVED: {REGISTRY_PATH}')


if __name__ == '__main__':
    main()
