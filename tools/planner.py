# Genera las rutas de ForeverAlliance&Horde a partir de los datos de Forever de QuestieDB.
#
#   QDB_JSON=<carpeta_json> py -I tools/planner.py alianza
#   QDB_JSON=<carpeta_json> py -I tools/planner.py horda
#
# Cada facción genera Data_Ruta_<Facción>.lua y Data_Misiones_<Facción>.lua en la carpeta del addon.
# Los pasos de una misión de clase llevan cl="CLASE": en el juego solo los ve esa clase.
#
# CÓMO AÑADIR COSAS
#   - Otra clase: escribe sus bloques (funciones como pal12 o mage10) y añádelos a 'clases' de su facción.
#   - Otra raza: añade su máscara a 'razas', y su zona de inicio al principio de 'plan'
#     (o crea una facción/ruta nueva en RUTAS y regístrala en GF.RutaMeta de Core.lua).
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qdb
from qdb import Q, N, O, EQ

ADDON = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Zonas y ciudades (areaID de QuestieDB)
# ---------------------------------------------------------------------------
SW, IF = 1519, 1537
UC, ORG = 1497, 1637
ELWYNN, WESTFALL, DUNMOROGH, LOCH = 12, 40, 1, 38
DEATHKNELL, TIRISFAL, SILVERPINE = 154, 85, 130
CLASS_MASK = {'WARRIOR': 1, 'PALADIN': 2, 'HUNTER': 4, 'ROGUE': 8, 'PRIEST': 16, 'SHAMAN': 64, 'MAGE': 128, 'WARLOCK': 256, 'DRUID': 1024}

# ---------------------------------------------------------------------------
# Estado de la simulación
# ---------------------------------------------------------------------------
done, excluded = set(), set()
steps = []
CUR = {'cl': None}          # clase del bloque que se está escribiendo (None = para todos)
sim = {'lvl': 1, 'xp': 0}
CFG = {}

