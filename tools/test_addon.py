# Prueba la lógica del addon fuera del juego con una API de WoW simulada (requiere: pip install lupa).
# Uso: py -I tools/test_addon.py <carpeta_de_lupa_o_site-packages> <carpeta_del_addon>
import sys, os, re
sys.path.insert(0, sys.argv[1])          # pylib (lupa)
ADDON = sys.argv[2]
from lupa import LuaRuntime
lua = LuaRuntime(unpack_returned_tuples=True)

STUBS = r'''
PRINTS = {}
TIMERS = {}
STATE = { level = 1, done = {}, log = {} }   -- log[q] = false (en curso) / true (completa)
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
function UnitClass() return "Paladín", "PALADIN" end
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
lua.execute(STUBS)
G = lua.globals()

toc = open(os.path.join(ADDON, 'ForeverHumansPaladins.toc'), encoding='utf-8').read()
files = [l.strip() for l in toc.splitlines() if l.strip().endswith('.lua')]
ns = lua.table()
loader = lua.eval('function(src, name, a, ns) local f, err = load(src, "@" .. name); if not f then error(err) end; return f(a, ns) end')
for f in files:
    loader(open(os.path.join(ADDON, f), encoding='utf-8').read(), f, 'ForeverHumansPaladins', ns)
GF = G.ForeverHP

def fire(ev, *a):
    for fr in G.FRAMES.values():
        fn = fr['script_OnEvent']
        if fn: fn(fr, ev, *a)
    G.RUN_TIMERS()

def step(): return G.ForeverHP_CharDB.paso
def cur(): s = GF.Ruta[step()]; return '%s q=%s %s' % (s.t, s.q, (s.txt or '')[:60])
def prints(clear=True):
    out = list(G.PRINTS.values());
    if clear: lua.execute('PRINTS = {}')
    return out

ok = True
def check(cond, msg):
    global ok
    print(('  OK   ' if cond else '  FALLO ') + msg)
    ok = ok and cond

# Lista de pasos de la ruta escrita a mano para preparar estados
R = [GF.Ruta[i] for i in range(1, len(GF.Ruta) + 1)]
print('Pasos totales:', len(R))

# ---------- Escenario 1: personaje nuevo ----------
print('Escenario 1: personaje nuevo, nivel 1')
fire('ADDON_LOADED', 'ForeverHumansPaladins'); fire('PLAYER_LOGIN')
check(step() == 1, 'empieza en el paso 1 -> ' + cur())
GF.NextStep(GF)    # nota de bienvenida
check(R[step()-1].q == 783, 'paso 2 = recoger Una amenaza del interior -> ' + cur())
G.STATE.log[783] = True; fire('QUEST_ACCEPTED')
check(R[step()-1].t == 'turnin' and R[step()-1].q == 783, 'al recoger 783 avanza solo a entregarla -> ' + cur())

# ---------- Escenario 2: misión que pide nivel 7 (Un peligro con olor a pescado, 40) ----------
print('Escenario 2: nivel 6 en Villadorada, la misión 40 pide nivel 7')
i40 = next(i for i, s in enumerate(R, 1) if s.q == 40 and s.t == 'accept')
G.STATE.level = 6
# todo lo anterior hecho
for s in R[:i40-1]:
    if s.q: G.STATE.done[s.q] = True
G.STATE.log = lua.table()
lua.execute('STATE.log = {}')
G.ForeverHP_CharDB.paso = i40
for k in list(G.ForeverHP_CharDB.manual.keys()): G.ForeverHP_CharDB.manual[k] = None
fire('QUEST_LOG_UPDATE')
check(step() > i40, 'no se para en la misión 40 (te falta nivel), va a -> paso %d %s' % (step(), cur()))
check(G.ForeverHP_CharDB.deferred[40] == i40, 'la 40 queda pospuesta para luego')
d = GF.ProgressData(GF)
blocked = [e.q for e in d.blocked.values()]
check(40 in blocked, 'el panel la muestra en PENDIENTES (necesitas nivel 7)')
here = step()
prints()
G.STATE.level = 7; fire('PLAYER_LEVEL_UP', 7)
check(step() == i40, 'al subir a 7 la guía vuelve a la misión 40 (paso %d) -> %s' % (step(), cur()))
check(any('Ya puedes recoger' in p for p in prints()), 'avisa en el chat: ¡Ya puedes recoger!')
G.STATE.log[40] = False; fire('QUEST_ACCEPTED')
check(R[step()-1].q == 40 and R[step()-1].t == 'turnin', 'después de recogerla sigue con su entrega -> ' + cur())

# ---------- Escenario 3: saltar una misión con >> y verla en el panel ----------
print('Escenario 3: saltar una misión con >>')
lua.execute('STATE.log = {}')
G.STATE.level = 8
iacc = next(i for i, s in enumerate(R, 1) if s.q == 60 and s.t == 'accept')
for s in R[:iacc-1]:
    if s.q: G.STATE.done[s.q] = True
G.ForeverHP_CharDB.paso = iacc
fire('QUEST_LOG_UPDATE')
check(step() == iacc, 'se para en recoger «Las velas de los kóbolds» -> ' + cur())
GF.SkipStep(GF)
check(step() > iacc, 'tras >> pasa al siguiente y se salta también sus pasos de hacer/entregar -> ' + cur())
d = GF.ProgressData(GF)
sk = [e.q for e in d.skippedReady.values()]
check(60 in sk, 'el panel la muestra en TE HAS SALTADO con botón Ir')
GF.JumpTo(GF, iacc)
check(step() == iacc, 'el botón Ir vuelve a esa misión')

# ---------- Escenario 4: César en el paso de la mina de Jaspe ----------
print('Escenario 4: progreso guardado de César')
i76 = next(i for i, s in enumerate(R, 1) if s.q == 76 and s.t == 'do')
lua.execute('STATE.log = {}')
for k in list(G.STATE.done.keys()): G.STATE.done[k] = None
for s in R[:i76-1]:
    if s.q and s.q not in (76, 35, 88): G.STATE.done[s.q] = True
G.STATE.log[76] = False; G.STATE.log[35] = False; G.STATE.log[88] = False
G.STATE.level = 9
G.ForeverHP_CharDB.paso = i76
fire('QUEST_LOG_UPDATE')
check(step() == i76, 'sigue en "Explora la mina de Jaspe" (paso %d)' % i76)
G.STATE.log[76] = True; fire('QUEST_LOG_UPDATE')
check(R[step()-1].q == 35, 'al explorar la mina pasa a entregar «Más preocupaciones» -> ' + cur())

# ---------- Escenario 5: abrir paneles sin errores ----------
print('Escenario 5: abrir panel de Progreso y ventanas')
try:
    GF.ToggleProgress(GF, True); GF.RefreshProgress(GF); GF.ShowInfo(GF, 'habilidades'); GF.Refresh(GF)
    check(True, 'paneles abiertos sin errores')
except Exception as e:
    check(False, 'error: %s' % e)

# ---------- Escenario 6: recorrer toda la ruta simulando que lo haces todo ----------
print('Escenario 6: recorrer la ruta completa')
lua.execute('STATE.log = {}; STATE.done = {}')
G.STATE.level = 1
G.ForeverHP_CharDB.paso = 1
lua.execute('ForeverHP_CharDB.manual = {}; ForeverHP_CharDB.skipped = {}; ForeverHP_CharDB.deferred = {}')
guard = 0
while guard < 4000:
    guard += 1
    i = step(); s = R[i-1]
    if i >= len(R): break
    if s.t == 'accept' and s.q: G.STATE.log[s.q] = False; fire('QUEST_ACCEPTED')
    elif s.t == 'do' and s.q: G.STATE.log[s.q] = True; fire('QUEST_LOG_UPDATE')
    elif s.t == 'turnin' and s.q: G.STATE.log[s.q] = None; G.STATE.done[s.q] = True; fire('QUEST_TURNED_IN')
    elif s.t == 'level': G.STATE.level = max(G.STATE.level, s.lv or 1); fire('PLAYER_LEVEL_UP', G.STATE.level)
    else: GF.NextStep(GF)
    if step() == i:   # no avanzó: atasco
        if s.lv and s.lv > G.STATE.level:
            G.STATE.level = s.lv; fire('PLAYER_LEVEL_UP', s.lv)
        if step() == i:
            GF.NextStep(GF)
    if s.lv and s.lv > G.STATE.level: G.STATE.level = min(60, s.lv)
    if s.t == 'note' and 'NIVEL 60' in (s.txt or ''): G.STATE.level = 60; fire('PLAYER_LEVEL_UP', 60)
check(step() >= len(R) - 1, 'llega al final de la ruta (paso %d de %d) en %d acciones' % (step(), len(R), guard))
d = GF.ProgressData(GF)
print('  misiones hechas %d de %d; saltadas disponibles %d; pendientes %d' % (d.done, d.total, len(d.skippedReady), len(d.blocked)))
for e in list(d.skippedReady.values())[:10]:
    print('   saltada:', e.q, GF.QName(GF, e.q), 'paso', e.i)
for e in list(d.blocked.values())[:10]:
    print('   bloqueada:', e.q, GF.QName(GF, e.q), e.st, e.extra, 'paso', e.i)

print('RESULTADO:', 'TODO OK' if ok else 'HAY FALLOS')
