# Genera la ruta 10-60 (Alianza) a partir de los datos de Forever de QuestieDB.
# Salida: un archivo Lua con pasos para ForeverHumans&Paladins.
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qdb
from qdb import Q, N, O, EQ

OUT = sys.argv[1]

# ---------------------------------------------------------------------------
# Plan de zonas: (areaID, nivel_ini, nivel_fin, texto de viaje)
# ---------------------------------------------------------------------------
SW, IF = 1519, 1537
PLAN = [
  ('zone', 40, 10, 17, "PÁRAMOS DE PONIENTE: sal de Elwynn por el oeste (puente de Villadorada). Base: Colina del Centinela. Descubre el vuelo."),
  ('class12',),
  ('zone', 38, 14, 19, "LOCH MODAN: vuela/coge el Tranvía Subterráneo a Forjaz y sal por la puerta este de Dun Morogh. Base: Thelsamar."),
  ('zone', 44, 17, 23, "MONTAÑAS CRESTAGRANA: desde Elwynn por el este (Valleoriente). Base: Villa del Lago. Descubre el vuelo."),
  ('class20',),
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
  ('class40',),
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
  ('class60',),
]

PALADIN = 2
done, excluded = set(), set()

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
    return (t[:150] + '…') if len(t) > 150 else t

def npc_es(kind, eid):
    nm = qdb.npc_name(eid) if kind == 'npc' else qdb.obj_name(eid)
    return nm[1] or nm[0] or '?'

def ent_loc(kind, eid, area):
    if kind == 'item': return None
    sp = qdb.spawns_of(kind, eid)
    if str(area) not in sp: return None
    c = qdb.centroid(sp[str(area)])
    return c

def unlocked(q):
    single = q[12]
    group = q[11]
    if single and not any(p in done for p in single): return False
    if group and not all(p in done for p in group): return False
    return True

def usable(qid, area):
    q = Q[str(qid)]
    if qid in done or qid in excluded: return False
    if q[16] != area: return False
    if not qdb.alliance_ok(q): return False
    if q[6] not in (None, 0): return False          # clase
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
        if f and 'A' not in f: return False
    ol = qdb.objective_loc(qid)
    if ol and ol[0] != area: return False            # objetivos en mazmorra / otra zona
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

steps = []
def add(t, txt, q=None, lv=None, ui=None, xy=None, tip=None):
    steps.append(dict(t=t, txt=txt, q=q, lv=lv, m=ui, x=xy and xy[0], y=xy and xy[1], tip=tip))

def plan_zone(area, lo, hi, travel):
    ui = qdb.AREA2UI.get(area)
    pool = [int(k) for k, q in Q.items() if q[16] == area]
    pool = [k for k in pool if usable(k, area)]
    if not pool: return
    add('go', travel, lv=lo, ui=ui, xy=None)
    est = float(lo)
    total = max(1, len(pool))
    step_lv = (hi - lo) / total
    active = []
    pos = None
    rounds = 0
    while rounds < 30:
        rounds += 1
        avail = []
        for k in pool:
            if k in done or k in excluded or k in active: continue
            q = Q[str(k)]
            if not unlocked(q): continue
            if (q[3] or 1) > est + 1: continue
            if (q[4] or q[3] or 1) > hi + 1: continue
            avail.append(k)
        avail = avail[: max(0, 18 - len(active))]
        if not avail and not active: break
        # recoger
        items = []
        for k in avail:
            kind, eid = qdb.starters(k)[0]
            items.append((ent_loc(kind, eid, area), k, kind, eid))
        if pos is None and items:
            # hub = punto con más dadores alrededor
            pos = max((it[0] for it in items), key=lambda p: sum(1 for o in items if dist(o[0], p) < 4))
        order, pos = nn_order(items, pos or (50, 50))
        for xy, k, kind, eid in order:
            q = Q[str(k)]
            add('accept', 'Recoge «%s» de %s.' % (es_name(k), npc_es(kind, eid)), q=k, lv=q[4] or q[3], ui=ui, xy=xy)
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
            q = Q[str(k)]
            obj = es_obj(k)
            where = (' (%s)' % ol[4]) if len(ol) > 4 and isinstance(ol[4], str) and ol[4] != 'trigger' else ''
            add('do', 'Haz «%s»%s: %s' % (es_name(k), where, obj), q=k, lv=q[4] or q[3], ui=ui, xy=xy)
        # entregar
        items = []
        for k in active:
            kind, eid = qdb.enders(k)[0]
            items.append((ent_loc(kind, eid, area), k, kind, eid))
        order, pos = nn_order(items, pos)
        for xy, k, kind, eid in order:
            q = Q[str(k)]
            add('turnin', 'Entrega «%s» a %s.' % (es_name(k), npc_es(kind, eid)), q=k, lv=q[4] or q[3], ui=ui, xy=xy)
            done.add(k)
            est = min(hi, est + step_lv)
        active = []
    add('level', 'Deberías estar cerca del nivel %d. Si te falta, mata bichos de la zona mientras recolectas.' % hi, lv=hi)

