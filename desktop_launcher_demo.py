"""Launcher for the separately packaged, time-limited DarmanSoft demo."""
import os

os.environ['DARMANSOFT_EDITION'] = 'demo'
os.environ['CLINITA_PORT'] = '8002'

from desktop_launcher import main


if __name__ == '__main__':
    main()
