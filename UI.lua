-- ForeverHumans&Paladins - Interfaz: ventana de pasos y ventana de información
local _, GF = ...
local C = GF.C
local BACKDROP_T = BackdropTemplateMixin and "BackdropTemplate" or nil

local TIPOS = {
  accept = { C.amarillo, "RECOGER" },
  turnin = { C.verde, "ENTREGAR" },
  ["do"] = { C.naranja, "HACER" },
  go     = { C.azul, "IR A" },
  train  = { C.morado, "ENTRENAR" },
  level  = { C.blanco, "SUBIR NIVEL" },
  note   = { C.gris, "CONSEJO" },
  zone   = { C.azul, "ZONA" },
  prof   = { C.oro, "PROFESIÓN" },
}

local function SetBackdrop(f)
  if not f.SetBackdrop then return end
  f:SetBackdrop({
    bgFile = "Interface\\Tooltips\\UI-Tooltip-Background",
    edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
    tile = true, tileSize = 16, edgeSize = 14,
    insets = { left = 3, right = 3, top = 3, bottom = 3 },
  })
  f:SetBackdropColor(0.05, 0.05, 0.08, 0.92)
  f:SetBackdropBorderColor(0.9, 0.75, 0.2, 1)
end

local function MakeButton(parent, text, w, onClick)
  local b = CreateFrame("Button", nil, parent, "UIPanelButtonTemplate")
  b:SetSize(w, 20)
  b:SetText(text)
  b:SetScript("OnClick", onClick)
  return b
end

local function SavePos(f, key)
  local p, _, rp, x, y = f:GetPoint()
  ForeverHP_DB[key] = { p, rp, x, y }
end

local function Movable(f, key)
  f:SetMovable(true)
  f:EnableMouse(true)
  f:RegisterForDrag("LeftButton")
  f:SetClampedToScreen(true)
  f:SetScript("OnDragStart", f.StartMoving)
  f:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() SavePos(self, key) end)
end

----------------------------------------------------------------------
-- Ventana principal
----------------------------------------------------------------------
function GF:CreateMainFrame()
  if self.main then return end
  local f = CreateFrame("Frame", "ForeverHPMain", UIParent, BACKDROP_T)
  f:SetSize(360, 200)
  SetBackdrop(f)
  Movable(f, "pos")
  local pos = ForeverHP_DB.pos
  if pos then f:SetPoint(pos[1], UIParent, pos[2], pos[3], pos[4]) else f:SetPoint("RIGHT", UIParent, "RIGHT", -60, 120) end
  f:SetScale(ForeverHP_DB.scale or 1)

  f.title = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  f.title:SetPoint("TOPLEFT", 10, -8)
  f.title:SetText(C.oro .. "ForeverHumans" .. C.fin .. C.azul .. "&Paladins" .. C.fin)

  f.counter = f:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  f.counter:SetPoint("TOPRIGHT", -28, -10)

  local close = CreateFrame("Button", nil, f, "UIPanelCloseButton")
  close:SetPoint("TOPRIGHT", 2, 2)
  close:SetScript("OnClick", function() GF:ToggleMain(false) GF:Print("Ventana oculta. /guia mostrar para verla.") end)

  f.tipo = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  f.tipo:SetPoint("TOPLEFT", 10, -28)

  f.txt = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  f.txt:SetPoint("TOPLEFT", 10, -44)
  f.txt:SetWidth(340)
  f.txt:SetJustifyH("LEFT")
  f.txt:SetJustifyV("TOP")

  f.tip = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  f.tip:SetPoint("TOPLEFT", f.txt, "BOTTOMLEFT", 0, -6)
  f.tip:SetWidth(340)
  f.tip:SetJustifyH("LEFT")
  f.tip:SetTextColor(0.75, 0.75, 0.75)

  -- Todo se coloca de arriba abajo para que nada se pise
  f.coords = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  f.coords:SetPoint("TOPLEFT", f.tip, "BOTTOMLEFT", 0, -10)
  f.coords:SetWidth(270)
  f.coords:SetJustifyH("LEFT")

  f.flecha = MakeButton(f, "Flecha", 60, function() GF:Waypoint(GF.Ruta[ForeverHP_CharDB.paso]) end)
  f.flecha:SetPoint("RIGHT", f, "RIGHT", -10, 0)
  f.flecha:SetPoint("TOP", f.coords, "TOP", 0, 4)

  -- Separador fino encima del bloque de dinero
  f.sep = f:CreateTexture(nil, "ARTWORK")
  f.sep:SetColorTexture(0.9, 0.75, 0.2, 0.35)
  f.sep:SetHeight(1)
  f.sep:SetPoint("LEFT", f, "LEFT", 8, 0)
  f.sep:SetPoint("RIGHT", f, "RIGHT", -8, 0)

  f.money = f:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
  f.money:SetWidth(340)
  f.money:SetJustifyH("LEFT")
  f.money:SetSpacing(2)

  -- Botones de navegación
  local prev = MakeButton(f, "<", 30, function() GF:PrevStep() end)
  prev:SetPoint("BOTTOMLEFT", 8, 8)
  local done = MakeButton(f, "Hecho >", 70, function() GF:NextStep() end)
  done:SetPoint("LEFT", prev, "RIGHT", 2, 0)
  local skip = MakeButton(f, ">>", 30, function() GF:SkipStep() end)
  skip:SetPoint("LEFT", done, "RIGHT", 2, 0)
  skip:SetScript("OnEnter", function(b) GameTooltip:SetOwner(b, "ANCHOR_TOP") GameTooltip:SetText("Saltar paso (no lo marca como hecho)") GameTooltip:Show() end)
  skip:SetScript("OnLeave", GameTooltip_Hide)

  local function Info(label, key, anchor)
    local b = MakeButton(f, label, 48, function() GF:ShowInfo(key) end)
    b:SetPoint("LEFT", anchor, "RIGHT", 2, 0)
    return b
  end
  local b1 = Info("Habil.", "habilidades", skip)
  local b2 = Info("Oro", "oro", b1)
  local b3 = Info("Prof.", "prof", b2)
  Info("JcJ", "jcj", b3)

  self.main = f
  if ForeverHP_CharDB.ocultar then f:Hide() end
