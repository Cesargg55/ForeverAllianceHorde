-- ForeverHumans&Paladins - Oro: farmeos por nivel y reglas de ahorro
local _, GF = ...

GF.Oro.farmeos = {
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

GF.Oro.reglas = {
  "|cff33ff66AHORRAR (lo más importante para un novato)|r",
  "1. NUNCA compres armas ni armaduras al vendedor. Las misiones te dan equipo gratis cada pocos niveles.",
  "2. NO compres en la casa de subastas para subir. Excepción: una buena arma de dos manos cada ~10 niveles si tu daño es muy bajo.",
  "3. NO compres comida ni agua: usa la que sueltan los bichos o cocínala tú (Cocina es gratis y da +Espíritu/+Aguante).",
  "4. Compra solo las habilidades que el addon marca en VERDE. Los rangos que no usas cuestan cientos de oro en total.",
  "5. Bolsas: no las compres al vendedor. Pide bolsas de lino/lana en subasta (baratas) o hazlas con Sastrería de un amigo.",
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

function GF:GoldTipForLevel(lvl)
  local best
  for _, f in ipairs(self.Oro.farmeos) do
    if lvl >= f.min and lvl <= f.max then best = f end
  end
  return best and best.txt
end