def raw(t, txt, q=None, lv=None, area=None, kind=None, eid=None, tip=None):
    ui = qdb.AREA2UI.get(area) if area else None
    xy = ent_loc(kind, eid, area) if (kind and area) else None
    add(t, txt, q=q, lv=lv, ui=ui, xy=xy, tip=tip)

def class12():
    add('note', 'MISIÓN DE CLASE nivel 12 (Libro de la Divinidad): te da REDENCIÓN (resucitar). Empieza en Villadorada.', lv=12)
    raw('accept', 'Villadorada (posada): recoge «Libro de la Divinidad» del Hermano Wilhelm.', q=2998, lv=12, area=12, kind='npc', eid=927)
    raw('turnin', 'Ventormenta, Catedral de la Luz: entrega a Duthorian Rall.', q=2998, lv=12, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «El Libro de la Divinidad».', q=1641, lv=12, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Lee el libro que te dan y entrégalo a Duthorian Rall.', q=1642, lv=12, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge el siguiente «El Libro de la Divinidad».', q=1643, lv=12, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Ventormenta (Ciudad Vieja): entrega a Stephanie Turner.', q=1643, lv=12, area=SW, kind='npc', eid=6174)
    raw('accept', 'Recoge su encargo (da 1 lino a un mendigo) de Stephanie Turner.', q=1644, lv=13, area=SW, kind='npc', eid=6174)
    raw('turnin', 'Entrega a Stephanie Turner.', q=1644, lv=13, area=SW, kind='npc', eid=6174)
    raw('accept', 'Recoge «Escrito sobre divinidad» de Stephanie Turner.', q=1780, lv=13, area=SW, kind='npc', eid=6174)
    raw('turnin', 'Vuelve a Duthorian Rall.', q=1780, lv=13, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge el siguiente libro de Duthorian Rall.', q=1781, lv=13, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrega a Gazin Tenorm (Catedral).', q=1781, lv=13, area=SW, kind='npc', eid=6173)
    raw('accept', 'Recoge «Escrito sobre divinidad» de Gazin Tenorm.', q=1786, lv=13, area=SW, kind='npc', eid=6173)
    raw('turnin', 'Elwynn (cerca de la mina de Jaspe): habla con Henze Faulk y usa el Símbolo de la Vida en él.', q=1786, lv=13, area=12, kind='npc', eid=6172)
    raw('accept', 'Recoge «Libro de la Divinidad» de Henze Faulk.', q=1787, lv=13, area=12, kind='npc', eid=6172)
    raw('turnin', 'Vuelve a Gazin Tenorm (Ventormenta).', q=1787, lv=13, area=SW, kind='npc', eid=6173)
    raw('accept', 'Recoge el último «Libro de la Divinidad».', q=1788, lv=13, area=SW, kind='npc', eid=6173)
    raw('turnin', 'Entrega a Duthorian Rall y aprende Redención.', q=1788, lv=13, area=SW, kind='npc', eid=6171)