XP_FILES = [os.path.join(qdb.J, 'xpDB.lua'), os.path.join(qdb.J, 'xpTr.lua')]
QXP = {}
for f in XP_FILES:
    if os.path.exists(f):
        for m in re.finditer(r'\[(\d+)\]\s*=\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}', open(f, encoding='utf-8').read()):
            QXP[int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
# XP necesaria para pasar de nivel N a N+1 (Classic)
XP_LEVEL = [0, 400, 900, 1400, 2100, 2800, 3600, 4500, 5400, 6500, 7600, 8800, 10100, 11400, 12900, 14400,
            16000, 17700, 19400, 21300, 23200, 25200, 27300, 29400, 31700, 34000, 36400, 38900, 41400, 44300,
            47400, 50800, 54500, 58600, 62800, 67100, 71600, 76100, 80800, 85700, 90700, 95800, 101000, 106300,
            111800, 117500, 123200, 129100, 135100, 141200, 147500, 153900, 160400, 167100, 173900, 180800,
            187900, 195000, 202300, 209800]
RED = int(os.environ.get('RED', '4'))   # niveles por encima del tuyo que se aceptan

def gain(qid):
    if sim['lvl'] >= 60: return
    lv, xp = QXP.get(qid, (None, None))
    if xp is None:
        q = Q.get(str(qid)); lv = (q and q[4]) or sim['lvl']; xp = 0
    diff = sim['lvl'] - (lv or sim['lvl'])
    mult = 1.0 if diff <= 5 else {6: 0.8, 7: 0.6, 8: 0.4, 9: 0.2}.get(diff, 0.1)
    sim['xp'] += xp * mult * CFG['kill']
    while sim['lvl'] < 60 and sim['xp'] >= XP_LEVEL[sim['lvl']]:
        sim['xp'] -= XP_LEVEL[sim['lvl']]
        sim['lvl'] += 1

def L(): return sim['lvl']

def lua_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ') + '"'

def es_name(qid):
    en, es = qdb.qname(qid)
    return es or en or ('Misión %d' % qid)

def es_obj(qid):
    e = EQ.get(str(qid))
    t = None
    if isinstance(e, list) and len(e) > 1 and e[1]:
        t = e[1][0] if isinstance(e[1], list) else e[1]
    if not t:
        ot = Q[str(qid)][7]
        t = ot[0] if isinstance(ot, list) and ot else None
    if not t: return ''
    t = t.replace('$B', ' ').replace('$b', ' ')
    return (t[:150] + '...') if len(t) > 150 else t

def npc_es(kind, eid):
    nm = qdb.npc_name(eid) if kind == 'npc' else qdb.obj_name(eid)
    return nm[1] or nm[0] or '?'

def ent_where(kind, eid, area):
    """(mapa UI, (x, y)) del PNJ/objeto en la zona o en una zona vecina permitida (near)."""
    if kind == 'item': return None
    area = CFG['spawn_area'].get(area, area)
    sp = qdb.spawns_of(kind, eid)
    for a in [area] + CFG['near'].get(area, []):
        if str(a) in sp:
            c = qdb.centroid(sp[str(a)])
            if c: return qdb.AREA2UI.get(a), c
    return None

def ent_loc(kind, eid, area):
    w = ent_where(kind, eid, area)
    return w and w[1]

# Correcciones de QuestieDB (classicQuestFixes) que no vienen en los datos exportados de Forever
QFIX = {
  1960: {'pre': None},   # «Investiga la tienda de alquimia»: 1959 es solo de enlace
  1882: {'pre': None},   # «La Hacienda Balnir»: 1881 es solo de enlace
}

def pre_single(qid):
    fx = QFIX.get(qid, {})
    return fx['pre'] if 'pre' in fx else Q[str(qid)][12]

def unlocked(qid):
    q = Q[str(qid)]
    single = pre_single(qid)
    group = q[11]
    if single and not any(p in done for p in single): return False
    if group and not all(p in done for p in group): return False
    return True

def usable(qid, area):
    q = Q[str(qid)]
    extra = qid in CFG['extra'].get(area, [])
    sa = CFG['spawn_area'].get(area, area)
    if qid in done or qid in excluded or qid in CFG['skip_in'].get(area, []): return False
    if q[16] != area and not extra: return False
    if not qdb.race_ok(q, CFG['race_mask']): return False
    if q[6] not in (None, 0):                        # misión de clase: solo si está en la tabla classq
        cl = CFG['classq'].get(qid)
        if not cl or not (int(q[6]) & CLASS_MASK[cl]): return False
    if q[17] or q[18] or q[19] or q[29] or q[30]: return False   # profesión / reputación / hechizo / especialización
    if q[23] and int(q[23]) & 3: return False        # repetible / evento
    if q[26]: return False                           # breadcrumb (viene de otra zona)
    st = [s for s in qdb.starters(qid) if s[0] != 'item']
    en = qdb.enders(qid)
    if not st or not en: return False
    if not ent_loc(st[0][0], st[0][1], area): return False
    if not ent_loc(en[0][0], en[0][1], area): return False
    if st[0][0] == 'npc':
        f = N[str(st[0][1])][12]
        if f and CFG['npc_faction'] not in f: return False   # PNJ de la otra facción
    ol = qdb.objective_loc(qid)
    if ol and ol[0] not in [sa] + CFG['near'].get(sa, []): return False   # objetivos en mazmorra / otra zona
    return True

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def nn_order(items, pos):
    out, items = [], list(items)
    while items:
        items.sort(key=lambda it: dist(it[0], pos))
        it = items.pop(0)
        out.append(it)
        pos = it[0]
    return out, pos

def add(t, txt, q=None, lv=None, ui=None, xy=None, tip=None, cl=None):
    steps.append(dict(t=t, txt=txt, q=q, lv=lv, m=ui, x=xy and xy[0], y=xy and xy[1], tip=tip, cl=cl or CUR['cl']))

def ui_of(area):
    return qdb.AREA2UI.get(CFG['spawn_area'].get(area, area))

def plan_zone(area, lo, hi, travel):
    ui = ui_of(area)
    pool = [int(k) for k, q in Q.items() if q[16] == area] + CFG['extra'].get(area, [])
    pool = [k for k in pool if usable(k, area)]
    if not pool: return
    if L() < lo:
        add('level', 'Antes de ir: sube a nivel %d (mata bichos en tu zona actual, haz una mazmorra o termina misiones pendientes del panel de Progreso).' % lo, lv=lo)
        sim['lvl'], sim['xp'] = lo, 0
    add('go', travel, lv=L(), ui=ui, xy=None)
    active = []
    pos = None
    rounds = grinds = 0
    while rounds < 30:
        rounds += 1
        emit_class_blocks(inzone=True)
        avail = []
        for k in pool:
            if k in done or k in excluded or k in active: continue
            q = Q[str(k)]
            if not unlocked(k): continue
            if (q[3] or 1) > L(): continue                       # nivel requerido EXACTO
            if (q[4] or q[3] or 1) > L() + RED: continue          # demasiado roja todavía
            if (q[4] or 1) < L() - 7: continue                   # gris: casi no da experiencia
            if q[31] and q[31] < L(): continue                   # nivel máximo superado
            avail.append(k)
        avail = avail[: max(0, 18 - len(active))]
        if not avail and not active:
            # ¿Quedan misiones de la zona a 1-2 niveles? Entonces se sube matando bichos aquí mismo.
            left = [(Q[str(k)][3] or 1) for k in pool
                    if k not in done and k not in excluded and unlocked(k) and (Q[str(k)][3] or 1) <= min(hi, L() + 2)]
            if left and min(left) > L() and grinds < 3:
                grinds += 1
                add('level', 'Sube a nivel %d matando bichos de esta zona. Hay más misiones a ese nivel.' % min(left), lv=min(left))
                sim['lvl'], sim['xp'] = min(left), 0
                continue
            break
        # recoger
        items = []
        for k in avail:
            kind, eid = [s for s in qdb.starters(k) if s[0] != 'item'][0]
            m, xy = ent_where(kind, eid, area)
            items.append((xy, k, kind, eid, m))
        if pos is None and items:
            # hub = punto con más dadores alrededor
            pos = max((it[0] for it in items), key=lambda p: sum(1 for o in items if dist(o[0], p) < 4))
        order, pos = nn_order(items, pos or (50, 50))
        for xy, k, kind, eid, m in order:
            q = Q[str(k)]
            add('accept', 'Recoge «%s» de %s.' % (es_name(k), npc_es(kind, eid)), q=k, lv=L(), ui=m, xy=xy, cl=CFG['classq'].get(k))
            for ex in (q[15] or []): excluded.add(ex)
            active.append(k)
        # hacer objetivos
        items = []
        for k in active:
            ol = qdb.objective_loc(k)
            if ol and ol[2] is not None:
                items.append(((ol[2], ol[3]), k, ol))
        order, pos = nn_order(items, pos)
        for xy, k, ol in order:
            obj = es_obj(k)
            where = (' (%s)' % ol[4]) if len(ol) > 4 and isinstance(ol[4], str) and ol[4] != 'trigger' else ''
            add('do', 'Haz «%s»%s: %s' % (es_name(k), where, obj), q=k, lv=L(), ui=ol[1] or ui, xy=xy, cl=CFG['classq'].get(k))
        # entregar
        items = []
        for k in active:
            kind, eid = qdb.enders(k)[0]
            m, xy = ent_where(kind, eid, area)
            items.append((xy, k, kind, eid, m))
        order, pos = nn_order(items, pos)
        for xy, k, kind, eid, m in order:
            add('turnin', 'Entrega «%s» a %s.' % (es_name(k), npc_es(kind, eid)), q=k, lv=L(), ui=m, xy=xy, cl=CFG['classq'].get(k))
            done.add(k)
            if k not in CFG['classq']: gain(k)
        active = []
    add('level', 'Al terminar esta zona deberías estar en nivel %d. Si vas por debajo, mata bichos de la zona mientras recolectas.' % L(), lv=L())
    print('  zona %-5s fin nivel %2d (%.0f%%)' % (area, L(), 100 * sim['xp'] / XP_LEVEL[min(L(), 59)]))

def raw(t, txt, q=None, lv=None, area=None, kind=None, eid=None, tip=None, xy=None):
    # Las misiones de clase no suman experiencia a la simulación (la ruta es la misma para todas las clases)
    if t == 'turnin' and q: done.add(q)
    ui = ui_of(area) if area else None
    if xy is None and kind and area: xy = ent_loc(kind, eid, area)
    add(t, txt, q=q, lv=lv, ui=ui, xy=xy, tip=tip)

# ===========================================================================
# MISIONES DE CLASE · PALADÍN (Alianza)
# ===========================================================================
def pal12():
    add('note', 'MISIÓN DE CLASE nivel 12 (Libro de la Divinidad): te da REDENCIÓN (resucitar). Empieza en Villadorada.', lv=12)
    raw('accept', 'Villadorada (posada): recoge «Libro de la Divinidad» del Hermano Wilhelm.', q=2998, lv=12, area=ELWYNN, kind='npc', eid=927)
    raw('turnin', 'Ventormenta, Catedral de la Luz: entrega a Duthorian Rall.', q=2998, lv=12, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «El Libro de la Divinidad».', q=1641, lv=12, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Habla otra vez con Duthorian Rall para entregarla.', q=1641, lv=12, area=SW, kind='npc', eid=6171)
    raw('accept', 'Haz clic derecho en el libro que te ha dado Duthorian Rall (en tus bolsas) para empezar la siguiente misión.', q=1642, lv=12)
    raw('turnin', 'Entrégalo a Duthorian Rall.', q=1642, lv=12, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge el siguiente «El Libro de la Divinidad».', q=1643, lv=12, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Ventormenta (Ciudad Vieja): entrega a Stephanie Turner.', q=1643, lv=12, area=SW, kind='npc', eid=6174)
    raw('accept', 'Recoge su encargo (da 1 lino a un mendigo) de Stephanie Turner.', q=1644, lv=13, area=SW, kind='npc', eid=6174)
    raw('turnin', 'Entrega a Stephanie Turner.', q=1644, lv=13, area=SW, kind='npc', eid=6174)
    raw('accept', 'Recoge «Escrito sobre divinidad» de Stephanie Turner.', q=1780, lv=13, area=SW, kind='npc', eid=6174)
    raw('turnin', 'Vuelve a Duthorian Rall.', q=1780, lv=13, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge el siguiente libro de Duthorian Rall.', q=1781, lv=13, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrega a Gazin Tenorm (Catedral).', q=1781, lv=13, area=SW, kind='npc', eid=6173)
    raw('accept', 'Recoge «Escrito sobre divinidad» de Gazin Tenorm.', q=1786, lv=13, area=SW, kind='npc', eid=6173)
    raw('turnin', 'Elwynn (cerca de la mina de Jaspe): habla con Henze Faulk y usa el Símbolo de la Vida en él.', q=1786, lv=13, area=ELWYNN, kind='npc', eid=6172)
    raw('accept', 'Recoge «Libro de la Divinidad» de Henze Faulk.', q=1787, lv=13, area=ELWYNN, kind='npc', eid=6172)
    raw('turnin', 'Vuelve a Gazin Tenorm (Ventormenta).', q=1787, lv=13, area=SW, kind='npc', eid=6173)
    raw('accept', 'Recoge el último «Libro de la Divinidad».', q=1788, lv=13, area=SW, kind='npc', eid=6173)
    raw('turnin', 'Entrega a Duthorian Rall y aprende Redención.', q=1788, lv=13, area=SW, kind='npc', eid=6171)

def pal20():
    add('note', 'MISIÓN DE CLASE nivel 20 (Libro del valor): ve al instructor de paladines Duthorian Rall en la Catedral de la Luz (Ventormenta).', lv=20,
        tip='Recompensa: una gran arma o escudo. Merece la pena.')
    raw('accept', 'Recoge «Escrito sobre valor» de Duthorian Rall.', q=1793, lv=20, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégasela a Duthorian Rall.', q=1793, lv=20, area=SW, kind='npc', eid=6171)
    raw('accept', 'Haz clic derecho en el «Escrito sobre valor» que te ha dado (en tus bolsas).', q=1649, lv=20)
    raw('turnin', 'Entrégaselo a Duthorian Rall.', q=1649, lv=20, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «Libro del valor» (sigue la cadena).', q=1650, lv=23, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Páramos de Poniente (sur, junto a la costa): habla con Daphne Fontana.', q=1650, lv=23, area=WESTFALL, kind='npc', eid=6182)
    raw('accept', 'Recoge «Libro del valor»: defiéndela de los Defias.', q=1651, lv=25, area=WESTFALL, kind='npc', eid=6182,
        tip='Son 3 oleadas. Ve con nivel 22-24 o con un amigo.')
    raw('turnin', 'Entrega a Daphne Fontana.', q=1651, lv=25, area=WESTFALL, kind='npc', eid=6182)
    raw('accept', 'Recoge el siguiente «Libro del valor».', q=1652, lv=25, area=WESTFALL, kind='npc', eid=6182)
    raw('turnin', 'Vuelve a Duthorian Rall (Ventormenta).', q=1652, lv=25, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «La prueba de rectitud».', q=1653, lv=21, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Dun Morogh: habla con Jordan Fontana.', q=1653, lv=21, area=DUNMOROGH, kind='npc', eid=6181)
    raw('accept', 'Recoge «La prueba de rectitud» (materiales).', q=1654, lv=22, area=DUNMOROGH, kind='npc', eid=6181,
        tip='Necesitas: carga de Bailor (Loch Modan), madera de roble blanco y la gema Kor (Costa Oscura).')
    raw('accept', 'Loch Modan (Thelsamar): recoge «Envío de minerales de Bailor» de Bailor Petramano.', q=1655, lv=22, area=LOCH, kind='npc', eid=6241)
    raw('turnin', 'Entrega «Envío de minerales de Bailor» a Bailor Petramano.', q=1655, lv=22, area=LOCH, kind='npc', eid=6241)
    raw('turnin', 'Entrega los materiales a Jordan Fontana.', q=1654, lv=22, area=DUNMOROGH, kind='npc', eid=6181)
    raw('accept', 'Recoge la última «La prueba de rectitud» de Jordan Fontana.', q=1806, lv=22, area=DUNMOROGH, kind='npc', eid=6181)
    raw('turnin', 'Entrega «La prueba de rectitud» final y elige tu arma.', q=1806, lv=22, area=DUNMOROGH, kind='npc', eid=6181,
        tip='Elige el Martillo de Verigan (dos manos): ideal para Reprensión.')

def pal40():
    add('note', 'NIVEL 40: ¡MONTURA GRATIS! Misión de clase «Libro de la nobleza».', lv=40)
    raw('accept', 'Ventormenta: recoge «Libro de la nobleza» de Duthorian Rall.', q=1661, lv=40, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégala y aprende Invocar caballo de guerra.', q=1661, lv=40, area=SW, kind='npc', eid=6171,
        tip='Te ahorras ~100g. Ese oro guárdalo para la montura rápida de 60.')
    add('train', 'Entrena nivel 40 y activa la DOBLE ESPECIALIZACIÓN (50g): Reprensión + Sagrado o Protección.', lv=40)

def pal60():
    add('note', 'NIVEL 60: CORCEL (montura épica de paladín). Cadena larga y cara; empieza cuando tengas ~500g y un grupo para Scholomance.', lv=60)
    raw('accept', 'Ventormenta: recoge «Lord Grisillo Quiebrasombras» de Duthorian Rall.', q=7638, lv=60, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégala a Lord Grisillo Quiebrasombras (Catedral).', q=7638, lv=60, area=SW, kind='npc', eid=928)
    raw('accept', 'Recoge «Énfasis en el sacrificio».', q=7637, lv=60, area=SW, kind='npc', eid=928)
    add('note', 'Sigue la cadena del Corcel (Forjaz, Tierras de la Peste, Scholomance). Necesitas: Gualdrapa de arcanita, Cristal de adivinación y mucho oro.', lv=60)

# ===========================================================================
# MISIONES DE CLASE · MAGO (Horda / No-muerto)
# ===========================================================================
def mage10():
    add('note', 'MISIÓN DE CLASE nivel 10 (La Hacienda Balnir): te da un bastón o una túnica. Empieza en Rémol y se entrega en Entrañas.', lv=10)
    raw('accept', 'Rémol (posada, arriba): recoge «Habla con Anastasia» de Cain Pirosón.', q=1881, lv=10, area=TIRISFAL, kind='npc', eid=2128)
    raw('turnin', 'Entrañas, Barrio de los Magos: entrega a Anastasia Hartwell.', q=1881, lv=10, area=UC, kind='npc', eid=4568,
        tip='Entrañas está al oeste de Rémol: entra por las ruinas de Lordaeron y baja en el ascensor.')
    raw('accept', 'Recoge «La Hacienda Balnir» de Anastasia Hartwell.', q=1882, lv=10, area=UC, kind='npc', eid=4568)
    raw('do', 'Hacienda Balnir (este de Tirisfal): recoge las Bocas de dragón de Balnir (flores del huerto).', q=1882, lv=10, area=TIRISFAL, xy=(77.5, 61.9))
    raw('turnin', 'Vuelve a Entrañas: entrega a Anastasia Hartwell y elige recompensa.', q=1882, lv=11, area=UC, kind='npc', eid=4568)

def mage15():
    add('note', 'MISIÓN DE CLASE nivel 15 (Toga Fuegohechizo): una túnica muy buena para tu nivel. Necesitas 10 Lino: no lo vendas.', lv=15)
    raw('accept', 'Rémol: recoge «Preséntate ante Anastasia» de Cain Pirosón.', q=1959, lv=15, area=TIRISFAL, kind='npc', eid=2128,
        tip='Si Cain no te la ofrece, sáltala con >> y habla directamente con Anastasia en Entrañas.')
    raw('turnin', 'Entrañas, Barrio de los Magos: entrega a Anastasia Hartwell.', q=1959, lv=15, area=UC, kind='npc', eid=4568)
    raw('accept', 'Recoge «Investiga la tienda de alquimia» de Anastasia Hartwell.', q=1960, lv=15, area=UC, kind='npc', eid=4568)
    raw('do', 'Coge el Canto de manifestación y el Cofre de arcas de contención (detrás de Anastasia). Usa el Canto para revelar las Crías del risco y, cuando estén aturdidas, usa el cofre en ellas (3 arcas llenas).',
        q=1960, lv=15, area=UC, xy=(53.0, 74.7))
    raw('turnin', 'Entrega «Investiga la tienda de alquimia» a Anastasia Hartwell.', q=1960, lv=16, area=UC, kind='npc', eid=4568)
    raw('accept', 'Recoge «Recolección de materiales» de Anastasia Hartwell.', q=1961, lv=16, area=UC, kind='npc', eid=4568)
    raw('do', 'Consigue 10 Lino y 6 Gemas de maná de Dalaran: las sueltan los magos y aprendices de Dalaran en Molino Ámbar (Bosque de Argénteos, este).',
        q=1961, lv=16, area=SILVERPINE, xy=(60.3, 65.4), tip='Son nivel 15-20 y van en grupos: usa Polimorfia en uno y Nova de Escarcha si se te acercan.')
    raw('turnin', 'Entrañas, Barrio de los Magos: entrega los materiales a Josef Gregorian.', q=1961, lv=17, area=UC, kind='npc', eid=4576)
    raw('accept', 'Recoge «Toga Fuegohechizo» de Josef Gregorian.', q=1962, lv=17, area=UC, kind='npc', eid=4576)
    raw('turnin', 'Entrégala a Josef Gregorian y llévate la Toga Fuegohechizo.', q=1962, lv=17, area=UC, kind='npc', eid=4576)

def mage26():
    add('note', 'MISIÓN DE CLASE nivel 26 (Prendas de encaje abisal): Entrañas -> Orgrimmar -> Vallefresno -> El Cruce. Hazla cuando pases por Kalimdor.', lv=26)
    raw('accept', 'Entrañas: recoge «Habla con Deino» de Anastasia Hartwell.', q=1943, lv=26, area=UC, kind='npc', eid=4568)
    raw('turnin', 'Orgrimmar (Valle de los Espíritus): entrega a Deino.', q=1943, lv=26, area=ORG, kind='npc', eid=5885)
    raw('accept', 'Recoge «Aguas de Xavian» de Deino.', q=1944, lv=26, area=ORG, kind='npc', eid=5885)
    raw('do', 'Vallefresno, Xavian (campamento de sátiros del este): llena el vial y consigue la Muestra de agua de Xavian.', q=1944, lv=26)
    raw('turnin', 'Vuelve a Orgrimmar: entrega a Deino.', q=1944, lv=27, area=ORG, kind='npc', eid=5885)
    raw('accept', 'Recoge «Hermanas sonrientes» de Deino.', q=1945, lv=27, area=ORG, kind='npc', eid=5885)
    raw('do', 'Vallefresno: mata Hermanas sonrientes hasta tener 12 Cabellos.', q=1945, lv=27, area=331, xy=(59.9, 54.4))
    raw('turnin', 'Los Baldíos, El Cruce: entrega a Kil\'hala.', q=1945, lv=27, area=17, kind='npc', eid=3484)
    raw('accept', 'Recoge «Prendas de encaje abisal» de Kil\'hala.', q=1946, lv=27, area=17, kind='npc', eid=3484)
    raw('turnin', 'Entrégala a Kil\'hala y elige tu recompensa.', q=1946, lv=27, area=17, kind='npc', eid=3484)

def mage35():
    add('note', 'MISIÓN DE CLASE 30-40 (Varitas de mago): te da una VARITA a elegir. Orgrimmar -> Marjal Revolcafango -> Las Mil Agujas.', lv=36,
        tip='Tabetha (Marjal Revolcafango) también da «Objetos de poder» (1 jade + zarza electrificada): opcional.')
    raw('accept', 'Orgrimmar: recoge «Viaje al pantano» de Deino.', q=1947, lv=36, area=ORG, kind='npc', eid=5885)
    raw('turnin', 'Marjal Revolcafango (casa en el centro-oeste): entrega a Tabetha.', q=1947, lv=36, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «Secretos escondidos» de Tabetha.', q=1949, lv=36, area=15, kind='npc', eid=6546)
    raw('turnin', 'Las Mil Agujas, El Desierto de Sal (Llanos de Sal, sureste): entrega a Magus Tirth.', q=1949, lv=36, area=400, kind='npc', eid=6548)
    raw('accept', 'Recoge «Santo y seña» de Magus Tirth.', q=1950, lv=36, area=400, kind='npc', eid=6548,
        tip='La frase la sabe uno de los goblins del circuito de carreras de los Llanos de Sal. Habla con ellos.')
    raw('turnin', 'Entrega «Santo y seña» a Magus Tirth.', q=1950, lv=36, area=400, kind='npc', eid=6548)
    raw('accept', 'Recoge «Rituales de poder» de Magus Tirth.', q=1951, lv=36, area=400, kind='npc', eid=6548)
    raw('turnin', 'Vuelve al Marjal Revolcafango: entrega el libro a Tabetha.', q=1951, lv=37, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «Varitas de mago» de Tabetha.', q=1952, lv=37, area=15, kind='npc', eid=6546)
    raw('turnin', 'Espera a que termine el ritual y habla con Tabetha: elige tu varita.', q=1952, lv=37, area=15, kind='npc', eid=6546)

def mage40():
    add('train', 'Entrena nivel 40 (Portales: aprende el de Entrañas y Orgrimmar) y activa la DOBLE ESPECIALIZACIÓN (50g): Escarcha para subir + Fuego/Arcano para mazmorras.', lv=40,
        tip='Los portales dan dinero: la gente paga propina por un portal a su capital.')
    add('note', 'MISIÓN DE CLASE 35-40 (Poder celestial): da un objeto muy bueno pero necesita GRUPO para Uldaman. Si no tienes grupo, sáltala con >>.', lv=40)
    raw('accept', 'Entrañas: recoge «Regreso al pantano» de Anastasia Hartwell.', q=1953, lv=40, area=UC, kind='npc', eid=4568)
    raw('turnin', 'Marjal Revolcafango: entrega a Tabetha.', q=1953, lv=40, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «El orbe infernal» de Tabetha.', q=1954, lv=40, area=15, kind='npc', eid=6546)
    raw('do', 'Desolace (sureste): mata Invocadores Filo Ardiente hasta que suelten el Orbe infernal.', q=1954, lv=40, area=405, xy=(80.8, 78.5))
    raw('turnin', 'Entrega el orbe a Tabetha.', q=1954, lv=40, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «El exorcismo» de Tabetha.', q=1955, lv=40, area=15, kind='npc', eid=6546)
    raw('turnin', 'Mata al demonio que sale del orbe y habla con Tabetha.', q=1955, lv=40, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «Poder en Uldaman» de Tabetha.', q=1956, lv=40, area=15, kind='npc', eid=6546)
    raw('do', 'Uldaman (Tierras Inhóspitas, CON GRUPO): consigue una Fuente de poder obsidiano.', q=1956, lv=41)
    raw('turnin', 'Entrega la fuente de poder a Tabetha.', q=1956, lv=41, area=15, kind='npc', eid=6546)
    raw('accept', 'Recoge «Oleadas de maná» de Tabetha.', q=1957, lv=41, area=15, kind='npc', eid=6546)
    raw('turnin', 'Mata 12 Oleadas de maná antes de que acabe el tiempo y habla con Tabetha.', q=1957, lv=41, area=15, kind='npc', eid=6546,
        tip='Salen muchas a la vez: Nova de Escarcha + Ventisca/Explosión Arcana.')
    raw('accept', 'Recoge «Poder celestial» de Tabetha.', q=1958, lv=41, area=15, kind='npc', eid=6546)
    raw('turnin', 'Entrégala y elige recompensa.', q=1958, lv=41, area=15, kind='npc', eid=6546)

def mage52():
    add('note', 'MISIÓN DE CLASE nivel 50+ (Pura magia, Azshara): da un gran objeto de mago. La última parte (Morphaz) es en el Templo Sumergido con grupo.', lv=52)
    raw('accept', 'Entrañas, Barrio de los Magos: recoge «Pura magia» de Pierce Esqueletonio.', q=8250, lv=52, area=UC, kind='npc', eid=4567)
    raw('turnin', 'Azshara: entrega a Sanath Lim-yo.', q=8250, lv=52, area=16, kind='npc', eid=8395)
    raw('accept', 'Torre del archimago Xylem (Azshara): recoge «El polvo mágico».', q=8251, lv=52, area=16, kind='npc', eid=8379)
    raw('do', 'Mata peritos elfos de sangre hasta tener 10 puñados de Polvo relumbrante.', q=8251, lv=52, area=16, xy=(57.2, 28.7))
    raw('turnin', 'Entrega el polvo al archimago Xylem.', q=8251, lv=52, area=16, kind='npc', eid=8379)
    raw('accept', 'Recoge «El coral de las sirenas» del archimago Xylem.', q=8252, lv=52, area=16, kind='npc', eid=8379)
    raw('do', 'Mata sirenas Látigo de Ira (costa) hasta tener 6 Corales encantados.', q=8252, lv=53, area=16, xy=(43.6, 56.4))
    raw('turnin', 'Entrega los corales al archimago Xylem.', q=8252, lv=53, area=16, kind='npc', eid=8379)
    raw('accept', 'Recoge «Destruye a Morphaz» (Templo Sumergido, CON GRUPO).', q=8253, lv=53, area=16, kind='npc', eid=8379)
    raw('turnin', 'Entrega el fragmento arcano de Morphaz al archimago Xylem.', q=8253, lv=54, area=16, kind='npc', eid=8379)

def mage60():
    add('note', 'NIVEL 60: entrena los últimos rangos y la montura rápida (~1000g en Forever). Mira /fah oro: el mago es el que más fácil farmea en área.', lv=60)

# ===========================================================================
# RUTAS
#   plan: ('zone', area, lv_ini, lv_fin, texto) · ('dungeon', texto) · ('forever', texto)
#         ('note'|'prof'|'train', nivel, texto[, consejo[, clase]]) · ('level', nivel, texto)
#         ('class', CLASE, función)  -> bloque de clase en ese punto exacto
#   clases: (nivel, CLASE, función, se_puede_en_mitad_de_zona) -> se coloca al llegar a ese nivel
# ===========================================================================
RUTAS = {}

RUTAS['alianza'] = dict(
  archivo='Alianza', titulo='Alianza (Humano)', npc_faction='A', race_mask=qdb.RACES['Human'],
  start=10, kill=float(os.environ.get('KILL_FACTOR', '2.1')),
  hand='Data_Ruta_Elwynn.lua',          # 1-10 escrita a mano
  spawn_area={}, near={}, extra={}, skip_in={}, classq={},
  clases=[(12, 'PALADIN', pal12, False), (20, 'PALADIN', pal20, False), (40, 'PALADIN', pal40, False)],
  plan=[
    ('zone', 40, 10, 17, "PÁRAMOS DE PONIENTE: sal de Elwynn por el oeste (puente de Villadorada). Base: Colina del Centinela. Descubre el vuelo."),
    ('zone', 38, 14, 19, "LOCH MODAN: vuela/coge el Tranvía Subterráneo a Forjaz y sal por la puerta este de Dun Morogh. Base: Thelsamar."),
    ('zone', 44, 17, 23, "MONTAÑAS CRESTAGRANA: desde Elwynn por el este (Valleoriente). Base: Villa del Lago. Descubre el vuelo."),
    ('dungeon', "Minas de la Muerte (17-24, en Páramos): haz las misiones de Colina del Centinela con grupo. Gran equipo azul."),
    ('zone', 10, 20, 26, "BOSQUE DEL OCASO: al sur de Elwynn. Base: Villa Oscura. Descubre el vuelo."),
    ('zone', 11, 21, 27, "LOS HUMEDALES: al norte de Loch Modan. Base: Puerto de Menethil. Descubre el vuelo."),
    ('zone', 44, 23, 28, "VUELVE A CRESTAGRANA a terminar lo que te quedaba (misiones de nivel 25+)."),
    ('zone', 10, 26, 31, "VUELVE AL BOSQUE DEL OCASO para terminar sus cadenas (Mor'Ladim, Stalvan, etc.)."),
    ('dungeon', "Las Mazmorras de Ventormenta (22-30) y Gnomeregan (25-35): recoge sus misiones en Ventormenta y Forjaz."),
    ('zone', 11, 27, 31, "VUELVE A LOS HUMEDALES para las misiones de nivel 28-30."),
    ('zone', 267, 28, 34, "LADERAS DE TRABALOMAS: desde Los Humedales al norte (puerta de Thandol). Base: Costasur. ¡Zona JcJ!"),
    ('forever', "NUEVO EN FOREVER: DALARAN en las Montañas de Alterac (al norte de Costasur). Visítala: tiene misiones y vendedores nuevos."),
    ('zone', 45, 30, 38, "TIERRAS ALTAS DE ARATHI: al este de Trabalomas. Base: Refugio de la Zaga."),
    ('zone', 33, 30, 38, "VEGA DE TUERCESPINA (norte): al sur del Bosque del Ocaso. Base: Campamento Rebelde y Bahía del Botín."),
    ('forever', "NUEVO EN FOREVER: RIVERGLADES (35-45, +150 misiones) y la mazmorra Krol'dok Stronghold (40-45). Si la zona está muy llena, sigue la ruta clásica y vuelve luego."),
    ('zone', 15, 35, 41, "PANTANO REVOLCAFANGO: barco de Menethil a Theramore. Base: Isla de Theramore."),
    ('zone', 3, 36, 44, "TIERRAS INHÓSPITAS: desde Loch Modan al sur. Ojo, zona de mucho JcJ."),
    ('zone', 8, 36, 44, "PANTANO DE LAS PENAS: al este del Bosque del Ocaso. Base: Nethergarde (Tierras Devastadas) / Puesto de la Alianza."),
    ('zone', 33, 37, 45, "VUELVE A TUERCESPINA para las misiones de 40+ (Bahía del Botín)."),
    ('dungeon', "Uldaman (40-47, Tierras Inhóspitas) y Zul'Farrak (44-54, Tanaris)."),
    ('forever', "NUEVO EN FOREVER: SHEN'DRALAS (40-53). Alternativa a Feralas/Tanaris."),
    ('zone', 357, 41, 48, "FERALAS: barco de Auberdine (Costa Oscura) o vuelo a Bastión Plumaluna."),
    ('zone', 440, 42, 49, "TANARIS: vuela a Gadgetzan (desde Theramore). Base: Gadgetzan."),
    ('zone', 47, 43, 50, "TIERRAS DEL INTERIOR: desde Trabalomas al este. Base: Nido del Águila."),
    ('zone', 51, 44, 50, "LA GARGANTA DE FUEGO: desde Loch Modan/Tierras Inhóspitas. Thorium Point."),
    ('zone', 16, 45, 52, "AZSHARA: vuelo desde Astranaar (Vallefresno)."),
    ('zone', 4, 45, 54, "LAS TIERRAS DEVASTADAS: Nethergarde, al sur del Pantano de las Penas."),
    ('zone', 490, 48, 55, "CRÁTER DE UN'GORO: desde Tanaris por el oeste. Base: Refugio Marshal."),
    ('zone', 361, 48, 55, "FRONDAVIL: al norte de Vallefresno. Base: Talonbranch Glade."),
    ('dungeon', "Templo Sumergido (50-56, Pantano de las Penas) y Profundidades de Roca Negra (52-60)."),
    ('zone', 46, 50, 56, "ESTEPAS ARDIENTES: al norte de Crestagrana. Base: Bastión de Morgan."),
    ('zone', 28, 51, 58, "TIERRAS DE LA PESTE DEL OESTE: desde Trabalomas al norte. Base: Campamento del Orvallo."),
    ('zone', 618, 53, 60, "CUNA DEL INVIERNO: desde Frondavil al norte (túnel de Fauces de Madera). Base: Everlook."),
    ('zone', 139, 54, 60, "TIERRAS DE LA PESTE DEL ESTE: Capilla de la Esperanza de la Luz."),
    ('zone', 1377, 55, 60, "SILITHUS: al sur de Un'Goro. Fuerte Cenarion."),
    ('class', 'PALADIN', pal60),
  ],
)

RUTAS['horda'] = dict(
  archivo='Horda', titulo='Horda (No-muerto)', npc_faction='H', race_mask=qdb.RACES['Scourge'],
  start=1, kill=float(os.environ.get('KILL_FACTOR', '2.3')),
  hand=None,
  # Camposanto está dentro del mapa de Tirisfal · El Baluarte (Peste del Oeste) está en el mapa de Tirisfal
  spawn_area={DEATHKNELL: TIRISFAL}, near={28: [TIRISFAL]},
  # Cartas de clase de Camposanto (cada clase ve solo la suya) y «Un trato de pícaro», que se entrega en Rémol
  extra={DEATHKNELL: [3095, 3096, 3097, 3098, 3099], TIRISFAL: [8]},
  skip_in={DEATHKNELL: [8, 590]},
  classq={3095: 'WARRIOR', 3096: 'ROGUE', 3097: 'PRIEST', 3098: 'MAGE', 3099: 'WARLOCK'},
  clases=[(10, 'MAGE', mage10, True), (15, 'MAGE', mage15, True), (26, 'MAGE', mage26, False),
          (35, 'MAGE', mage35, False), (40, 'MAGE', mage40, False), (52, 'MAGE', mage52, False)],
  plan=[
    ('note', 1, "Bienvenido, Renegado. Esta guía te dice QUÉ hacer y en QUÉ orden. Los pasos de misión se marcan solos.",
     "Regla de oro del novato: recoge TODAS las misiones de una zona antes de salir a matar. Así matas una vez y avanzas varias misiones a la vez."),
    ('note', 1, "Mago: pelea desde LEJOS. Empieza con Bola de Fuego; a nivel 4 aprende Descarga de Escarcha (frena al bicho) y a nivel 10 Nova de Escarcha (lo congela: aléjate y sigue lanzando).",
     "Entre peleas siéntate a beber (agua conjurada, gratis). Empieza cada pelea con el maná lleno.", 'MAGE'),
    ('zone', DEATHKNELL, 1, 6, "CAMPOSANTO: te despiertas en la cripta de Camposanto (Deathknell). Todo está muy cerca de la iglesia."),
    ('note', 5, "Antes de bajar a Rémol: entrena con tu instructor de clase (iglesia de Camposanto) si eres nivel 4 o 6. Compra SOLO lo que salga en verde."),
    ('note', 5, "Mago: NO compres comida ni agua NUNCA. Conjurar agua y Conjurar comida te la dan gratis.", None, 'MAGE'),
    ('zone', TIRISFAL, 5, 12, "CLAROS DE TIRISFAL: sigue el camino al este hasta Rémol (Brill). Base: Rémol. Pon tu piedra de hogar en la posada."),
    ('prof', 6, "PROFESIONES (Rémol): Primeros auxilios, Cocina y Pesca (secundarias, baratas). Principales: Herboristería + Minería. Mira /fah prof.",
     "Recolectar = oro desde el minuto 1 sin gastar. Craftear al principio CUESTA dinero."),
    ('zone', SILVERPINE, 10, 18, "BOSQUE DE ARGÉNTEOS: al sur de Tirisfal por el camino. Base: El Sepulcro. Descubre el vuelo."),
    ('level', 15, "Antes de irte a Kalimdor: llega a nivel 15 aquí en Argénteos (te falta poco). Los magos hacen aquí su misión de clase (Entrañas + Argénteos) sin cruzar el mar dos veces."),
    ('zone', 17, 12, 21, "LOS BALDÍOS: zepelín desde la torre al lado de Entrañas hasta Orgrimmar; sal por la puerta oeste hacia El Cruce. Descubre el vuelo de Orgrimmar y El Cruce."),
    ('dungeon', "Colmillo Oscuro (18-25, Bosque de Argénteos) y Cuevas de los Lamentos (17-24, Los Baldíos)."),
    ('zone', 406, 16, 25, "SIERRA ESPOLÓN: desde Los Baldíos al noroeste. Base: Refugio Roca del Sol."),
    ('zone', 267, 20, 30, "LADERAS DE TRABALOMAS: vuelve a Tirisfal en zepelín y baja por Argénteos al sur. Base: Molino Tarren. ¡Zona JcJ!"),
    ('zone', 331, 20, 30, "VALLEFRESNO: al norte de Los Baldíos. Base: Puesto Hachazo (Splintertree)."),
    ('zone', 17, 20, 27, "VUELVE A LOS BALDÍOS a terminar las cadenas del sur (Campamento Taurajo)."),
    ('zone', 400, 24, 34, "LAS MIL AGUJAS: al sur de Los Baldíos. Base: Poblado Viento Libre (Freewind)."),
    ('dungeon', "Monasterio Escarlata (26-45, noreste de Tirisfal): cementerio, biblioteca, armería y catedral. Las misiones están en Entrañas y Rémol."),
    ('forever', "NUEVO EN FOREVER: DALARAN en las Montañas de Alterac (al norte de Molino Tarren). Visítala: tiene misiones y vendedores nuevos."),
    ('zone', 45, 30, 38, "TIERRAS ALTAS DE ARATHI: al este de Trabalomas. Base: Sentencia (Hammerfall)."),
    ('zone', 33, 30, 40, "VEGA DE TUERCESPINA: zepelín de Tirisfal a Grom'gol. Bases: Campamento Grom'gol y Bahía del Botín."),
    ('zone', 405, 30, 39, "DESOLACE: desde Sierra Espolón al sur. Base: Aldea Cazasombras (Shadowprey)."),
    ('forever', "NUEVO EN FOREVER: RIVERGLADES (35-45, +150 misiones) y la mazmorra Krol'dok Stronghold (40-45). Si la zona está muy llena, sigue la ruta clásica y vuelve luego."),
    ('zone', 15, 35, 43, "MARJAL REVOLCAFANGO: desde Los Baldíos al este (Puente de Golpe Bajo) o vuelo. Base: Poblado Brackenwall."),
    ('zone', 3, 35, 44, "TIERRAS INHÓSPITAS: vuelo a Kargath (o a pie desde la Garganta de Fuego). Base: Kargath."),
    ('zone', 33, 37, 45, "VUELVE A TUERCESPINA para las misiones de 40+ (Bahía del Botín)."),
    ('zone', 8, 38, 45, "PANTANO DE LAS PENAS: base: Rocal (Stonard). Vuelo desde Grom'gol o Kargath."),
    ('note', 40, "NIVEL 40: MONTURA. Los No-muertos la compran en Rémol (Zachariah Post, al lado del instructor de equitación). Revisa el precio real en el juego.",
     "Brujos: la vuestra es de misión de clase (gratis). Mira /fah oro."),
    ('dungeon', "Uldaman (40-47, Tierras Inhóspitas) y Zul'Farrak (44-54, Tanaris)."),
    ('forever', "NUEVO EN FOREVER: SHEN'DRALAS (40-53). Alternativa a Feralas/Tanaris."),
    ('zone', 357, 41, 48, "FERALAS: al sur de Desolace o vuelo. Base: Campamento Mojache."),
    ('zone', 440, 42, 49, "TANARIS: vuelo a Gadgetzan (desde Viento Libre o Brackenwall). Base: Gadgetzan."),
    ('zone', 47, 43, 50, "TIERRAS DEL INTERIOR: desde Trabalomas al este. Base: Poblado Revantusk (costa este)."),
    ('zone', 51, 44, 50, "LA GARGANTA DE FUEGO: al norte de Tierras Inhóspitas. Thorium Point."),
    ('zone', 16, 45, 52, "AZSHARA: vuelo desde Orgrimmar a Valormok."),
    ('zone', 4, 45, 54, "LAS TIERRAS DEVASTADAS: al sur del Pantano de las Penas."),
    ('zone', 490, 48, 55, "CRÁTER DE UN'GORO: desde Tanaris por el oeste. Base: Refugio Marshal."),
    ('zone', 361, 48, 55, "FRONDAVIL: al norte de Vallefresno. Base: Puesto Bloodvenom."),
    ('dungeon', "Templo Sumergido (50-56, Pantano de las Penas) y Profundidades de Roca Negra (52-60)."),
    ('zone', 46, 50, 56, "ESTEPAS ARDIENTES: al norte de la Garganta de Fuego. Base: Cresta de la Llama."),
    ('zone', 28, 51, 58, "TIERRAS DE LA PESTE DEL OESTE: al este de Tirisfal. Base: El Baluarte (Bulwark)."),
    ('zone', 618, 53, 60, "CUNA DEL INVIERNO: desde Frondavil al norte (túnel de Fauces de Madera). Base: Vista Eterna (Everlook)."),
    ('zone', 139, 54, 60, "TIERRAS DE LA PESTE DEL ESTE: Capilla de la Esperanza de la Luz."),
    ('zone', 1377, 55, 60, "SILITHUS: al sur de Un'Goro. Fuerte Cenarion."),
    ('class', 'MAGE', mage60),
  ],
)

# ===========================================================================
def emit_block(cl, fn):
    CUR['cl'] = cl
    fn()
    CUR['cl'] = None

def emit_class_blocks(inzone=False):
    pend = CFG['_pend']
    while pend and L() >= pend[0][0] and (pend[0][3] or not inzone):
        _, cl, fn, _ = pend.pop(0)
        emit_block(cl, fn)

def main(rid):
    CFG.update(RUTAS[rid])
    CFG['_pend'] = sorted(CFG['clases'], key=lambda b: b[0])
    sim['lvl'], sim['xp'] = CFG['start'], 0

    hand_ids = []
    if CFG['hand']:
        for m in re.finditer(r'q=(\d+)', open(os.path.join(ADDON, CFG['hand']), encoding='utf-8').read()):
            if int(m.group(1)) not in hand_ids: hand_ids.append(int(m.group(1)))
    done.update(hand_ids)

    for p in CFG['plan']:
        emit_class_blocks()
        if p[0] == 'zone': plan_zone(p[1], p[2], p[3], p[4])
        elif p[0] == 'dungeon': add('zone', 'MAZMORRA: ' + p[1])
        elif p[0] == 'forever': add('zone', p[1])
        elif p[0] in ('note', 'prof', 'train'):
            add(p[0], p[2], lv=p[1], tip=p[3] if len(p) > 3 else None, cl=p[4] if len(p) > 4 else None)
        elif p[0] == 'level':
            if L() < p[1]:
                add('level', p[2], lv=p[1])
                sim['lvl'], sim['xp'] = p[1], 0
        elif p[0] == 'class': emit_block(p[1], p[2])
    emit_class_blocks()

    add('level', '¡NIVEL 60! Nueva zona: MONTE HYJAL. Raids desde el 9 de diciembre: Barrow Deeps, Cumbre Hyjal, Guarida de Onyxia.', lv=60)
    add('note', 'A 60: equipo pre-raid en mazmorras (Scholomance, Stratholme, Roca Negra), ahorra para la montura rápida y empieza JcJ (/fah jcj).', lv=60)

    # ---- Ruta ----
    out = os.path.join(ADDON, 'Data_Ruta_%s.lua' % CFG['archivo'])
    lines = ['-- ForeverAlliance&Horde - Ruta %s' % CFG['titulo'],
             '-- GENERADO automáticamente a partir de los datos de Forever de QuestieDB',
             '-- (https://github.com/Questie/QuestieDB): IDs de misión, PNJ, coordenadas y nombres en español.',
             '-- Para cambiar la ruta edita tools/planner.py y vuelve a generarlo. cl = solo para esa clase.',
             'local _, GF = ...', 'local R = {']
    for s in steps:
        parts = ['t=%s' % lua_str(s['t'])]
        if s['q']: parts.append('q=%d' % s['q'])
        if s['lv']: parts.append('lv=%d' % s['lv'])
        if s['cl']: parts.append('cl="%s"' % s['cl'])
        if s['m'] and s['x'] is not None:
            parts.append('m=%d, x=%.1f, y=%.1f' % (s['m'], s['x'], s['y']))
        parts.append('txt=%s' % lua_str(s['txt']))
        if s['tip']: parts.append('tip=%s' % lua_str(s['tip']))
        lines.append('  { ' + ', '.join(parts) + ' },')
    lines += ['}', 'GF:AddRoute("%s", R)' % rid, '']
    open(out, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
    print('%s: pasos %d, misiones %d, nivel final %d' % (rid, len(steps), len(done), L()))

    # ---- Datos de cada misión de la ruta: nivel requerido, previas, exclusivas y nombre ----
    ids = list(hand_ids) + [s['q'] for s in steps if s['q']]
    seen = set()
    qi = ['-- ForeverAlliance&Horde - Datos de las misiones de la ruta %s (GENERADO, ver tools/planner.py)' % CFG['titulo'],
          '-- rl = nivel requerido, ql = nivel de la misión, pre = una de estas antes, preg = todas estas antes,',
          '-- ex = exclusiva con, n = nombre en español',
          'local _, GF = ...', 'local T = {']
    def lst(v):
        v = [int(x) for x in (v or []) if x]
        return ('{' + ','.join(str(x) for x in v) + '}') if v else None
    for k in ids:
        if k in seen or str(k) not in Q: continue
        seen.add(k)
        q = Q[str(k)]
        parts = ['rl=%d' % (q[3] or 1), 'ql=%d' % (q[4] or q[3] or 1)]
        for key, val in (('pre', pre_single(k)), ('preg', q[11]), ('ex', q[15])):
            s = lst(val)
            if s: parts.append('%s=%s' % (key, s))
        parts.append('n=%s' % lua_str(es_name(k)))
        qi.append('  [%d]={%s},' % (k, ','.join(parts)))
    qi += ['}', 'for k, v in pairs(T) do GF.QInfo[k] = v end', '']
    open(os.path.join(ADDON, 'Data_Misiones_%s.lua' % CFG['archivo']), 'w', encoding='utf-8', newline='\n').write('\n'.join(qi))
    print('%s: info de misiones %d' % (rid, len(seen)))

if __name__ == '__main__':
    rid = sys.argv[1] if len(sys.argv) > 1 else ''
    if rid not in RUTAS:
        sys.exit('Uso: planner.py <%s>' % '|'.join(RUTAS))
    main(rid)
