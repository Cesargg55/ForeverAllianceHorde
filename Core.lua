-- ForeverAlliance&Horde - Núcleo: base de datos, utilidades, eventos y comandos
local ADDON, GF = ...
_G.ForeverAH = GF

GF.version = "1.0.0"
GF.Ruta = {}            -- pasos de la guía de TU personaje (se elige al entrar: ver PickRoute)
GF.Rutas = {}           -- todas las rutas: GF.Rutas[id] = { pasos... } (Data_Ruta_*.lua)
GF.QInfo = {}           -- datos de cada misión (Data_Misiones_*.lua)
GF.Clases = {}          -- habilidades por clase (Data_Clases.lua)
GF.Oro = {}             -- farmeos de oro (Data_Oro.lua)
GF.Profesiones = {}     -- profesiones (Data_Profesiones.lua)
GF.JcJ = {}             -- JcJ (Data_JcJ.lua)

-- Colores
GF.C = {
  oro = "|cffffd100", verde = "|cff33ff66", rojo = "|cffff4040", amarillo = "|cffffff55",
  gris = "|cff9d9d9d", azul = "|cff3fbfff", naranja = "|cffff9933", blanco = "|cffffffff",
  morado = "|cffa335ee", fin = "|r",
}
local C = GF.C

----------------------------------------------------------------------
-- Rutas disponibles. Para añadir una raza: pon su nombre interno (UnitRace, 2º valor)
-- en 'razas' de la ruta donde empieza, o crea una ruta nueva y regístrala aquí.
--   Nombres internos: Human, Dwarf, NightElf, Gnome, Orc, Scourge (No-muerto), Tauren, Troll
----------------------------------------------------------------------
GF.RutaMeta = {
  alianza = { nombre = "Alianza (Humano: Northshire y Elwynn)", inicio = "Abadía de Northshire y Bosque de Elwynn",
              faccion = "Alliance", razas = { Human = true } },
  horda   = { nombre = "Horda (No-muerto: Camposanto y Tirisfal)", inicio = "Inicio",
              faccion = "Horde", razas = { Scourge = true } },
}
GF.RutaOrden = { "alianza", "horda" }

-- Lo llaman los archivos de datos: añade pasos al final de una ruta
function GF:AddRoute(id, pasos)
  self.Rutas[id] = self.Rutas[id] or {}
  for _, s in ipairs(pasos) do table.insert(self.Rutas[id], s) end
end

-- Elige la ruta del personaje (raza -> facción -> la que haya) y se queda solo con los pasos de su clase
function GF:PickRoute()
  local db = ForeverAH_CharDB
  local _, race = UnitRace("player")
  local faction = UnitFactionGroup and UnitFactionGroup("player")
  local id = db.ruta
  self.razaSinRuta = nil
  if not (id and self.Rutas[id]) then
    id = nil
    for _, rid in ipairs(self.RutaOrden) do
      if self.RutaMeta[rid].razas[race or ""] then id = rid break end
    end
    if not id then
      for _, rid in ipairs(self.RutaOrden) do
        if self.RutaMeta[rid].faccion == faction then id = rid break end
      end
      self.razaSinRuta = race or "?"
    end
  end
  id = id or self.RutaOrden[1]
  self.rutaId = id
  local class = self:PlayerClass()
  self.Ruta = {}
  for _, s in ipairs(self.Rutas[id] or {}) do
    if not s.cl or s.cl == class then table.insert(self.Ruta, s) end
  end
end

function GF:SetRoute(id)
  local db = ForeverAH_CharDB
  if id == "" or id == "auto" then id = nil end
  if id and not self.Rutas[id] then
    local ids = {}
    for _, rid in ipairs(self.RutaOrden) do table.insert(ids, rid) end
    self:Print("Ruta desconocida. Rutas: " .. table.concat(ids, ", ") .. " (o 'auto').")
    return
  end
  db.ruta = id
  db.paso, db.manual, db.skipped, db.deferred, db.pasoFirma = 1, {}, {}, {}, nil
  self:PickRoute()
  self:BuildSections()
  self:Print("Ruta: " .. C.amarillo .. self.RutaMeta[self.rutaId].nombre .. C.fin .. ". Escribe " .. C.amarillo .. "/guia nivel" .. C.fin .. " para ir a tu nivel.")
  self:AutoAdvance()
  self:Refresh()
