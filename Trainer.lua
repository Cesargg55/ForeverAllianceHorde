-- ForeverAlliance&Horde - Ayudante del entrenador: marca qué comprar y qué NO, y compra lo recomendado
local _, GF = ...
local C = GF.C
local BACKDROP_T = BackdropTemplateMixin and "BackdropTemplate" or nil

-- nombre (en tu idioma, minúsculas) -> entrada de Data_Clases
function GF:BuildSkillIndex()
  self.skillIndex = {}
  local data = self.Clases[self:PlayerClass()]
  if not data then return end
  for _, sk in ipairs(data.skills) do
    local name = self:SpellName(sk.id)
    if name then self.skillIndex[name:lower()] = sk end
  end
end

local function Verdict(name)
  if not name or not GF.skillIndex then return nil end
  return GF.skillIndex[name:lower()]
end

local function IsTradeTrainer()
  return IsTradeskillTrainer and IsTradeskillTrainer()
end

local function Scan()
  local list = {}
  local n = GetNumTrainerServices and GetNumTrainerServices() or 0
  for i = 1, n do
    local name, rank, category = GetTrainerServiceInfo(i)
    if name and category == "available" then
      local cost = GetTrainerServiceCost and GetTrainerServiceCost(i) or 0
      local sk = Verdict(name)
      tinsert(list, { i = i, name = name, rank = rank or "", cost = cost or 0, sk = sk })
    end
  end
  return list
end

local function Panel()
  if GF.trainerPanel then return GF.trainerPanel end
  local f = CreateFrame("Frame", "ForeverAHTrainer", UIParent, BACKDROP_T)
  f:SetSize(330, 380)
  if f.SetBackdrop then
    f:SetBackdrop({ bgFile = "Interface\\Tooltips\\UI-Tooltip-Background", edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
      tile = true, tileSize = 16, edgeSize = 14, insets = { left = 3, right = 3, top = 3, bottom = 3 } })
    f:SetBackdropColor(0.05, 0.05, 0.08, 0.95)
    f:SetBackdropBorderColor(0.9, 0.75, 0.2, 1)
  end
  f:SetFrameStrata("HIGH")
  f:SetMovable(true) f:EnableMouse(true) f:RegisterForDrag("LeftButton")
  f:SetScript("OnDragStart", f.StartMoving) f:SetScript("OnDragStop", f.StopMovingOrSizing)

  f.title = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
  f.title:SetPoint("TOPLEFT", 10, -8)
  f.title:SetText(C.oro .. "Guía: ¿qué compro?" .. C.fin)

  local sf = CreateFrame("ScrollFrame", "ForeverAHTrainerScroll", f, "UIPanelScrollFrameTemplate")
  sf:SetPoint("TOPLEFT", 10, -28)
  sf:SetPoint("BOTTOMRIGHT", -30, 40)
  local content = CreateFrame("Frame", nil, sf)
  content:SetSize(290, 10)
  sf:SetScrollChild(content)
  f.text = content:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
  f.text:SetPoint("TOPLEFT")
  f.text:SetWidth(290)
  f.text:SetJustifyH("LEFT")
  f.text:SetSpacing(2)
  f.content = content

  f.buy = CreateFrame("Button", nil, f, "UIPanelButtonTemplate")
  f.buy:SetSize(220, 22)
  f.buy:SetPoint("BOTTOM", 0, 10)
  f.buy:SetScript("OnClick", function() GF:BuyRecommended() end)

  GF.trainerPanel = f
  return f
end

function GF:OnTrainer(event)
  if IsTradeTrainer() then
    if event == "TRAINER_SHOW" then
      self:Print("Entrenador de profesión. Consejos en " .. C.amarillo .. "/guia prof" .. C.fin ..
        ". Aprende solo hasta el rango que puedas subir ahora (Aprendiz 75, Oficial 150, Experto 225, Artesano 300).")
    end
    return
  end
  local f = Panel()
  f:ClearAllPoints()
  if ClassTrainerFrame and ClassTrainerFrame:IsShown() then
    f:SetPoint("TOPLEFT", ClassTrainerFrame, "TOPRIGHT", -30, -12)
  else
    f:SetPoint("LEFT", UIParent, "CENTER", 120, 0)
  end

  local list = Scan()
  local si, opc, no, unk = {}, {}, {}, {}
  local total = 0
  for _, e in ipairs(list) do
    local line = e.name .. (e.rank ~= "" and (" (" .. e.rank .. ")") or "") .. " - " .. self:Money(e.cost)
    if e.sk and e.sk.v == "SI" then
      tinsert(si, C.verde .. "• " .. line .. C.fin .. "\n   " .. C.gris .. e.sk.why .. C.fin)
      total = total + e.cost
    elseif e.sk and e.sk.v == "OPC" then
      tinsert(opc, C.amarillo .. "• " .. line .. C.fin .. "\n   " .. C.gris .. e.sk.why .. C.fin)
    elseif e.sk and e.sk.v == "NO" then
      tinsert(no, C.rojo .. "• " .. line .. C.fin .. "\n   " .. C.gris .. e.sk.why .. C.fin)
    else
      tinsert(unk, C.blanco .. "• " .. line .. C.fin)
    end
  end

  local out = {}
  if #list == 0 then
    tinsert(out, "No hay nada nuevo que aprender ahora. ¡Ahorras dinero!")
  end
  if #si > 0 then tinsert(out, C.verde .. "COMPRAR" .. C.fin) for _, l in ipairs(si) do tinsert(out, l) end tinsert(out, " ") end
  if #opc > 0 then tinsert(out, C.amarillo .. "OPCIONAL" .. C.fin) for _, l in ipairs(opc) do tinsert(out, l) end tinsert(out, " ") end
  if #no > 0 then tinsert(out, C.rojo .. "NO COMPRAR" .. C.fin) for _, l in ipairs(no) do tinsert(out, l) end tinsert(out, " ") end
  if #unk > 0 then
    tinsert(out, C.blanco .. "SIN DATOS (regla: compra si es tu ataque/curación principal)" .. C.fin)
    for _, l in ipairs(unk) do tinsert(out, l) end
  end
  f.text:SetText(table.concat(out, "\n"))
  f.content:SetHeight(f.text:GetStringHeight() + 10)

  if total > 0 then
    f.buy:SetText("Comprar recomendadas (" .. self:Money(total) .. ")")
    f.buy:Enable()
  else
    f.buy:SetText("Nada recomendado que comprar")
    f.buy:Disable()
  end
  f:Show()

  -- Compra encadenada (una por actualización del entrenador)
  if self.buying and event == "TRAINER_UPDATE" then
    C_Timer.After(0.2, function() GF:BuyNext() end)
  end
end

function GF:BuyRecommended()
  self.buying = true
  self.buyCount = 0
  self:BuyNext()
end

function GF:BuyNext()
  if not self.buying then return end
  for _, e in ipairs(Scan()) do
    if e.sk and e.sk.v == "SI" then
      if GetMoney() < e.cost then
        self:Print(C.rojo .. "No tienes oro para " .. e.name .. "." .. C.fin)
      else
        self.buyCount = (self.buyCount or 0) + 1
        if self.buyCount > 40 then break end
        BuyTrainerService(e.i)
        return -- esperamos a TRAINER_UPDATE para la siguiente
      end
    end
  end
  self.buying = false
  self:Print("Compradas las habilidades recomendadas.")
end

function GF:OnTrainerClosed()
  self.buying = false
  if self.trainerPanel then self.trainerPanel:Hide() end
end
