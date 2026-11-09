# Utilidades de consulta sobre los JSON de QuestieDB Forever
import json, os, sys, re
J = os.environ.get("QDB_JSON", os.path.join(os.path.dirname(__file__), "..", "questie", "json"))
def L(n): return json.load(open(os.path.join(J, n + '.json'), encoding='utf-8'))
Q, N, O, I = L('quests'), L('npcs'), L('objects'), L('items')
EQ, EN, EO = L('es_lookupQuests'), L('es_lookupNpcs'), L('es_lookupObjects')
_cp = os.path.join(J, 'conversion.json')
if not os.path.exists(_cp): _cp = os.path.join(J, '..', 'fdata', 'conversion.json')
conv = json.load(open(_cp, encoding='utf-8'))
AREA2UI = {}
for t in conv['geometry']['transforms']:
    AREA2UI.setdefault(t['area_id'], t['ui_map_id'])
AREA2NAME = {t['area_id']: t['target_name'] for t in conv['geometry']['transforms']}

HUMAN = 1
def alliance_ok(q):
    r = q[5]
    if r in (None, 0): return True
    return bool(int(r) & HUMAN)

def qname(qid):
    e = EQ.get(str(qid))
    es = e[0] if isinstance(e, list) and e else None
    q = Q.get(str(qid))
    return (q[0] if q else None), es

def npc_name(nid):
    e = EN.get(str(nid))
    es = (e[0] if isinstance(e, list) else e) if e else None
    n = N.get(str(nid))
    return (n[0] if n else None), es

def obj_name(oid):
    e = EO.get(str(oid))
    es = (e[0] if isinstance(e, list) else e) if e else None
    o = O.get(str(oid))
    return (o[0] if o else None), es

def spawns_of(kind, eid):
    if kind == 'npc':
        n = N.get(str(eid)); sp = n and n[6]
    else:
        o = O.get(str(eid)); sp = o and o[3]
    return sp or {}

def centroid(pts):
    # centro aproximado: media del grupo más grande (para no caer entre dos campamentos)
    if not pts: return None
    pts = [p for p in pts if isinstance(p, list) and len(p) >= 2 and p[0] >= 0]
    if not pts: return None
    best = None
    for p in pts:
        grp = [q for q in pts if abs(q[0]-p[0]) < 6 and abs(q[1]-p[1]) < 6]
        if best is None or len(grp) > len(best): best = grp
    x = sum(p[0] for p in best) / len(best); y = sum(p[1] for p in best) / len(best)
    return round(x, 1), round(y, 1)

def loc(kind, eid, prefer_area=None):
    sp = spawns_of(kind, eid)
    if not sp: return None
    keys = list(sp.keys())
    area = None
    if prefer_area and str(prefer_area) in sp: area = str(prefer_area)
    else: area = max(keys, key=lambda k: len(sp[k]))
    c = centroid(sp[area])
    if not c: return None
    a = int(area)
    return a, AREA2UI.get(a), c[0], c[1]

def starters(qid):
    q = Q[str(qid)]
    s = q[1] or []
    out = []
    if len(s) > 0 and s[0]: out += [('npc', x) for x in s[0]]
    if len(s) > 1 and s[1]: out += [('obj', x) for x in s[1]]
    if len(s) > 2 and s[2]: out += [('item', x) for x in s[2]]
    return out

def enders(qid):
    q = Q[str(qid)]
    s = q[2] or []
    out = []
    if len(s) > 0 and s[0]: out += [('npc', x) for x in s[0]]
    if len(s) > 1 and s[1]: out += [('obj', x) for x in s[1]]
    return out

def desc(qid):
    q = Q.get(str(qid))
    if not q: return 'NO EXISTE %s' % qid
    en, es = qname(qid)
    st = starters(qid); en_ = enders(qid)
    def fmt(lst):
        r = []
        for k, e in lst:
            if k == 'item': r.append('item %s' % e); continue
            nm = npc_name(e) if k == 'npc' else obj_name(e)
            l = loc(k, e, q[16])
            r.append('%s/%s %s' % (nm[1] or nm[0], e, l))
        return '; '.join(r)
    return '%s | %s | %s | req%s lvl%s zone%s | ini: %s | fin: %s | pre:%s/%s next:%s' % (
        qid, en, es, q[3], q[4], q[16], fmt(st), fmt(en_), q[11], q[12], q[21])

def objective_loc(qid):
    """Ubicación aproximada de los objetivos: bichos, objetos, objetos que sueltan bichos."""
    q = Q[str(qid)]
    zone = q[16]
    ob = q[9] or []
    cands = []
    def get(i): return ob[i] if isinstance(ob, list) and len(ob) > i else None
    for c in (get(0) or []):
        cands.append(('npc', c[0]))
    for c in (get(1) or []):
        cands.append(('obj', c[0]))
    for c in (get(2) or []):
        it = I.get(str(c[0]))
        if it:
            for nid in (it[1] or [])[:6]: cands.append(('npc', nid))
            for oid in (it[2] or [])[:6]: cands.append(('obj', oid))
    for c in (get(4) or []):
        base = c[1] if len(c) > 1 else None
        if base: cands.append(('npc', base))
    trig = q[8]
    if trig and isinstance(trig, list) and len(trig) > 1 and isinstance(trig[1], dict):
        for a, pts in trig[1].items():
            cc = centroid(pts)
            if cc: return int(a), AREA2UI.get(int(a)), cc[0], cc[1], 'trigger'
    for k, e in cands:
        l = loc(k, e, zone)
        if l: return l + ((npc_name(e) if k == 'npc' else obj_name(e))[1] or (npc_name(e) if k == 'npc' else obj_name(e))[0],)
    return None

if __name__ == '__main__':
    for a in sys.argv[1:]:
        print(desc(int(a)))