end

-- Facción y raza para los textos de ayuda (si tu raza no tiene textos propios, los de tu facción)
function GF:Faction()
  local f = UnitFactionGroup and UnitFactionGroup("player")
  if f ~= "Alliance" and f ~= "Horde" then f = (self.RutaMeta[self.rutaId or "alianza"] or {}).faccion or "Alliance" end
  return f
end

function GF:Race()
  local _, race = UnitRace("player")
  return race
end

function GF:Print(...)
  local msg = table.concat({ ... }, " ")
  DEFAULT_CHAT_FRAME:AddMessage(C.oro .. "[FA&H]" .. C.fin .. " " .. msg)
end

----------------------------------------------------------------------
-- Base de datos
----------------------------------------------------------------------
local defaultsGlobal = { pos = nil, infoPos = nil, scale = 1 }
local defaultsChar = {
  paso = 1,
  manual = {},          -- pasos marcados a mano ("Hecho")
  skipped = {},         -- pasos saltados con ">>"
  deferred = {},        -- [questID] = paso: misiones que aún no podías coger (nivel / previa)
  ocultar = false,
  autoVenderGris = true,
  autoReparar = true,
  avisosNivel = true,
  objetivoOro = nil,    -- en cobre; nil = automático
  ruta = nil,           -- ruta elegida a mano (/guia ruta); nil = automática según tu raza
}

local function CopyDefaults(dst, src)
  for k, v in pairs(src) do
    if dst[k] == nil then
      if type(v) == "table" then dst[k] = {} ; CopyDefaults(dst[k], v) else dst[k] = v end
    end
  end
end

----------------------------------------------------------------------
-- Utilidades de juego (con compatibilidad entre versiones de la API)
----------------------------------------------------------------------
function GF:SpellName(id)
  if C_Spell and C_Spell.GetSpellName then
    local n = C_Spell.GetSpellName(id)
    if n then return n end
  end
  if GetSpellInfo then return (GetSpellInfo(id)) end
end

function GF:QuestDone(qid)
  if not qid then return false end
  if C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted then
    return C_QuestLog.IsQuestFlaggedCompleted(qid) and true or false
  elseif IsQuestFlaggedCompleted then
    return IsQuestFlaggedCompleted(qid) and true or false
  end
  return false
end

function GF:QuestTitle(qid, fallback)
  if qid and C_QuestLog then
    local t
    if C_QuestLog.GetTitleForQuestID then t = C_QuestLog.GetTitleForQuestID(qid) end
    if (not t or t == "") and C_QuestLog.GetQuestInfo then t = C_QuestLog.GetQuestInfo(qid) end
    if t and t ~= "" then return t end
  end
  return fallback or ("Misión " .. tostring(qid))
end

-- Devuelve tabla { [questID] = true(completa) / false(en curso) }
function GF:ScanQuestLog()
  local log = {}
  local n
  if C_QuestLog and C_QuestLog.GetNumQuestLogEntries then
    n = C_QuestLog.GetNumQuestLogEntries()
  elseif GetNumQuestLogEntries then
    n = GetNumQuestLogEntries()
  end
  n = n or 0
  for i = 1, n do
    if C_QuestLog and C_QuestLog.GetInfo then
      local info = C_QuestLog.GetInfo(i)
      if info and not info.isHeader and info.questID and info.questID > 0 then
        local comp = false
        if C_QuestLog.IsComplete then comp = C_QuestLog.IsComplete(info.questID) and true or false end
        if not comp and info.isComplete and info.isComplete ~= -1 and info.isComplete ~= false and info.isComplete ~= 0 then
          comp = true
        end
        log[info.questID] = comp
      end
    elseif GetQuestLogTitle then
      local _, _, _, isHeader, _, isComplete, _, qid = GetQuestLogTitle(i)
      if not isHeader and qid and qid > 0 then
        log[qid] = (isComplete == 1 or isComplete == true)
      end
    end
  end
  GF.log = log
  return log
