# Convierte las tablas de datos de QuestieDB (Forever) a JSON SIN ejecutar código:
# un lector propio que solo entiende literales Lua (tablas, cadenas, números, nil, true/false).
import sys, json, os, re

src, out = sys.argv[1], sys.argv[2]

TOKEN = re.compile(r'''
   (?P<ws>\s+|--[^\n]*)
 | (?P<str>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')
 | (?P<num>-?\d+\.?\d*(?:[eE][-+]?\d+)?)
 | (?P<word>[A-Za-z_][A-Za-z0-9_]*)
 | (?P<sym>[{}\[\]=,;])
''', re.X)

ESC = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', "'": "'"}
def unq(s):
    body = s[1:-1]
    return re.sub(r'\\(.)', lambda m: ESC.get(m.group(1), m.group(1)), body)

def tokenize(text):
    pos, n = 0, len(text)
    toks = []
    while pos < n:
        m = TOKEN.match(text, pos)
        if not m:
            raise ValueError('carácter inesperado en %d: %r' % (pos, text[pos:pos+40]))
        pos = m.end()
        k = m.lastgroup
        if k == 'ws': continue
        v = m.group(k)
        if k == 'str': toks.append(('v', unq(v)))
        elif k == 'num': toks.append(('v', float(v) if ('.' in v or 'e' in v.lower()) else int(v)))
        elif k == 'word':
            if v == 'nil': toks.append(('v', None))
            elif v == 'true': toks.append(('v', True))
            elif v == 'false': toks.append(('v', False))
            else: toks.append(('w', v))
        else: toks.append(('s', v))
    return toks

def parse(toks):
    i = 0
    def value():
        nonlocal i
        t = toks[i]
        if t == ('s', '{'):
            return table()
        if t[0] == 'v':
            i += 1
            return t[1]
        raise ValueError('token inesperado %r' % (t,))
    def table():
        nonlocal i
        i += 1  # {
        arr, d, idx = {}, {}, 1
        while toks[i] != ('s', '}'):
            if toks[i] == ('s', '['):
                i += 1
                k = value()
                assert toks[i] == ('s', ']'); i += 1
                assert toks[i] == ('s', '='); i += 1
                d[k] = value()
            elif toks[i][0] == 'w' and toks[i+1] == ('s', '='):
                k = toks[i][1]; i += 2
                d[k] = value()
            else:
                arr[idx] = value(); idx += 1
            if toks[i] in (('s', ','), ('s', ';')): i += 1
        i += 1  # }
        if not d:
            # lista posicional (puede tener nils): la guardamos como lista
            return [arr[k] for k in range(1, idx)]
        for k, v in arr.items(): d[k] = v
        return d
    return value()

def load_block(path, marker):
    txt = open(path, encoding='utf-8').read()
    i = txt.index(marker)
    j = txt.index('[[', i) + 2
    k = txt.index(']]', j)
    body = txt[j:k].strip()
    assert body.startswith('return')
    return parse(tokenize(body[len('return'):]))

def pad(row, n):
    row = list(row) if isinstance(row, list) else [row.get(i) for i in range(1, n + 1)]
    return row + [None] * (n - len(row))

def jsonable(o):
    if isinstance(o, dict): return {str(k): jsonable(v) for k, v in o.items()}
    if isinstance(o, list): return [jsonable(v) for v in o]
    return o

jobs = [
    ('quests', 'foreverQuestDB.lua', 'QuestieDB.questData', 36),
    ('npcs', 'foreverNpcDB.lua', 'QuestieDB.npcData', 15),
    ('objects', 'foreverObjectDB.lua', 'QuestieDB.objectData', 7),
    ('items', 'foreverItemDB.lua', 'QuestieDB.itemData', 15),
]
os.makedirs(out, exist_ok=True)
import shutil
if os.path.exists(os.path.join(src, 'conversion.json')):
    shutil.copy(os.path.join(src, 'conversion.json'), os.path.join(out, 'conversion.json'))
for name, f, marker, n in jobs:
    d = load_block(os.path.join(src, f), marker)
    d = {str(k): jsonable(pad(v, n)) for k, v in d.items()}
    json.dump(d, open(os.path.join(out, name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print(name, len(d))

for t in ('lookupQuests', 'lookupNpcs', 'lookupObjects'):
    merged = {}
    for pre in ('es_', 'tr_'):
        p = os.path.join(src, pre + t + '.lua')
        if os.path.exists(p):
            merged.update({str(k): jsonable(v) for k, v in load_block(p, 'loadstring(').items()})
    json.dump(merged, open(os.path.join(out, 'es_' + t + '.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    print('es', t, len(merged))
