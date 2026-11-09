-- ForeverHumans&Paladins - Panel de Progreso: por dónde vas, qué has hecho y qué te has saltado
local _, GF = ...
local C = GF.C
local BACKDROP_T = BackdropTemplateMixin and "BackdropTemplate" or nil

local ICON_OK   = "|TInterface\\RaidFrame\\ReadyCheck-Ready:14:14|t"
local ICON_NO   = "|TInterface\\RaidFrame\\ReadyCheck-NotReady:14:14|t"
local ICON_WAIT = "|TInterface\\RaidFrame\\ReadyCheck-Waiting:14:14|t"
local ICON_HERE = "|TInterface\\ChatFrame\\ChatFrameExpandArrow:14:14|t"

----------------------------------------------------------------------
-- Datos
----------------------------------------------------------------------
-- Devuelve un resumen del estado de todas las misiones de la guía
function GF:ProgressData()
  local db = ForeverHP_CharDB
  local cur = db.paso
  local d = { total = 0, done = 0, secs = {}, skippedReady = {}, blocked = {}, inLog = {} }
  for si, sec in ipairs(self.secs or {}) do d.secs[si] = { name = sec.name, first = sec.first, total = 0, done = 0 } end

  for q, first in pairs(self.firstStepOf or {}) do
    local st, extra = self:QStatus(q)
    local si = self:Section(first)
    local sec = d.secs[si]
    if st ~= "na" then
      d.total = d.total + 1
      if sec then sec.total = sec.total + 1 end
      if st == "done" then
        d.done = d.done + 1
        if sec then sec.done = sec.done + 1 end
      end
    end
    if st == "log" then
      table.insert(d.inLog, { q = q, i = first })
    elseif first < cur and st == "ready" then
      table.insert(d.skippedReady, { q = q, i = first })
    elseif first < cur and (st == "level" or st == "pre") then
      table.insert(d.blocked, { q = q, i = first, st = st, extra = extra })
    end
  end
  local byStep = function(a, b) return a.i < b.i end
  table.sort(d.skippedReady, byStep)
  table.sort(d.blocked, byStep)
  table.sort(d.inLog, byStep)
  return d
end

----------------------------------------------------------------------
-- Ventana
----------------------------------------------------------------------
local function CreatePanel()
  local f = CreateFrame("Frame", "ForeverHPProgress", UIParent, BACKDROP_T)
  f:SetSize(440, 500)
  if f.SetBackdrop then
    f:SetBackdrop({ bgFile = "Interface\\Tooltips\\UI-Tooltip-Background", edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
      tile = true, tileSize = 16, edgeSize = 14, insets = { left = 3, right = 3, top = 3, bottom = 3 } })
    f:SetBackdropColor(0.05, 0.05, 0.08, 0.95)
    f:SetBackdropBorderColor(0.9, 0.75, 0.2, 1)
  end
  f:SetFrameStrata("HIGH")
  f:SetMovable(true) f:EnableMouse(true) f:RegisterForDrag("LeftButton") f:SetClampedToScreen(true)
  f:SetScript("OnDragStart", f.StartMoving)
  f:SetScript("OnDragStop", function(self)
    self:StopMovingOrSizing()
    local p, _, rp, x, y = self:GetPoint()
    ForeverHP_DB.progPos = { p, rp, x, y }
  end)
  local pos = ForeverHP_DB.progPos
  if pos then f:SetPoint(pos[1], UIParent, pos[2], pos[3], pos[4]) else f:SetPoint("CENTER", -200, 0) end
  tinsert(UISpecialFrames, "ForeverHPProgress")

  f.title = f:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
  f.title:SetPoint("TOPLEFT", 12, -10)
  f.title:SetText(C.oro .. "Progreso" .. C.fin)
  local close = CreateFrame("Button", nil, f, "UIPanelCloseButton")
  close:SetPoint("TOPRIGHT", 2, 2)

  f.where = f:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
  f.where:SetPoint("TOPLEFT", 12, -36)
  f.where:SetWidth(410)
  f.where:SetJustifyH("LEFT")

  -- Barra de progreso total
  f.bar = CreateFrame("StatusBar", nil, f)
  f.bar:SetPoint("TOPLEFT", 12, -76)
  f.bar:SetSize(410, 16)
  f.bar:SetStatusBarTexture("Interface\\TargetingFrame\\UI-StatusBar")
  f.bar:SetStatusBarColor(0.2, 0.75, 0.3)
  f.bar:SetMinMaxValues(0, 1)
  local bg = f.bar:CreateTexture(nil, "BACKGROUND")
  bg:SetAllPoints()
  bg:SetColorTexture(0, 0, 0, 0.5)
  f.barText = f.bar:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  f.barText:SetPoint("CENTER")

  local sf = CreateFrame("ScrollFrame", "ForeverHPProgressScroll", f, "UIPanelScrollFrameTemplate")
  sf:SetPoint("TOPLEFT", 12, -100)
  sf:SetPoint("BOTTOMRIGHT", -32, 12)
  local content = CreateFrame("Frame", nil, sf)
  content:SetSize(400, 10)
  sf:SetScrollChild(content)
  f.content, f.scroll = content, sf
  f.lines, f.buttons = {}, {}
  return f
end

-- Filas reutilizables
local function Reset(f) f.y, f.nl, f.nb = 0, 0, 0 end