end

function GF:Money(copper)
  copper = copper or 0
  local g = floor(copper / 10000)
  local s = floor((copper % 10000) / 100)
  local c = copper % 100
  if g > 0 then return string.format("%s%dg|r %s%ds|r", C.oro, g, C.gris, s) end
  if s > 0 then return string.format("%s%ds|r %s%dc|r", C.blanco, s, C.naranja, c) end
  return string.format("%s%dc|r", C.naranja, c)
end

function GF:Level()
  return math.max(UnitLevel("player") or 1, self.lvlUp or 0)
end

function GF:PlayerClass()
  local _, class = UnitClass("player")
  return class
end

-- Objetivo de ahorro automático según nivel/clase
function GF:GoalInfo()
  local db = ForeverAH_CharDB
  if db.objetivoOro then return db.objetivoOro, "Objetivo personal" end
  local lvl = UnitLevel("player") or 1
  local class = self:PlayerClass()
  local montoGratis = (class == "PALADIN" or class == "WARLOCK")
  if lvl < 40 and not montoGratis then
    return 100 * 10000, "Montura nivel 40 (aprox., revisa precio real en el vendedor)"
  elseif lvl < 40 and montoGratis then
    return 60 * 10000, "Colchón para nv40 (tu montura es de misión de clase: ¡AHORRAS ~100g!)"
  elseif lvl < 60 then
    return 300 * 10000, "Reservar para habilidades 40-60 + empezar montura rápida"
  else
    return 1000 * 10000, "Montura rápida nivel 60 (~1000g en Forever)"
  end
end

----------------------------------------------------------------------
-- Lógica de pasos
----------------------------------------------------------------------
-- Tipos: accept (recoger), turnin (entregar), do (hacer objetivos), go (ir), train (entrenar),
--        level (subir a nivel X), note (consejo), zone (resumen de zona), prof (profesión)
function GF:StepDone(i)
  local s = self.Ruta[i]
  if not s then return true end
  local db = ForeverAH_CharDB
  if db.manual[i] then return true end
  local log = self.log or self:ScanQuestLog()
  if s.t == "accept" and s.q then
    return log[s.q] ~= nil or self:QuestDone(s.q)
  elseif s.t == "turnin" and s.q then
    return self:QuestDone(s.q)
  elseif s.t == "do" and s.q then
    return log[s.q] == true or self:QuestDone(s.q)
  elseif s.t == "level" and s.lv then
    return self:Level() >= s.lv
  end
  return false
end

----------------------------------------------------------------------
-- Estado real de una misión en el juego
--   "done"  = entregada        "log" = en tu diario     "ready" = puedes recogerla ya
--   "level" = te falta nivel   "pre" = te falta una misión previa
--   "na"    = no aplica (hiciste otra exclusiva con ella)
----------------------------------------------------------------------
function GF:QStatus(q)
  if self:QuestDone(q) then return "done" end
  local log = self.log or self:ScanQuestLog()
  if log[q] ~= nil then return "log" end
  local info = self.QInfo and self.QInfo[q]
  if not info then return "ready" end
  if info.ex then
    for _, e in ipairs(info.ex) do
      if self:QuestDone(e) or log[e] ~= nil then return "na" end
    end
  end
  if info.pre then
    local ok = false
    for _, p in ipairs(info.pre) do if self:QuestDone(p) then ok = true break end end
    if not ok then return "pre", info.pre[1] end
  end
  if info.preg then
    for _, p in ipairs(info.preg) do if not self:QuestDone(p) then return "pre", p end end
  end
  if self:Level() < (info.rl or 1) then return "level", info.rl end
  return "ready"
end

function GF:QName(q)
  local info = self.QInfo and self.QInfo[q]
  return (info and info.n) or self:QuestTitle(q, "misión " .. tostring(q))
end