end

function GF:ToggleMain(show)
  if not self.main then return end
  ForeverHP_CharDB.ocultar = not show
  if show then self.main:Show() self:Refresh() else self.main:Hide() end
end

function GF:RefreshMoney()
  local f = self.main
  if not f then return end
  local money = GetMoney() or 0
  local goal, why = self:GoalInfo()
  local pct = goal > 0 and math.min(100, floor(money / goal * 100)) or 100
  local col = pct >= 100 and C.verde or (pct >= 50 and C.amarillo or C.rojo)
  f.money:SetText("Ahorro: " .. self:Money(money) .. " / " .. self:Money(goal) .. " " .. col .. "(" .. pct .. "%)" .. C.fin ..
    "\n" .. C.gris .. why .. C.fin)
end

function GF:Refresh()
  local f = self.main
  if not f then return end
  local db = ForeverHP_CharDB
  local i = db.paso
  local s = self.Ruta[i]
  if not s then return end
  db.pasoFirma = self:StepKey(i)
  local tipo = TIPOS[s.t] or TIPOS.note
  local lvl = UnitLevel("player") or 1
  local lvTxt = ""
  if s.lv then
    local diff = s.lv - lvl
    local col = diff > 2 and C.rojo or (diff < -4 and C.gris or C.verde)
    lvTxt = "  " .. col .. "(nv " .. s.lv .. ")" .. C.fin
  end
  f.counter:SetText("Paso " .. i .. "/" .. #self.Ruta)
  f.tipo:SetText(tipo[1] .. tipo[2] .. C.fin .. lvTxt)

  local txt = s.txt or ""
  if s.q then
    local name = self:QuestTitle(s.q, nil)
    if name and not name:find("^Misión ") then
      txt = txt .. "\n" .. C.amarillo .. "[" .. name .. "]" .. C.fin
    end
    local log = self.log or {}
    if s.t == "do" and log[s.q] == false then txt = txt .. "  " .. C.naranja .. "(en curso)" .. C.fin end
  end
  f.txt:SetText(txt)
  f.tip:SetText(s.tip and ("» " .. s.tip) or "")

  -- Coordenadas (si las hay) y, debajo, el bloque de dinero
  local below
  f.sep:ClearAllPoints()
  f.sep:SetPoint("RIGHT", f, "RIGHT", -8, 0)
  if s.x then
    local zone = self:MapName(s.m) or ""
    f.coords:SetText(C.azul .. zone .. " " .. s.x .. ", " .. s.y .. C.fin)
    f.coords:Show()
    f.flecha:Show()
    below = f.coords
  else
    f.coords:SetText("")
    f.coords:Hide()
    f.flecha:Hide()
    below = f.tip
  end
  f.sep:SetPoint("TOPLEFT", below, "BOTTOMLEFT", -2, -10)
  f.money:ClearAllPoints()
  f.money:SetPoint("TOPLEFT", f.sep, "BOTTOMLEFT", 2, -6)
  self:RefreshMoney()

  -- Altura = suma real de cada bloque + botones abajo
  local h = 44                                   -- título + tipo
    + f.txt:GetStringHeight() + 6
    + (s.tip and f.tip:GetStringHeight() or 0)
    + (s.x and (10 + math.max(f.coords:GetStringHeight(), 22)) or 0)
    + 10 + 1 + 6 + f.money:GetStringHeight()
    + 38                                         -- margen + fila de botones
  f:SetHeight(math.max(150, h))
end

----------------------------------------------------------------------
-- Ventana de información (texto con scroll)
----------------------------------------------------------------------
function GF:CreateInfoFrame()
  if self.info then return self.info end
  local f = CreateFrame("Frame", "ForeverHPInfo", UIParent, BACKDROP_T)
  f:SetSize(520, 460)
  SetBackdrop(f)
  Movable(f, "infoPos")
  local pos = ForeverHP_DB.infoPos
  if pos then f:SetPoint(pos[1], UIParent, pos[2], pos[3], pos[4]) else f:SetPoint("CENTER") end
  f:SetFrameStrata("HIGH")
  tinsert(UISpecialFrames, "ForeverHPInfo") -- se cierra con Escape

  f.title = f:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
  f.title:SetPoint("TOPLEFT", 12, -10)

  local close = CreateFrame("Button", nil, f, "UIPanelCloseButton")
  close:SetPoint("TOPRIGHT", 2, 2)

  local sf = CreateFrame("ScrollFrame", "ForeverHPInfoScroll", f, "UIPanelScrollFrameTemplate")
  sf:SetPoint("TOPLEFT", 12, -36)
  sf:SetPoint("BOTTOMRIGHT", -32, 40)
  local content = CreateFrame("Frame", nil, sf)
  content:SetSize(470, 10)
  sf:SetScrollChild(content)
  f.text = content:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  f.text:SetPoint("TOPLEFT")
  f.text:SetWidth(470)
  f.text:SetJustifyH("LEFT")
  f.text:SetJustifyV("TOP")
  f.text:SetSpacing(2)
  f.content = content
  f.scroll = sf

  -- pestañas
  local tabs = {
    { "Habilidades", "habilidades" }, { "Talentos", "talentos" }, { "Oro", "oro" },
    { "Profesiones", "prof" }, { "JcJ", "jcj" }, { "Clases", "clases" }, { "Novedades", "novedades" },
  }
  local last
  for _, t in ipairs(tabs) do
    local b = MakeButton(f, t[1], 70, function() GF:ShowInfo(t[2]) end)
    if last then b:SetPoint("LEFT", last, "RIGHT", 2, 0) else b:SetPoint("BOTTOMLEFT", 10, 10) end
    last = b
  end

  self.info = f
  return f
end

local function Join(lines) return table.concat(lines, "\n") end

function GF:InfoText(key)
  local class = self:PlayerClass()
  local data = self.Clases[class]
  local lvl = UnitLevel("player") or 1
  if key == "habilidades" then
    local out = { C.oro .. "HABILIDADES DE " .. (data and data.nombre or class):upper() .. C.fin, " " }
    if data and data.resumen then tinsert(out, data.resumen) tinsert(out, " ") end
    if not data or #data.skills == 0 then
      tinsert(out, "Aún no hay lista detallada para tu clase. Regla general:")
      tinsert(out, C.verde .. "SÍ:" .. C.fin .. " rangos nuevos de tus ataques/curaciones principales, controles (aturdir, miedo) e inmunidades.")
      tinsert(out, C.rojo .. "NO:" .. C.fin .. " resistencias, detectar criaturas, rangos de hechizos que no usas.")
      return Join(out)
    end
    local grupos = { { "SI", C.verde, "COMPRAR" }, { "OPC", C.amarillo, "OPCIONAL (solo si lo necesitas)" }, { "NO", C.rojo, "NO COMPRAR" } }
    for _, g in ipairs(grupos) do
      tinsert(out, g[2] .. "== " .. g[3] .. " ==" .. C.fin)
      for _, sk in ipairs(data.skills) do
        if sk.v == g[1] then
          local name = self:SpellName(sk.id) or ("Hechizo " .. sk.id)
          tinsert(out, g[2] .. "• " .. name .. C.fin .. " - " .. sk.why)
        end
      end
      tinsert(out, " ")
    end
    tinsert(out, C.gris .. "Al abrir tu entrenador el addon te lo marca y puede comprar lo recomendado por ti." .. C.fin)
    return Join(out)
  elseif key == "talentos" then
    local out = { C.oro .. "TALENTOS" .. C.fin, " " }
    if data and data.talentos then for _, l in ipairs(data.talentos) do tinsert(out, l) end end
    tinsert(out, " ")
    tinsert(out, C.gris .. "Nivel 10 = 1er talento; luego 1 punto por nivel. A 40, doble especialización (50g)." .. C.fin)
    return Join(out)
  elseif key == "oro" then
    local out = { C.oro .. "ORO Y AHORRO (tu nivel: " .. lvl .. ")" .. C.fin, " " }
    local tip = self:GoldTipForLevel(lvl)
    if tip then tinsert(out, C.verde .. "AHORA MISMO:" .. C.fin .. " " .. tip) tinsert(out, " ") end
    local goal, why = self:GoalInfo()
    tinsert(out, "Tienes " .. self:Money(GetMoney()) .. ". Objetivo: " .. self:Money(goal) .. " (" .. why .. ")")
    tinsert(out, " ")
    for _, l in ipairs(self.Oro.reglas) do tinsert(out, l) end
    tinsert(out, " ")
    tinsert(out, C.oro .. "FARMEOS POR NIVEL" .. C.fin)
    for _, fm in ipairs(self.Oro.farmeos) do
      local col = (lvl >= fm.min and lvl <= fm.max) and C.verde or C.gris
      tinsert(out, col .. "Nv " .. fm.min .. "-" .. fm.max .. ":" .. C.fin .. " " .. fm.txt)
    end
    return Join(out)
  elseif key == "prof" then
    return Join(self.Profesiones.texto)
  elseif key == "jcj" then
    local out = {}
    for _, l in ipairs(self.JcJ.general) do tinsert(out, l) end
    tinsert(out, " ")
    local cl = self.JcJ[class]
    if cl then for _, l in ipairs(cl) do tinsert(out, l) end end
    return Join(out)
  elseif key == "clases" then
    return Join(self.ClasesTexto)
  elseif key == "novedades" then
    return Join(self.Novedades)
  end
  return ""
end

local TITULOS = { habilidades="Habilidades", talentos="Talentos", oro="Oro", prof="Profesiones", jcj="JcJ", clases="Clases", novedades="Novedades de Forever" }

function GF:ShowInfo(key)
  local f = self:CreateInfoFrame()
  f.title:SetText(C.oro .. "ForeverHumans" .. C.fin .. C.azul .. "&Paladins" .. C.fin .. " - " .. (TITULOS[key] or key))
  f.text:SetText(self:InfoText(key))
  f.content:SetHeight(f.text:GetStringHeight() + 20)
  f.scroll:SetVerticalScroll(0)
  f:Show()
end
