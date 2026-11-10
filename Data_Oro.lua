-- ForeverAlliance&Horde - Oro: farmeos por nivel y reglas de ahorro
-- farmeos[Facción] = zonas de tu facción · farmeos[CLASE] = trucos de esa clase (se mezclan)
-- reglasClase[CLASE] = reglas extra que salen arriba del todo
local _, GF = ...

GF.Oro.farmeos = {}
GF.Oro.farmeos.Alliance = {
  { min=1,  max=14, txt="Recolecta TODO (cobre, Flor de paz, Hojaplata). Vende tela de lino en subasta. Desuella si tienes Desuello." },
  { min=10, max=20, txt="Mina de cobre en Elwynn/Páramos/Loch Modan. Vende Mena/Barra de cobre y Piedra en bruto: los herreros e ingenieros la necesitan." },
  { min=15, max=25, txt="Lana: Defias y gnolls de Bosque del Ocaso y Crestagrana. Mena de estaño y Brezospina/Raíz de tierra: siempre se venden." },
  { min=20, max=30, txt="Mazmorras de Ventormenta y Minas de la Muerte: azules ligados al equipar (BoE) = oro en subasta. Hierro y Hierba cardenal." },
  { min=30, max=40, txt="Seda y Tejido mágico en Vega de Tuercespina y Arathi. Mena de hierro, Mitrilo (a partir de ~35). Hierbas: Sangrerregia y las de nivel 30-40 (mira cuáles se venden caras en subasta)." },
  { min=35, max=45, txt="Riverglades (NUEVA): las zonas nuevas tienen menos recolectores al principio de la expansión = nodos libres." },
  { min=40, max=50, txt="Elementales de tierra en Tierras Inhóspitas (Tierra elemental se vende muy bien). Mitrilo y hierbas de 40-50. Tanaris: Tejido mágico." },
  { min=45, max=55, txt="Tejido rúnico empieza ~48. Hinterlands y Feralas: Tejido mágico + cuero grueso. Torio en Un'Goro y Garganta de Fuego." },
  { min=50, max=60, txt="Sátiros Jadefire en Frondavil (runas demoníacas + tejido vil). Furbolgs Fauces de Invierno (Cuna del Invierno): E'ko para todo el grupo." },
  { min=55, max=60, txt="Mazmorras 55+: Tarnished Undermine Reals -> Bahía del Botín. Mano de Tyr (Tierras de la Peste del Este): tejido rúnico y plata. Torio + Flor de la peste + Loto negro." },
}
GF.Oro.farmeos.Horde = {
  { min=1,  max=14, txt="Recolecta TODO (cobre, Flor de paz, Hojaplata) en Tirisfal y Argénteos. Vende el lino en la subasta de Entrañas (o guárdalo si vas a hacer Sastrería)." },
  { min=10, max=20, txt="Cobre en Argénteos y Los Baldíos. Vende Mena/Barra de cobre y Piedra en bruto en la subasta: siempre hay herreros e ingenieros comprando." },
  { min=15, max=25, txt="Lana: humanos de Argénteos (Molino Ámbar), Trabalomas y Sierra Espolón. Mena de estaño, Brezospina y Raíz de tierra: siempre se venden." },
  { min=20, max=30, txt="Colmillo Oscuro y Cuevas de los Lamentos: azules ligados al equipar (BoE) = oro en subasta. Hierro y Hierba cardenal." },
  { min=26, max=40, txt="Monasterio Escarlata (Tirisfal): tela de seda, grises y azules BoE para la subasta." },
  { min=30, max=40, txt="Seda y Tejido mágico en Arathi, Vega de Tuercespina y Desolace. Mena de hierro y Mitrilo (~35). Hierbas: Sangrerregia y las de nivel 30-40 (mira cuáles se venden caras)." },
  { min=35, max=45, txt="Riverglades (NUEVA): las zonas nuevas tienen menos recolectores al principio de la expansión = nodos libres." },
  { min=40, max=50, txt="Elementales de tierra en Tierras Inhóspitas (Tierra elemental se vende muy bien). Tejido mágico en Tanaris." },
  { min=45, max=55, txt="Tejido rúnico empieza ~48. Tierras del Interior y Feralas: Tejido mágico. Torio en Un'Goro y Garganta de Fuego." },
  { min=50, max=60, txt="Sátiros Jadefire en Frondavil (runas demoníacas + tejido vil). Furbolgs Fauces de Invierno (Cuna del Invierno)." },
  { min=55, max=60, txt="Mazmorras 55+: Tarnished Undermine Reals -> Bahía del Botín. Tierras de la Peste: tejido rúnico. Torio + Flor de la peste + Loto negro." },
}
GF.Oro.farmeos.MAGE = {
  { min=22, max=30, txt="MAGO EN ÁREA: con Ventisca y Nova de Escarcha junta grupos de bichos fáciles (5-8) y mátalos de golpe. Ahorras tiempo y la tela/grises se acumulan rápido." },
  { min=30, max=40, txt="MAGO: haz en área tú solo mazmorras que ya superas de nivel (p. ej. Monasterio Escarlata: Cementerio y Biblioteca). Tela, grises y azules BoE." },
  { min=40, max=50, txt="PORTALES: ponte en tu capital y ofrece portales en el chat de comercio (la gente da propina)." },
  { min=45, max=60, txt="MAGO: farmeo en área de bichos 2-3 niveles por debajo de ti. Eres la clase que más fácil farmea en solitario: aprovéchalo." },
}