local function Line(f, text, indent, btnText, onClick)
  f.nl = f.nl + 1
  local fs = f.lines[f.nl]
  if not fs then
    fs = f.content:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    fs:SetJustifyH("LEFT")
    f.lines[f.nl] = fs
  end
  indent = indent or 0
  fs:ClearAllPoints()
  fs:SetPoint("TOPLEFT", f.content, "TOPLEFT", indent, -f.y)
  fs:SetWidth(400 - indent - (btnText and 46 or 0))
  fs:SetText(text)
  fs:Show()
  local h = math.max(16, fs:GetStringHeight())
  if btnText then
    f.nb = f.nb + 1
    local b = f.buttons[f.nb]
    if not b then
      b = CreateFrame("Button", nil, f.content, "UIPanelButtonTemplate")
      b:SetSize(42, 18)
      f.buttons[f.nb] = b
    end
    b:ClearAllPoints()
    b:SetPoint("TOPRIGHT", f.content, "TOPRIGHT", 0, -f.y + 1)
    b:SetText(btnText)
    b:SetScript("OnClick", onClick)
    b:Show()
    h = math.max(h, 20)
  end
  f.y = f.y + h + 2
end

local function Gap(f, px) f.y = f.y + (px or 8) end

local function Finish(f)
  for i = f.nl + 1, #f.lines do f.lines[i]:Hide() end
  for i = f.nb + 1, #f.buttons do f.buttons[i]:Hide() end
  f.content:SetHeight(f.y + 10)
end

function GF:RefreshProgress()
  local f = self.progress
  if not f or not f:IsShown() then return end
  local db = ForeverHP_CharDB
  local d = self:ProgressData()
  local cur = db.paso
  local sec = self.secs and self.secs[self:Section(cur)]

  f.where:SetText(string.format("%sVas por:%s paso %d de %d  ·  nivel %d\n%sZona:%s %s",
    C.oro, C.fin, cur, #self.Ruta, self:Level(), C.oro, C.fin, sec and sec.name or "?"))
  local pct = d.total > 0 and d.done / d.total or 0
  f.bar:SetValue(pct)
  f.barText:SetText(string.format("Misiones de la guía: %d / %d hechas (%d%%)", d.done, d.total, floor(pct * 100 + 0.5)))

  Reset(f)
  -- 1) Saltadas que ya puedes hacer
  Line(f, C.naranja .. "TE HAS SALTADO (puedes hacerlas ya): " .. #d.skippedReady .. C.fin)
  if #d.skippedReady == 0 then
    Line(f, C.gris .. "Nada. ¡Vas al día!" .. C.fin, 8)
  end
  for _, e in ipairs(d.skippedReady) do
    local secName = self.secs[self:Section(e.i)] and self.secs[self:Section(e.i)].name or ""
    Line(f, ICON_NO .. " " .. self:QName(e.q) .. C.gris .. "  (paso " .. e.i .. ", " .. secName .. ")" .. C.fin, 8,
      "Ir", function() GF:JumpTo(e.i) end)
  end
  Gap(f)

  -- 2) Pendientes que aún no puedes coger
  Line(f, C.amarillo .. "PENDIENTES (aún no puedes cogerlas): " .. #d.blocked .. C.fin)
  if #d.blocked == 0 then Line(f, C.gris .. "Ninguna." .. C.fin, 8) end
  for _, e in ipairs(d.blocked) do
    local why
    if e.st == "level" then
      why = "necesitas nivel " .. tostring(e.extra)
    else
      why = "antes haz «" .. self:QName(e.extra) .. "»"
    end
    Line(f, ICON_WAIT .. " " .. self:QName(e.q) .. C.gris .. "  - " .. why .. " (paso " .. e.i .. ")" .. C.fin, 8)
  end
  Gap(f)

  -- 3) En tu diario
  Line(f, C.azul .. "EN TU DIARIO: " .. #d.inLog .. C.fin)
  for _, e in ipairs(d.inLog) do
    local comp = self.log and self.log[e.q] == true
    Line(f, (comp and ICON_OK or ICON_WAIT) .. " " .. self:QName(e.q) .. C.gris ..
      (comp and "  - ¡lista para entregar!" or "  - en curso") .. C.fin, 8, "Ir", function() GF:JumpTo(e.i) end)
  end
  Gap(f)

  -- 4) Zonas
  Line(f, C.oro .. "ZONAS DE LA RUTA" .. C.fin)
  local curSec = self:Section(cur)
  for si, s in ipairs(d.secs) do
    local icon, col
    if si < curSec then
      icon, col = (s.done >= s.total and ICON_OK or ICON_NO), (s.done >= s.total and C.verde or C.naranja)
    elseif si == curSec then
      icon, col = ICON_HERE, C.amarillo
    else
      icon, col = "    ", C.gris
    end
    local txt = string.format("%s %s%s%s  %d/%d", icon, col, s.name, C.fin, s.done, s.total)
    if si == curSec then txt = txt .. C.amarillo .. "  <- estás aquí" .. C.fin end
    Line(f, txt, 8, si ~= curSec and "Ir" or nil, si ~= curSec and function() GF:JumpTo(s.first) end or nil)
  end
  Finish(f)
end

function GF:ToggleProgress(show)
  if not self.progress then self.progress = CreatePanel() end
  if show == nil then show = not self.progress:IsShown() end
  if show then
    self.progress:Show()
    self:ScanQuestLog()
    self:RefreshProgress()
  else
    self.progress:Hide()
  end
end

-- Número de misiones saltadas que ya puedes hacer (para el botón de la ventana principal)
function GF:SkippedReadyCount()
  local cur, n = ForeverHP_CharDB.paso, 0
  for q, first in pairs(self.firstStepOf or {}) do
    if first < cur and self:QStatus(q) == "ready" then n = n + 1 end
  end
  return n
end
