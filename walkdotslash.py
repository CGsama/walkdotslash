import functools
import os
import json
import time
import pathlib
from datetime import datetime, timezone
from tqdm import tqdm
import hashlib
import re

fn = f".walkdotslash/{int(time.time())}"
pathlib.Path('.walkdotslash').mkdir(parents=True, exist_ok=True)

a = os.walk(".")
b = []
c = []
while True:
    try:
        i = next(a)
        num = 0
        dn = i[0].replace('\\', '/') + '/'
        for j in i[2]:
            c.append(dn + j)
            num += 1
        b.append([dn, num])
        print(f"{dn} ({num})")
    except StopIteration:
        break

with open(fn + "-directory.json", 'w', encoding='utf8') as json_file:
    json.dump(b, json_file, indent=2, ensure_ascii=False)

c = set(c)

prevs = os.listdir(".walkdotslash")
prevs.sort()
prev = 0
for i in prevs:
    if re.compile("(\d+)-simple.json").match(i):
        if prev < int(re.compile("(\d+)-simple.json").match(i)[1]):
            prev = int(re.compile("(\d+)-simple.json").match(i)[1])
if prev:
    with open(f".walkdotslash/{prev}-simple.json", 'r', encoding='utf8') as json_data:
        prev = set(json.load(json_data))

    delta_add = list(c - prev)
    delta_del = list(prev - c)
    delta_int = list(prev & c)
    delta_add.sort()
    delta_del.sort()
    delta_int.sort()

    with open(fn + "-delta.json", 'w', encoding='utf8') as json_file:
        json.dump({"add":delta_add,"del":delta_del}, json_file, indent=2, ensure_ascii=False)


c = list(c)
c.sort()

with open(fn + "-simple.json", 'w', encoding='utf8') as json_file:
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
with open(fn + "-datesize.json", 'w', encoding='utf8') as json_file:
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
with tqdm(total = total_size, unit = unit[scale], bar_format = '{percentage:3.0f}% {bar} {n:.2f}/{total:.2f} ' + unit[scale] +' [{elapsed}<{remaining}, {rate_noinv_fmt}, {rate_inv_fmt})]') as pbar:
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

with open(fn + "-sha1.json", 'w', encoding='utf8') as json_file:
    json.dump(e, json_file, indent=2, ensure_ascii=False)

prev = 0
for i in prevs:
    if re.compile("(\d+)-sha1.json").match(i):
        if prev < int(re.compile("(\d+)-sha1.json").match(i)[1]):
            prev = int(re.compile("(\d+)-sha1.json").match(i)[1])
if prev:
    with open(f".walkdotslash/{prev}-sha1.json", 'r', encoding='utf8') as json_data:
        prev = json.load(json_data)

    prevd = {}
    for i in prev:
        prevd[i[0]] = i[3]

    ed = {}
    for i in e:
        ed[i[0]] = i[3]

    delta_mod = []

    for i in delta_int:
        if prevd[i] != ed[i]:
            delta_mod.append(i)

    delta_mod = list(set(delta_mod))
    delta_mod.sort()

    with open(fn + "-delta.json", 'w', encoding='utf8') as json_file:
        json.dump({"add":delta_add,"del":delta_del,"mod":delta_mod}, json_file, indent=2, ensure_ascii=False)