GF.Oro.reglas = {
  "|cff33ff66AHORRAR (lo más importante para un novato)|r",
  "1. NUNCA compres armas ni armaduras al vendedor. Las misiones te dan equipo gratis cada pocos niveles.",
  "2. NO compres en la casa de subastas para subir. Excepción: una buena arma cada ~10 niveles si tu daño es muy bajo.",
  "3. NO compres comida ni agua: usa la que sueltan los bichos o cocínala tú (Cocina es gratis y da +Espíritu/+Aguante).",
  "4. Compra solo las habilidades que el addon marca en VERDE. Los rangos que no usas cuestan cientos de oro en total.",
  "5. Bolsas: no las compres al vendedor. Pide bolsas de lino/lana en subasta (baratas) o hazlas con Sastrería.",
  "6. No aprendas profesiones de fabricación caras antes de nv 40. Recolecta y vende.",
  "7. Vende los grises SIEMPRE (el addon lo hace solo). Los blancos: mira si son de profesión antes de venderlos.",
  "8. NO te equipes azules/morados BoE que no necesitas: véndelos en subasta (pueden valer cientos de oro).",
  "9. Repara solo en el vendedor; no mueras tontamente (cada muerte = -10% durabilidad).",
  "10. Usa la piedra de hogar y vuelos solo cuando ahorren mucho tiempo. Correr es gratis.",
  " ",
  "|cffffd100OBJETIVOS DE DINERO (aprox.)|r",
  "  Nivel 20: ~5-10g  ·  Nivel 30: ~30-40g  ·  Nivel 40: ~100g (montura) + 50g doble espe opcional",
  "  Nivel 60: ~1000g montura rápida. Habilidades 40-60 cuestan bastante: guarda margen.",
  "  Paladín y Brujo: montura de nv40 por misión de clase (gratis). Ese dinero va directo a la de 60.",
  " ",
  "|cff3fbfffNUEVO EN FOREVER QUE DA DINERO|r",
  "  - Tarnished Undermine Reals: sueltan los jefes de mazmorras 55+, se cambian en Bahía del Botín.",
  "  - Cajas de botín: llénalas y entrégalas para reputación y Merchant's Favor (necesario para recetas altas).",
  "  - Puntos de Legado (Legacy Points): subir profesiones principales de fabricación da puntos de cuenta.",
  "  - Piedras de afilar del herrero valen más: en Forever se pueden usar junto a venenos/efectos de tótem.",
  "  - Ingeniería: las granadas se venden a no ingenieros.",
}

GF.Oro.reglasClase = {
  MAGE = {
    "|cffa335eeMAGO|r",
    "  - Comida y agua: CONJÚRALAS siempre (Conjurar agua / Conjurar comida). Nunca las compres.",
    "  - Teletransportes (nv20) en vez de la piedra de hogar y vuelos largos.",
    "  - No compres rangos de Bola de Fuego ni Agostar si vas de Escarcha.",
    "  - Tu montura NO es gratis: ahorra desde el nivel 30.",
    " ",
  },
  PALADIN = {
    "|cfff58cbaPALADÍN|r",
    "  - Te curas solo: no gastes en vendas ni pociones subiendo.",
    "  - Montura de nv40 GRATIS (misión de clase): todo lo que ahorres va a la de 60.",
    " ",
  },
}

-- Consejo de farmeo para tu nivel (de tu facción y de tu clase; gana el más específico)
function GF:GoldFarms()
  local list = {}
  for _, f in ipairs(self.Oro.farmeos[self:Faction()] or {}) do table.insert(list, f) end
  for _, f in ipairs(self.Oro.farmeos[self:PlayerClass() or ""] or {}) do table.insert(list, f) end
  table.sort(list, function(a, b) if a.min ~= b.min then return a.min < b.min end return a.max < b.max end)
  return list
end

function GF:GoldTipForLevel(lvl)
  local best
  for _, f in ipairs(self:GoldFarms()) do
    if lvl >= f.min and lvl <= f.max then best = f end
  end
  return best and best.txt
end
