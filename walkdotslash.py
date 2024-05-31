import functools
import os
import json
import time
import pathlib
from datetime import datetime, timezone
from tqdm import tqdm
import hashlib

a = os.walk(".")
b = []
while True:
    try:
        i = next(a)
        num = 0
        dn = i[0].replace('\\', '/') + '/'
        for j in i[2]:
            b.append(dn + j)
            num += 1
        print(f"{dn} ({num})")
    except StopIteration:
        break
b = set(b)
c = list(b)
c.sort()
fn = f".walkdotslash/{int(time.time())}.json"
pathlib.Path('.walkdotslash').mkdir(parents=True, exist_ok=True) 
with open(fn, 'w', encoding='utf8') as json_file:
    json.dump(c, json_file, indent=2, ensure_ascii=False)

d = []
total_size = 0
for i in tqdm(c):
    try:
        stat = pathlib.Path(i).stat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        total_size += stat.st_size
        d.append([i, stat.st_size, modified.isoformat()])
    except:
        d.append([i, 0, "error"])
with open(fn, 'w', encoding='utf8') as json_file:
    json.dump(d, json_file, indent=2, ensure_ascii=False)

scale = 0
while total_size >= 2000:
    total_size /= 1024
    scale += 1
unit = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

"""
def getRate(num):
    rate_scale = scale
    while num < 1 and rate_scale >= 0:
        num *= 1024
        rate_scale -= 1
    return f"{num}{unit[rate_scale]/s}"
"""
      
e = []
with tqdm(total = total_size, unit = unit[scale], bar_format = '{percentage:3.0f}% {bar} {n:.2f}/{total:.2f} [{elapsed}<{remaining}, {rate_noinv_fmt}, {rate_inv_fmt})]') as pbar:
    for i in d:
        try:
            file_hash = hashlib.sha1()
            with open(i[0], "rb") as f:
                while chunk := f.read(8192):
                    update_size = len(chunk) / 1024 ** scale
                    pbar.update(update_size)
                    file_hash.update(chunk)
            e.append([i[0], i[1], i[2], file_hash.hexdigest()])
        except:
            e.append([i[0], i[1], i[2], "error"])
        #pbar.update(i[1])

with open(fn, 'w', encoding='utf8') as json_file:
    json.dump(d, json_file, indent=2, ensure_ascii=False)
