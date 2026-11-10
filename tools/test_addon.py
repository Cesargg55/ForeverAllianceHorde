# Prueba la lógica del addon fuera del juego con una API de WoW simulada (requiere: pip install lupa).
# Uso: py -I tools/test_addon.py <carpeta_de_lupa_o_site-packages> <carpeta_del_addon>
# Cada personaje se prueba en un Lua nuevo (como si entraras con otro personaje).
import sys, os
sys.path.insert(0, sys.argv[1])          # pylib (lupa)
ADDON = sys.argv[2]
from lupa import LuaRuntime

STUBS = r'''
PRINTS = {}
TIMERS = {}
STATE = { level = 1, done = {}, log = {}, race = "Human", raceName = "Humano", class = "PALADIN", faction = "Alliance" }
local function newobj()
  local o = { shown = true, text = "" }
  return setmetatable(o, { __index = function(t, k)
    if k == "Show" then return function(self) self.shown = true end end
    if k == "Hide" then return function(self) self.shown = false end end
    if k == "IsShown" then return function(self) return self.shown end end
    if k == "SetText" then return function(self, s) self.text = s end end
    if k == "GetText" then return function(self) return self.text end end
    if k == "GetStringHeight" then return function() return 12 end end
    if k == "GetPoint" then return function() return "CENTER", nil, "CENTER", 0, 0 end end
    if k == "CreateFontString" or k == "CreateTexture" then return function() return newobj() end end
    if k == "SetScript" then return function(self, ev, fn) self["script_" .. ev] = fn end end
    return function() end
  end })
end
FRAMES = {}
function CreateFrame(kind, name, parent, tmpl) local o = newobj(); table.insert(FRAMES, o); if name then _G[name] = o end; return o end
UIParent, GameTooltip = newobj(), newobj()
function GameTooltip_Hide() end
UISpecialFrames = {}
tinsert, floor = table.insert, math.floor
BackdropTemplateMixin = {}
SlashCmdList = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(self, m) table.insert(PRINTS, (m:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", ""))) end }
C_Timer = { After = function(s, fn) table.insert(TIMERS, fn) end }
function RUN_TIMERS() local n = 0 while #TIMERS > 0 and n < 100 do local fn = table.remove(TIMERS, 1); fn(); n = n + 1 end end
function UnitLevel() return STATE.level end
function UnitClass() return STATE.class, STATE.class end
function UnitRace() return STATE.raceName, STATE.race end
function UnitFactionGroup() return STATE.faction, STATE.faction end
function GetMoney() return 12345 end
C_Spell = { GetSpellName = function(id) return "Hechizo" .. id end }
C_Map = { GetMapInfo = function(id) return { name = "Mapa" .. id } end }
local function logList() local l = {} for q, c in pairs(STATE.log) do table.insert(l, q) end table.sort(l) return l end
C_QuestLog = {
  GetNumQuestLogEntries = function() return #logList() end,
  GetInfo = function(i) local q = logList()[i]; return q and { questID = q, isHeader = false } end,
  IsComplete = function(q) return STATE.log[q] == true end,
  IsQuestFlaggedCompleted = function(q) return STATE.done[q] == true end,
  GetTitleForQuestID = function(q) return nil end,
}
'''

toc = open(os.path.join(ADDON, 'ForeverAllianceHorde.toc'), encoding='utf-8').read()
FILES = [l.strip() for l in toc.splitlines() if l.strip().endswith('.lua')]

ok = True
def check(cond, msg):
    global ok
    print(('  OK   ' if cond else '  FALLO ') + msg)
    ok = ok and cond

class Char:
    """Un personaje: Lua nuevo, addon cargado, login hecho."""
    def __init__(self, race, raceName, cls, faction):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(STUBS)
        self.G = self.lua.globals()
        self.G.STATE.race, self.G.STATE.raceName, self.G.STATE['class'], self.G.STATE.faction = race, raceName, cls, faction
        ns = self.lua.table()
        loader = self.lua.eval('function(src, name, a, ns) local f, err = load(src, "@" .. name); if not f then error(err) end; return f(a, ns) end')
        for f in FILES:
            loader(open(os.path.join(ADDON, f), encoding='utf-8').read(), f, 'ForeverAllianceHorde', ns)
        self.GF = self.G.ForeverAH
        self.fire('ADDON_LOADED', 'ForeverAllianceHorde'); self.fire('PLAYER_LOGIN')
        self.R = [self.GF.Ruta[i] for i in range(1, len(self.GF.Ruta) + 1)]
    def fire(self, ev, *a):
        for fr in self.G.FRAMES.values():
            fn = fr['script_OnEvent']
            if fn: fn(fr, ev, *a)
        self.G.RUN_TIMERS()
    def step(self): return self.G.ForeverAH_CharDB.paso
    def cur(self): s = self.GF.Ruta[self.step()]; return '%s q=%s %s' % (s.t, s.q, (s.txt or '')[:60])
    def prints(self, clear=True):
        out = list(self.G.PRINTS.values())
        if clear: self.lua.execute('PRINTS = {}')
        return out
    def idx(self, q, t):
        return next(i for i, s in enumerate(self.R, 1) if s.q == q and s.t == t)
    def reset(self):
        self.lua.execute('STATE.log = {}; STATE.done = {}; ForeverAH_CharDB.deferred = {}; ForeverAH_CharDB.skipped = {}; ForeverAH_CharDB.manual = {}')
    def done_before(self, i, keep=()):
        for s in self.R[:i-1]:
            if s.q and s.q not in keep: self.G.STATE.done[s.q] = True