def class20():
    add('note', 'MISIÓN DE CLASE nivel 20 (Libro del valor): ve al instructor de paladines Duthorian Rall en la Catedral de la Luz (Ventormenta).', lv=20,
        tip='Recompensa: una gran arma o escudo. Merece la pena.')
    raw('accept', 'Recoge «Escrito sobre valor» de Duthorian Rall.', q=1793, lv=20, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégasela a Duthorian Rall.', q=1793, lv=20, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «Libro del valor» (sigue la cadena).', q=1650, lv=23, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Páramos de Poniente (sur, junto a la costa): habla con Daphne Fontana.', q=1650, lv=23, area=40, kind='npc', eid=6182)
    raw('accept', 'Recoge «Libro del valor»: defiéndela de los Defias.', q=1651, lv=25, area=40, kind='npc', eid=6182,
        tip='Son 3 oleadas. Ve con nivel 22-24 o con un amigo.')
    raw('turnin', 'Entrega a Daphne Fontana.', q=1651, lv=25, area=40, kind='npc', eid=6182)
    raw('accept', 'Recoge el siguiente «Libro del valor».', q=1652, lv=25, area=40, kind='npc', eid=6182)
    raw('turnin', 'Vuelve a Duthorian Rall (Ventormenta).', q=1652, lv=25, area=SW, kind='npc', eid=6171)
    raw('accept', 'Recoge «La prueba de rectitud».', q=1653, lv=21, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Dun Morogh: habla con Jordan Fontana.', q=1653, lv=21, area=1, kind='npc', eid=6181)
    raw('accept', 'Recoge «La prueba de rectitud» (materiales).', q=1654, lv=22, area=1, kind='npc', eid=6181,
        tip='Necesitas: carga de Bailor (Loch Modan), madera de roble blanco y la gema Kor (Costa Oscura).')
    raw('note', 'Loch Modan (Thelsamar): Bailor Petramano te da «Envío de minerales de Bailor».', lv=22, area=38, kind='npc', eid=6241)
    raw('turnin', 'Entrega los materiales a Jordan Fontana.', q=1654, lv=22, area=1, kind='npc', eid=6181)
    raw('turnin', 'Entrega «La prueba de rectitud» final y elige tu arma.', q=1806, lv=22, area=1, kind='npc', eid=6181,
        tip='Elige el Martillo de Verigan (dos manos): ideal para Reprensión.')

def class40():
    add('note', 'NIVEL 40: ¡MONTURA GRATIS! Misión de clase «Libro de la nobleza».', lv=40)
    raw('accept', 'Ventormenta: recoge «Libro de la nobleza» de Duthorian Rall.', q=1661, lv=40, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégala y aprende Invocar caballo de guerra.', q=1661, lv=40, area=SW, kind='npc', eid=6171,
        tip='Te ahorras ~100g. Ese oro guárdalo para la montura rápida de 60.')
    add('train', 'Entrena nivel 40 y activa la DOBLE ESPECIALIZACIÓN (50g): Reprensión + Sagrado o Protección.', lv=40)

def class60():
    add('note', 'NIVEL 60: CORCEL (montura épica de paladín). Cadena larga y cara; empieza cuando tengas ~500g y un grupo para Scholomance.', lv=60)
    raw('accept', 'Ventormenta: recoge «Lord Grisillo Quiebrasombras» de Duthorian Rall.', q=7638, lv=60, area=SW, kind='npc', eid=6171)
    raw('turnin', 'Entrégala a Lord Grisillo Quiebrasombras (Catedral).', q=7638, lv=60, area=SW, kind='npc', eid=928)
    raw('accept', 'Recoge «Énfasis en el sacrificio».', q=7637, lv=60, area=SW, kind='npc', eid=928)
    add('note', 'Sigue la cadena del Corcel (Forjaz, Tierras de la Peste, Scholomance). Necesitas: Gualdrapa de arcanita, Cristal de adivinación y mucho oro.', lv=60)

for p in PLAN:
    if p[0] == 'zone': plan_zone(p[1], p[2], p[3], p[4])
    elif p[0] == 'dungeon': add('zone', 'MAZMORRA: ' + p[1], lv=None)
    elif p[0] == 'forever': add('zone', p[1], lv=None)
    elif p[0] == 'class12': class12()
    elif p[0] == 'class20': class20()
    elif p[0] == 'class40': class40()
    elif p[0] == 'class60': class60()

add('level', '¡NIVEL 60! Nueva zona: MONTE HYJAL. Raids desde el 9 de diciembre: Barrow Deeps, Cumbre Hyjal, Guarida de Onyxia.', lv=60)
add('note', 'A 60: equipo pre-raid en mazmorras (Scholomance, Stratholme, Roca Negra), ahorra para la montura rápida y empieza JcJ (/fhp jcj).', lv=60)

# ---------------------------------------------------------------------------
lines = ['-- ForeverHumans&Paladins - Ruta 10-60 (Alianza)',
         '-- GENERADO automáticamente a partir de los datos de Forever de QuestieDB',
         '-- (https://github.com/Questie/QuestieDB): IDs de misión, PNJ, coordenadas y nombres en español.',
         '-- Para cambiar la ruta edita tools/planner.py y vuelve a generarlo.',
         'local _, GF = ...', 'local R = {']
for s in steps:
    parts = ['t=%s' % lua_str(s['t'])]
    if s['q']: parts.append('q=%d' % s['q'])
    if s['lv']: parts.append('lv=%d' % s['lv'])
    if s['m'] and s['x'] is not None:
        parts.append('m=%d, x=%.1f, y=%.1f' % (s['m'], s['x'], s['y']))
    parts.append('txt=%s' % lua_str(s['txt']))
    if s['tip']: parts.append('tip=%s' % lua_str(s['tip']))
    lines.append('  { ' + ', '.join(parts) + ' },')
lines += ['}', 'for _, s in ipairs(R) do table.insert(GF.Ruta, s) end', '']
open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))
print('pasos', len(steps), 'misiones', len(done))