-- ¿Se puede pasar este paso sin pararse? (no está hecho, pero no tiene sentido pararse ahora)
function GF:StepPass(i)
  local s = self.Ruta[i]
  local db = ForeverAH_CharDB
  if not s then return true end
  if db.skipped[i] then return true end
  if not s.q or not self.logReady then return false end
  local st = self:QStatus(s.q)
  if st == "level" or st == "pre" then
    if s.t == "accept" and not db.deferred[s.q] then db.deferred[s.q] = i end
    return true
  end
  if st == "na" then return true end
  if (s.t == "do" or s.t == "turnin") and st == "ready" then return true end -- no la tienes en el diario
  return false
end

-- Misiones pospuestas que ya puedes coger: avisa y, si son de tu zona actual, vuelve a ellas
function GF:CheckDeferred()
  local db = ForeverAH_CharDB
  local back
  for q, i in pairs(db.deferred) do
    local st = self:QStatus(q)
    if st == "done" or st == "log" or st == "na" then
      db.deferred[q] = nil
    elseif st == "ready" then
      db.deferred[q] = nil
      if i < db.paso and self:Section(i) == self:Section(db.paso) then
        if not back or i < back then back = i end
        self:Print(C.verde .. "¡Ya puedes recoger «" .. self:QName(q) .. "»!" .. C.fin .. " La guía vuelve a ella (paso " .. i .. ").")
      else
        self:Print(C.verde .. "Ya disponible: «" .. self:QName(q) .. "»" .. C.fin .. " (paso " .. i .. "). Mira " .. C.amarillo .. "/fah progreso" .. C.fin)
      end
    end
  end
  if back then db.paso = back end
end

