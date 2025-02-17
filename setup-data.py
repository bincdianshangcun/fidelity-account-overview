#!/usr/bin/env python


from pathlib import Path
from datetime import datetime


path_data = Path(__file__).parent / 'data'
path_current = path_data / 'current'
path_downloads = Path('~/Downloads').expanduser()

candidates = []
for p in path_downloads.glob('Portfolio_Positions_*.csv'):
    candidates.append((p, p.stat().st_mtime))

candidates.sort(key=lambda p:p[1], reverse=True)

# Portfolio_Positions_Feb-17-2025.csv
today = datetime.today().date().strftime('%b-%d-%Y')
print(today)

latest_csv_path:Path = None
for p,_ in candidates:
    if today in p.stem:
        latest_csv_path = p
        break

if not latest_csv_path:
    print('no file found, nothing changed')
    exit(1)

print(f'file found {p}')
target = latest_csv_path.replace(path_data / latest_csv_path.name)
print(f'moved to {target}')

path_current.unlink(missing_ok=True)
path_current.symlink_to(target=target)
print(f'{path_current} symlink to {target}')

print('Success.')