def deferral(c, q, lv):
    """Misión que pide nivel lv: se pospone y la guía vuelve a ella al subir."""
    c.reset()
    i = c.idx(q, 'accept')
    c.G.STATE.level = lv - 1
    c.done_before(i)
    c.G.ForeverAH_CharDB.paso = i
    c.fire('QUEST_LOG_UPDATE')
    check(c.step() > i, 'no se para en la misión %d (te falta nivel), va a -> %s' % (q, c.cur()))
    check(c.G.ForeverAH_CharDB.deferred[q] == i, 'la %d queda pospuesta para luego' % q)
    check(q in [e.q for e in c.GF.ProgressData(c.GF).blocked.values()], 'el panel la muestra en PENDIENTES (necesitas nivel %d)' % lv)
    c.prints()
    c.G.STATE.level = lv; c.fire('PLAYER_LEVEL_UP', lv)
    check(c.step() == i, 'al subir a %d la guía vuelve a la misión %d -> %s' % (lv, q, c.cur()))
    check(any('Ya puedes recoger' in p for p in c.prints()), 'avisa en el chat: ¡Ya puedes recoger!')

def skip(c, q, lv):
    c.reset()
    c.G.STATE.level = lv
    i = c.idx(q, 'accept')
    c.done_before(i)
    c.G.ForeverAH_CharDB.paso = i
    c.fire('QUEST_LOG_UPDATE')
    check(c.step() == i, 'se para en recoger la misión %d -> %s' % (q, c.cur()))
    c.GF.SkipStep(c.GF)
    check(c.step() > i, 'tras >> pasa al siguiente -> ' + c.cur())
    check(q in [e.q for e in c.GF.ProgressData(c.GF).skippedReady.values()], 'el panel la muestra en TE HAS SALTADO con botón Ir')
    c.GF.JumpTo(c.GF, i)
    check(c.step() == i, 'el botón Ir vuelve a esa misión')

def in_progress(c, q, lv, keep=()):
    c.reset()
    i = c.idx(q, 'do')
    c.done_before(i, keep=(q,) + tuple(keep))
    c.G.STATE.log[q] = False
    for k in keep: c.G.STATE.log[k] = False
    c.G.STATE.level = lv
    c.G.ForeverAH_CharDB.paso = i
    c.fire('QUEST_LOG_UPDATE')
    check(c.step() == i, 'sigue en el objetivo de la misión %d (paso %d)' % (q, i))
    c.G.STATE.log[q] = True; c.fire('QUEST_LOG_UPDATE')
    nxt = c.R[c.step()-1]
    check(nxt.t == 'turnin' or (nxt.q in keep), 'al completar el objetivo pasa a la siguiente entrega -> ' + c.cur())

def panels(c):
    try:
        c.GF.ToggleProgress(c.GF, True); c.GF.RefreshProgress(c.GF)
        for k in ('habilidades', 'talentos', 'oro', 'prof', 'jcj', 'clases', 'novedades'):
            c.GF.ShowInfo(c.GF, k)
        c.GF.Refresh(c.GF)
        check(True, 'paneles y pestañas abiertos sin errores')
    except Exception as e:
        check(False, 'error: %s' % e)