----------------------------------------------------------------------
-- Secciones (zonas) de la ruta: empiezan en cada paso "go"
----------------------------------------------------------------------
function GF:BuildSections()
  local meta = self.RutaMeta[self.rutaId or ""]
  self.secOf, self.secs = {}, { { name = meta and meta.inicio or "Inicio", first = 1 } }
  self.firstStepOf = {}
  for i, s in ipairs(self.Ruta) do
    if s.t == "go" and i > 1 then
      local name = (s.txt or ""):match("^([^:]+):") or (s.txt or ""):sub(1, 40)
      self.secs[#self.secs].last = i - 1
      table.insert(self.secs, { name = name, first = i })
    end
    self.secOf[i] = #self.secs
    if s.q and not self.firstStepOf[s.q] then self.firstStepOf[s.q] = i end
  end
  self.secs[#self.secs].last = #self.Ruta
end

function GF:Section(i)
  return self.secOf and self.secOf[i] or 1
end

-- Firma estable de un paso: permite encontrar tu paso aunque cambie su número entre versiones
function GF:StepKey(i)
  local s = self.Ruta[i]
  if not s then return nil end
  return (s.t or "") .. ":" .. tostring(s.q or "") .. ":" .. (s.txt or ""):sub(1, 40)
end

function GF:RelocateProgress()
  local db = ForeverAH_CharDB
  if not db.pasoFirma or self:StepKey(db.paso) == db.pasoFirma then return end
  for i = 1, #self.Ruta do
    if self:StepKey(i) == db.pasoFirma then
      if i ~= db.paso then
        self:Print("La guía se ha actualizado: tu progreso se ha movido al paso " .. i .. ".")
        db.paso = i
        db.manual = {}
        db.skipped = {}
      end
      return
    end
  end
end

-- Avanza mientras el paso actual esté hecho o no se pueda hacer todavía
function GF:AutoAdvance()
  local db = ForeverAH_CharDB
  local guard = 0
  while db.paso < #self.Ruta and (self:StepDone(db.paso) or self:StepPass(db.paso)) and guard < 2000 do
    db.paso = db.paso + 1
    guard = guard + 1
  end
end

function GF:AfterChange()
  self:AutoAdvance()
  self:Refresh()
  if self.RefreshProgress then self:RefreshProgress() end
end

function GF:NextStep()
  local db = ForeverAH_CharDB
  db.manual[db.paso] = true
  if db.paso < #self.Ruta then db.paso = db.paso + 1 end
  self:AfterChange()
end

function GF:PrevStep()
  local db = ForeverAH_CharDB
  if db.paso > 1 then
    db.paso = db.paso - 1
    db.manual[db.paso] = nil
    db.skipped[db.paso] = nil
  end
  self:Refresh()
  if self.RefreshProgress then self:RefreshProgress() end
end

function GF:SkipStep()
  local db = ForeverAH_CharDB
  db.skipped[db.paso] = true
  if db.paso < #self.Ruta then db.paso = db.paso + 1 end
  self:AfterChange()
end

-- Ir a un paso (desde el panel de Progreso): se para ahí aunque lo hubieras saltado
function GF:JumpTo(i)
  local db = ForeverAH_CharDB
  i = math.max(1, math.min(#self.Ruta, tonumber(i) or 1))
  db.paso = i
  db.manual[i] = nil
  db.skipped[i] = nil
  self:ToggleMain(true)
  self:Refresh()
  if self.RefreshProgress then self:RefreshProgress() end
end

function GF:GoToStep(n)
  local db = ForeverAH_CharDB
  n = tonumber(n)
  if not n then return end
  n = math.max(1, math.min(#self.Ruta, n))
  db.paso = n
  for k in pairs(db.manual) do if k >= n then db.manual[k] = nil end end
  for k in pairs(db.skipped) do if k >= n then db.skipped[k] = nil end end
  self:Refresh()
  if self.RefreshProgress then self:RefreshProgress() end
end

-- Salta al primer paso adecuado para tu nivel actual (útil si empiezas a usar el addon tarde)
function GF:SyncToLevel()
  local lvl = UnitLevel("player") or 1
  local db = ForeverAH_CharDB
  for i, s in ipairs(self.Ruta) do
    if (s.lv or 1) >= lvl then
      db.paso = i
      self:AutoAdvance()
      self:Refresh()
      self:Print("Saltado al paso " .. db.paso .. " (adecuado para nivel " .. lvl .. ").")
      return
    end
  end
end

----------------------------------------------------------------------
-- Flecha / waypoint
----------------------------------------------------------------------
function GF:Waypoint(s)
  if not s or not s.m or not s.x then return end
  local title = s.txt and s.txt:gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", "") or "ForeverAlliance&Horde"
  if TomTom and TomTom.AddWaypoint then
    TomTom:AddWaypoint(s.m, s.x / 100, s.y / 100, { title = title, persistent = false, minimap = true, world = true })
    self:Print("Flecha de TomTom puesta en " .. s.x .. ", " .. s.y)
    return
  end
  if C_Map and C_Map.SetUserWaypoint and UiMapPoint then
    local ok = pcall(function()
      if C_Map.CanSetUserWaypointOnMap and not C_Map.CanSetUserWaypointOnMap(s.m) then error("no") end
      C_Map.SetUserWaypoint(UiMapPoint.CreateFromCoordinates(s.m, s.x / 100, s.y / 100))
      if C_SuperTrack and C_SuperTrack.SetSuperTrackedUserWaypoint then C_SuperTrack.SetSuperTrackedUserWaypoint(true) end
    end)
    if ok then self:Print("Marca puesta en el mapa: " .. s.x .. ", " .. s.y) return end
  end
  self:Print("Ve a las coordenadas " .. C.amarillo .. s.x .. ", " .. s.y .. C.fin .. " (instala TomTom para tener flecha).")
end

function GF:MapName(id)
  if id and C_Map and C_Map.GetMapInfo then
    local info = C_Map.GetMapInfo(id)
    if info and info.name then return info.name end
  end
  return nil
end

----------------------------------------------------------------------
-- Avisos al subir de nivel
----------------------------------------------------------------------
function GF:OnLevelUp(lvl)
  if not ForeverAH_CharDB.avisosNivel then return end
  self:Print(C.verde .. "¡Nivel " .. lvl .. "!" .. C.fin)
  if lvl % 2 == 0 then
    self:Print("Nivel par = habilidades nuevas. Ve a tu entrenador: el addon te marcará " ..
      C.verde .. "qué comprar" .. C.fin .. " y " .. C.rojo .. "qué NO" .. C.fin .. ".")
  end
  local farm = self:GoldTipForLevel(lvl)
  if farm then self:Print(C.oro .. "Oro a tu nivel:" .. C.fin .. " " .. farm) end
  if lvl == 10 then self:Print("Nivel 10: talentos desbloqueados (Escarcha para subir). Escribe " .. C.amarillo .. "/guia talentos" .. C.fin) end
  if lvl == 20 and self:PlayerClass() == "MAGE" then
    self:Print("Nivel 20: aprende " .. C.verde .. "Teletransporte: Entrañas" .. C.fin .. " y " .. C.verde .. "Orgrimmar" .. C.fin .. ". Viajar te sale casi gratis.")
  end
  if lvl == 40 then
    local extra = self:PlayerClass() == "MAGE" and ", portales" or ""
    self:Print("Nivel 40: montura" .. extra .. " y doble especialización (50g en el entrenador). " .. C.amarillo .. "/guia oro" .. C.fin)
  end
end

----------------------------------------------------------------------
-- Venta de grises y reparación
----------------------------------------------------------------------
local function ContainerInfo(bag, slot)
  if C_Container and C_Container.GetContainerItemInfo then
    return C_Container.GetContainerItemInfo(bag, slot)
  end
  local _, count, _, quality, _, _, link, _, noValue = GetContainerItemInfo(bag, slot)
  if link then return { stackCount = count, quality = quality, hyperlink = link, hasNoValue = noValue } end
end
local function NumSlots(bag)
  if C_Container and C_Container.GetContainerNumSlots then return C_Container.GetContainerNumSlots(bag) or 0 end
  return GetContainerNumSlots(bag) or 0
end
local function UseItem(bag, slot)
  if C_Container and C_Container.UseContainerItem then C_Container.UseContainerItem(bag, slot) else UseContainerItem(bag, slot) end
end

function GF:OnMerchant()
  local db = ForeverAH_CharDB
  if db.autoReparar and CanMerchantRepair and CanMerchantRepair() then
    local cost, need = GetRepairAllCost()
    if need and cost and cost > 0 and GetMoney() >= cost then
      RepairAllItems()
      self:Print("Reparado por " .. self:Money(cost) .. ".")
    end
  end
  if db.autoVenderGris then
    local total, n = 0, 0
    for bag = 0, 4 do
      for slot = 1, NumSlots(bag) do
        local info = ContainerInfo(bag, slot)
        if info and info.quality == 0 and not info.hasNoValue and info.hyperlink then
          local price = select(11, GetItemInfo(info.hyperlink)) or 0
          if price > 0 then
            total = total + price * (info.stackCount or 1)
            n = n + 1
            UseItem(bag, slot)
          end
        end
      end
    end
    if n > 0 then self:Print("Vendidos " .. n .. " objetos grises por " .. self:Money(total) .. ".") end
  end
  self:Print(C.gris .. "Recuerda: NO compres armas/armaduras al vendedor. Las misiones te dan equipo gratis." .. C.fin)
  if self:PlayerClass() == "MAGE" then
    self:Print(C.gris .. "Mago: no compres comida ni agua. Conjúrala tú (gratis)." .. C.fin)
  end
end

----------------------------------------------------------------------
-- Eventos
----------------------------------------------------------------------
local ev = CreateFrame("Frame")
GF.eventFrame = ev
ev:RegisterEvent("ADDON_LOADED")
ev:RegisterEvent("PLAYER_LOGIN")
ev:RegisterEvent("QUEST_LOG_UPDATE")
ev:RegisterEvent("QUEST_TURNED_IN")
ev:RegisterEvent("QUEST_ACCEPTED")
ev:RegisterEvent("PLAYER_LEVEL_UP")
ev:RegisterEvent("PLAYER_MONEY")
ev:RegisterEvent("MERCHANT_SHOW")
ev:RegisterEvent("TRAINER_SHOW")
ev:RegisterEvent("TRAINER_UPDATE")
ev:RegisterEvent("TRAINER_CLOSED")

local pending = false
local function Throttled()
  if pending then return end
  pending = true
  C_Timer.After(0.3, function()
    pending = false
    if not ForeverAH_CharDB or not GF.main then return end
    GF:ScanQuestLog()
    if GF.logReady then GF:CheckDeferred() end
    GF:AfterChange()
  end)
end

ev:SetScript("OnEvent", function(_, event, arg1)
  if event == "ADDON_LOADED" and arg1 == ADDON then
    ForeverAH_DB = ForeverAH_DB or {}
    ForeverAH_CharDB = ForeverAH_CharDB or {}
    CopyDefaults(ForeverAH_DB, defaultsGlobal)
    CopyDefaults(ForeverAH_CharDB, defaultsChar)
  elseif event == "PLAYER_LOGIN" then
    GF:PickRoute()
    GF:BuildSkillIndex()
    GF:BuildSections()
    GF:RelocateProgress()
    GF:CreateMainFrame()
    GF:ScanQuestLog()
    GF:Refresh()
    -- Esperamos a que el servidor mande el diario de misiones antes de saltar pasos
    C_Timer.After(4, function()
      GF.logReady = true
      GF:ScanQuestLog()
      GF:CheckDeferred()
      GF:AfterChange()
    end)
    GF:Print("Cargada v" .. GF.version .. ". Ruta: " .. C.amarillo .. GF.RutaMeta[GF.rutaId].nombre .. C.fin ..
      ". Escribe " .. C.amarillo .. "/guia" .. C.fin .. " para ver los comandos.")
    if GF.razaSinRuta then
      GF:Print(C.naranja .. "Tu raza aún no tiene ruta propia: usas la de tu facción, que empieza en otra zona." .. C.fin ..
        " Ve hasta allí o escribe " .. C.amarillo .. "/guia nivel" .. C.fin .. " cuando tengas nivel.")
    end
    if ForeverAH_CharDB.paso == 1 and (UnitLevel("player") or 1) > 3 then
      GF:Print("Ya no eres nivel 1. Escribe " .. C.amarillo .. "/guia nivel" .. C.fin .. " para saltar a la parte de la guía de tu nivel.")
    end
  elseif event == "QUEST_LOG_UPDATE" or event == "QUEST_TURNED_IN" or event == "QUEST_ACCEPTED" then
    Throttled()
  elseif event == "PLAYER_LEVEL_UP" then
    GF.lvlUp = arg1
    GF:OnLevelUp(arg1)
    Throttled()
  elseif event == "PLAYER_MONEY" then
    if GF.RefreshMoney then GF:RefreshMoney() end
  elseif event == "MERCHANT_SHOW" then
    GF:OnMerchant()
  elseif event == "TRAINER_SHOW" or event == "TRAINER_UPDATE" then
    if GF.OnTrainer then
      -- pequeño retraso para que la ventana de Blizzard ya esté abierta y podamos anclarnos a ella
      C_Timer.After(0.1, function() GF:OnTrainer(event) end)
    end
  elseif event == "TRAINER_CLOSED" then
    if GF.OnTrainerClosed then GF:OnTrainerClosed() end
  end
end)

----------------------------------------------------------------------
-- Comandos
----------------------------------------------------------------------
SLASH_GUIAFORAH1 = "/fah"
SLASH_GUIAFORAH2 = "/guia"
SlashCmdList.GUIAFORAH = function(msg)
  msg = (msg or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")
  local cmd, rest = msg:match("^(%S*)%s*(.-)$")
  if cmd == "" then
    GF:ToggleMain(true)
    GF:Print("Comandos:")
    GF:Print(C.amarillo .. "/guia ocultar|mostrar" .. C.fin .. " - ventana de la guía")
    GF:Print(C.amarillo .. "/guia habilidades" .. C.fin .. " - qué habilidades comprar y cuáles NO")
    GF:Print(C.amarillo .. "/guia talentos" .. C.fin .. " - qué talentos coger")
    GF:Print(C.amarillo .. "/guia oro" .. C.fin .. " - farmeos de oro para tu nivel y cómo ahorrar")
    GF:Print(C.amarillo .. "/guia prof" .. C.fin .. " - profesiones, qué recetas comprar y qué craftear")
    GF:Print(C.amarillo .. "/guia jcj" .. C.fin .. " - consejos de JcJ para tu clase")
    GF:Print(C.amarillo .. "/guia clases" .. C.fin .. " - qué clase elegir con tu raza")
    GF:Print(C.amarillo .. "/guia ruta alianza|horda|auto" .. C.fin .. " - cambiar de ruta (normalmente se elige sola)")
    GF:Print(C.amarillo .. "/guia novedades" .. C.fin .. " - qué hay nuevo en Forever")
    GF:Print(C.amarillo .. "/fah progreso" .. C.fin .. " - por dónde vas, qué has hecho y qué te has saltado")
    GF:Print(C.amarillo .. "/guia nivel" .. C.fin .. " - saltar al paso de tu nivel · " .. C.amarillo .. "/guia paso N" .. C.fin)
    GF:Print(C.amarillo .. "/guia objetivo 150" .. C.fin .. " - fijar objetivo de ahorro en oro (0 = automático)")
    GF:Print(C.amarillo .. "/guia vender | reparar | avisos" .. C.fin .. " - activar/desactivar automatismos")
  elseif cmd == "ocultar" then GF:ToggleMain(false)
  elseif cmd == "mostrar" then GF:ToggleMain(true)
  elseif cmd == "habilidades" or cmd == "hab" then GF:ShowInfo("habilidades")
  elseif cmd == "talentos" then GF:ShowInfo("talentos")
  elseif cmd == "oro" then GF:ShowInfo("oro")
  elseif cmd == "prof" or cmd == "profesiones" then GF:ShowInfo("prof")
  elseif cmd == "jcj" or cmd == "pvp" then GF:ShowInfo("jcj")
  elseif cmd == "clases" then GF:ShowInfo("clases")
  elseif cmd == "novedades" then GF:ShowInfo("novedades")
  elseif cmd == "progreso" or cmd == "prog" then GF:ToggleProgress(true)
  elseif cmd == "nivel" then GF:SyncToLevel()
  elseif cmd == "paso" then GF:GoToStep(rest)
  elseif cmd == "ruta" then GF:SetRoute(rest)
  elseif cmd == "objetivo" then
    local g = tonumber(rest)
    if g and g > 0 then ForeverAH_CharDB.objetivoOro = g * 10000 else ForeverAH_CharDB.objetivoOro = nil end
    GF:RefreshMoney()
    GF:Print("Objetivo de ahorro: " .. (g and g > 0 and (g .. "g") or "automático"))
  elseif cmd == "vender" then
    ForeverAH_CharDB.autoVenderGris = not ForeverAH_CharDB.autoVenderGris
    GF:Print("Vender grises automáticamente: " .. (ForeverAH_CharDB.autoVenderGris and "SÍ" or "NO"))
  elseif cmd == "reparar" then
    ForeverAH_CharDB.autoReparar = not ForeverAH_CharDB.autoReparar
    GF:Print("Reparar automáticamente: " .. (ForeverAH_CharDB.autoReparar and "SÍ" or "NO"))
  elseif cmd == "avisos" then
    ForeverAH_CharDB.avisosNivel = not ForeverAH_CharDB.avisosNivel
    GF:Print("Avisos al subir de nivel: " .. (ForeverAH_CharDB.avisosNivel and "SÍ" or "NO"))
  elseif cmd == "reset" then
    ForeverAH_CharDB.paso = 1
    ForeverAH_CharDB.manual = {}
    ForeverAH_CharDB.skipped = {}
    ForeverAH_CharDB.deferred = {}
    GF:AutoAdvance()
    GF:Refresh()
    GF:Print("Guía reiniciada.")
  else
    GF:Print("Comando desconocido. Escribe /guia")
  end
end
