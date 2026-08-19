#!/usr/bin/env python3
"""Rebuild NextBillion route-planner report HTML files from template-v2.
Fetches each shared solution from the public API and embeds it in the template.
Usage: python3 build_reports.py   (writes ./out/{request_id}.html)
"""
import json, os, urllib.request

RAW = 'https://raw.githubusercontent.com/mbsoft/pt-fleet-sizing/main/'
TPL_TITLE = 'PT tactical fleet sizing'
TPL_SOLUTION_ID = '994dc69b159c1159e8e39d02740f0cb1'
API = 'https://bff.nextbillion.ai/route-planner-api/v1/shared-solutions/'

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'report-builder'})
    return urllib.request.urlopen(req, timeout=60).read()

tpl = get(RAW + 'template-v2.html').decode('utf-8')
ids = get(RAW + 'ids.txt').decode('utf-8').split()
OPEN = '<script id="nb-data" type="application/json">'
i = tpl.index(OPEN) + len(OPEN)
j = tpl.index('</' + 'script>', i)
head0, tail0 = tpl[:i], tpl[j:]

os.makedirs('out', exist_ok=True)
ok, errs = 0, []
for rid in ids:
    try:
        data = json.loads(get(API + rid))
        desc = data.get('description') or rid
        head = head0.replace(TPL_TITLE, desc).replace(TPL_SOLUTION_ID, rid)
        tail = tail0.replace(TPL_TITLE, desc).replace(TPL_SOLUTION_ID, rid)
        body = json.dumps(data).replace('<', '\\u003c')
        with open('out/%s.html' % rid, 'w', encoding='utf-8') as f:
            f.write(head + body + tail)
        ok += 1
        if ok % 25 == 0:
            print('built %d/%d' % (ok, len(ids)), flush=True)
    except Exception as e:
        errs.append('%s %s' % (rid, e))
print('DONE ok=%d errors=%d' % (ok, len(errs)))
for e in errs:
    print('ERR', e)