def walk(c):
    c.lua.execute('STATE.log = {}; STATE.done = {}; ForeverAH_CharDB.manual = {}; ForeverAH_CharDB.skipped = {}; ForeverAH_CharDB.deferred = {}')
    c.G.STATE.level = 1
    c.G.ForeverAH_CharDB.paso = 1
    R, G = c.R, c.G
    guard = 0
    while guard < 5000:
        guard += 1
        i = c.step(); s = R[i-1]
        if i >= len(R): break
        if s.t == 'accept' and s.q: G.STATE.log[s.q] = False; c.fire('QUEST_ACCEPTED')
        elif s.t == 'do' and s.q: G.STATE.log[s.q] = True; c.fire('QUEST_LOG_UPDATE')
        elif s.t == 'turnin' and s.q: G.STATE.log[s.q] = None; G.STATE.done[s.q] = True; c.fire('QUEST_TURNED_IN')
        elif s.t == 'level': G.STATE.level = max(G.STATE.level, s.lv or 1); c.fire('PLAYER_LEVEL_UP', G.STATE.level)
        else: c.GF.NextStep(c.GF)
        if c.step() == i:
            if s.lv and s.lv > G.STATE.level:
                G.STATE.level = s.lv; c.fire('PLAYER_LEVEL_UP', s.lv)
            if c.step() == i:
                c.GF.NextStep(c.GF)
        if s.lv and s.lv > G.STATE.level: G.STATE.level = min(60, s.lv)
        if s.t == 'note' and 'NIVEL 60' in (s.txt or ''): G.STATE.level = 60; c.fire('PLAYER_LEVEL_UP', 60)
    check(c.step() >= len(R) - 1, 'recorre la ruta entera (paso %d de %d) en %d acciones' % (c.step(), len(R), guard))
    d = c.GF.ProgressData(c.GF)
    print('  misiones hechas %d de %d; saltadas disponibles %d; pendientes %d' % (d.done, d.total, len(d.skippedReady), len(d.blocked)))
    for e in list(d.skippedReady.values())[:10]:
        print('   saltada:', e.q, c.GF.QName(c.GF, e.q), 'paso', e.i)
    for e in list(d.blocked.values())[:10]:
        print('   bloqueada:', e.q, c.GF.QName(c.GF, e.q), e.st, e.extra, 'paso', e.i)

def classes_in(c):
    return sorted(set(s['cl'] for s in c.R if s['cl']))

# ======================================================================
print('== HUMANO PALADÍN ==')
c = Char('Human', 'Humano', 'PALADIN', 'Alliance')
check(c.GF.rutaId == 'alianza', 'elige la ruta de la Alianza')
check(classes_in(c) == ['PALADIN'], 'solo ve pasos de clase de Paladín: %s' % classes_in(c))
check(any(s.q == 2998 for s in c.R), 'incluye su misión de clase de nv12 (Libro de la Divinidad)')
check(c.R[c.step()-1].t == 'note', 'empieza en la nota de bienvenida')
c.GF.NextStep(c.GF)
check(c.R[c.step()-1].q == 783, 'paso 2 = recoger «Una amenaza interna» (783) -> ' + c.cur())
c.G.STATE.log[783] = True; c.fire('QUEST_ACCEPTED')
check(c.R[c.step()-1].t == 'turnin' and c.R[c.step()-1].q == 783, 'al recogerla avanza solo a entregarla -> ' + c.cur())
print('- misión que pide nivel 7 (40)'); deferral(c, 40, 7)
print('- saltar con >> (60)'); skip(c, 60, 8)
print('- mina de Jaspe en curso (76)'); in_progress(c, 76, 9, keep=(35, 88))
print('- paneles'); panels(c)
print('- ruta completa'); walk(c)

print('== NO-MUERTO MAGO ==')
c = Char('Scourge', 'No-muerto', 'MAGE', 'Horde')
check(c.GF.rutaId == 'horda', 'elige la ruta de la Horda')
check(classes_in(c) == ['MAGE'], 'solo ve pasos de clase de Mago: %s' % classes_in(c))
check(any(s.q == 3098 for s in c.R) and not any(s.q == 3095 for s in c.R), 've la carta de mago (3098) y no la de guerrero (3095)')
while c.R[c.step()-1].t in ('note', 'go'): c.GF.NextStep(c.GF)
check(c.R[c.step()-1].q == 363, 'primer paso de misión = recoger «Desvelo brutal» (363) -> ' + c.cur())
print('- misión que pide nivel 5 (5481)'); deferral(c, 5481, 5)
print('- saltar con >> (404)'); skip(c, 404, 6)
print('- misión de clase en curso (1882)'); in_progress(c, 1882, 10)
print('- paneles'); panels(c)
print('- ruta completa'); walk(c)

print('== NO-MUERTO GUERRERO ==')
c = Char('Scourge', 'No-muerto', 'WARRIOR', 'Horde')
check(classes_in(c) == ['WARRIOR'], 'solo ve su carta de clase: %s' % classes_in(c))
check(not any(s.q == 1881 for s in c.R), 'no ve las misiones de mago')
print('- paneles'); panels(c)
print('- ruta completa'); walk(c)

print('== ENANO CAZADOR (raza sin ruta propia) ==')
c = Char('Dwarf', 'Enano', 'HUNTER', 'Alliance')
check(c.GF.rutaId == 'alianza' and c.GF.razaSinRuta == 'Dwarf', 'usa la ruta de su facción y lo avisa')
check(any('aún no tiene ruta propia' in p for p in c.prints(False)), 'mensaje en el chat')
c.G.SlashCmdList.GUIAFORAH('ruta horda')
check(c.GF.rutaId == 'horda' and c.G.ForeverAH_CharDB.ruta == 'horda', '/guia ruta horda cambia de ruta')
c.G.SlashCmdList.GUIAFORAH('ruta auto')
check(c.GF.rutaId == 'alianza', '/guia ruta auto vuelve a la automática')
print('- paneles'); panels(c)

print('RESULTADO:', 'TODO OK' if ok else 'HAY FALLOS')
