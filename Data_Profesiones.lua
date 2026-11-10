-- ForeverAlliance&Horde - Profesiones: qué coger, qué recetas comprar, qué craftear
-- textos[plan] = texto · porClase[CLASE] = qué plan usa esa clase (si no está, ARMADURA)
local _, GF = ...

GF.Profesiones.porClase = {
  PALADIN = "ARMADURA", WARRIOR = "ARMADURA", SHAMAN = "ARMADURA", HUNTER = "ARMADURA", ROGUE = "ARMADURA", DRUID = "ARMADURA",
  MAGE = "TELA", PRIEST = "TELA", WARLOCK = "TELA",
}

GF.Profesiones.textos = {}
GF.Profesiones.textos.ARMADURA = {
  "|cffffd100PLAN DE PROFESIONES (Paladín, Guerrero y clases con armadura; foco en oro + JcJ)|r",
  " ",
  "|cff33ff66FASE 1 (nivel 1-40): MINERÍA + HERBORISTERÍA|r",
  "  - Las dos son de recolección: cero gasto, todo lo que coges se vende.",
  "  - Sube su nivel a la vez que subes de nivel: recoge cada nodo que veas de camino.",
  "  - Minería te sirve luego para Herrería o Ingeniería (no la quites nunca).",
  "  - Compra: Pico de minero (barato) en el vendedor de comercio. Herboristería no necesita herramienta.",
  "  - Cuero o malla (Pícaro, Cazador, Druida, Chamán): cambia Herboristería por DESUELLO y luego Herrería por PELETERÍA.",
  " ",
  "|cff33ff66SECUNDARIAS (todas, son baratas y útiles)|r",
  "  - PRIMEROS AUXILIOS: vendas = curarte sin gastar maná ni pociones. En Forever además hace la Poción de sanación menor.",
  "  - COCINA: comida con +Aguante/+Espíritu. Cocina lo que sueltan los bichos.",
  "  - PESCA: comida + algunos pescados valen mucho en subasta.",
  "  - NUEVO: 'Camping' da bonificaciones de profesión desde nivel 20 de habilidad.",
  "  - NUEVO: 'Dedicated Study' (1 vez al día) sube +1 tu profesión más baja. ¡Úsalo cada día!",
  " ",
  "|cff3fbfffFASE 2 (nivel 40-60): elige UNA|r",
  "  A) |cff33ff66MINERÍA + INGENIERÍA (la mejor para JcJ)|r",
  "     Bombas, redes, granadas, dinamita = aturdir/inmovilizar en JcJ. Las granadas se venden a no-ingenieros.",
  "     Recetas que SÍ: Pólvora (todas), Dinamita, Granadas de hierro, Bomba explosiva, Red (Net-o-Matic),",
  "     Muñeco objetivo, Sombrero/gafas de ingeniero con buenas stats.",
  "     Recetas que NO: mascotas mecánicas, fuegos artificiales, objetos decorativos.",
  "     A nivel 200: Goblin (cargas de zapador, más daño) o Gnomo (más control y utilidad). JcJ clásico: Goblin.",
  "  B) |cff33ff66MINERÍA + HERRERÍA (la mejor para tu armadura de placas)|r",
  "     En Forever los fabricantes de armadura tienen patrones NUEVOS ligados al recoger (BoP): equipo solo para ti.",
  "     Recetas que SÍ: Piedras de afilar (TODAS: en Forever valen más), Contrapesos, piezas de placas BoP nuevas.",
  "     Recetas que NO: armas y armaduras normales para subir habilidad que nadie compra; vende solo lo que tenga demanda.",
  "     Recetas altas piden Merchant's Favor + reputación (cajas de botín).",
  "  C) |cff33ff66HERBORISTERÍA + ALQUIMIA (la mejor para oro estable)|r",
  "     Pociones de sanación/maná, elixires y frascos: SIEMPRE se venden, sobre todo a 60 y en JcJ.",
  "     Recetas que SÍ: Poción de sanación (todas), Poción de maná, Elixir de agilidad/fuerza, Poción de acción libre.",
  "     Recetas que NO: aceites raros, pociones de agua/sigilo que nadie compra.",
}

GF.Profesiones.textos.TELA = {
  "|cffffd100PLAN DE PROFESIONES (Mago, Sacerdote, Brujo: clases de tela; foco en oro + JcJ)|r",
  " ",
  "|cff33ff66FASE 1 (nivel 1-40): HERBORISTERÍA + MINERÍA|r",
  "  - Las dos son de recolección: cero gasto, todo lo que coges se vende.",
  "  - Sube su nivel a la vez que subes de nivel: recoge cada nodo que veas de camino.",
  "  - Compra: Pico de minero (barato) en el vendedor de comercio. Herboristería no necesita herramienta.",
  "  - Alternativa: HERBORISTERÍA + SASTRERÍA. Usas tu propia tela para hacer bolsas y tu equipo de tela.",
  " ",
  "|cff33ff66SECUNDARIAS (todas, son baratas y útiles)|r",
  "  - PRIMEROS AUXILIOS: vendas = curarte sin gastar maná. El mago no se cura: ¡imprescindible! En Forever además hace la Poción de sanación menor.",
  "  - COCINA: comida con +Aguante/+Espíritu (la conjurada no da bonificaciones).",
  "  - PESCA: algunos pescados valen mucho en subasta.",
  "  - NUEVO: 'Camping' da bonificaciones de profesión desde nivel 20 de habilidad.",
  "  - NUEVO: 'Dedicated Study' (1 vez al día) sube +1 tu profesión más baja. ¡Úsalo cada día!",
  " ",
  "|cff3fbfffFASE 2 (nivel 40-60): elige UNA|r",
  "  A) |cff33ff66SASTRERÍA + ENCANTAMIENTO (la clásica de las clases de tela)|r",
  "     Sastrería: bolsas (siempre se venden), tu propia armadura de tela y piezas BoP nuevas de Forever.",
  "     Encantamiento: desencanta los verdes que no uses, haz varitas (Varita mágica mayor) y encanta tu equipo.",
  "     Recetas que SÍ: Bolsas (todas), Túnicas/Togas con Intelecto, rollos de tela, encantamientos de +Intelecto/+Espíritu, Varitas.",
  "     Recetas que NO: ropa decorativa, camisas, sombreros sin estadísticas.",
  "  B) |cff33ff66HERBORISTERÍA + ALQUIMIA (la mejor para oro estable)|r",
  "     Pociones de maná/sanación, elixires y frascos: SIEMPRE se venden, sobre todo a 60 y en JcJ.",
  "     Recetas que SÍ: Poción de maná (todas), Poción de sanación, Elixir de poder de Escarcha / de hechizos, Poción de acción libre.",
  "     Recetas que NO: aceites raros, pociones de agua/sigilo que nadie compra.",
  "  C) |cff33ff66MINERÍA + INGENIERÍA (la mejor para JcJ)|r",
  "     Bombas, redes y granadas para controlar. Las granadas se venden a no-ingenieros.",
  "     Recetas que SÍ: Pólvora, Dinamita, Granadas de hierro, Bomba explosiva, Red (Net-o-Matic), gafas de ingeniero de tela.",
  "     Recetas que NO: mascotas mecánicas, fuegos artificiales, objetos decorativos.",
}

-- Común a todos los planes
GF.Profesiones.comun = {
  " ",
  "|cffffd100QUÉ CRAFTEAR PARA VENDER (siempre que esté por encima del coste)|r",
  "  1. Mira el precio de los materiales y del objeto final en subasta ANTES de craftear.",
  "  2. Si el objeto vale menos que los materiales, vende los materiales y no craftees.",
  "  3. Los consumibles (pociones, bolsas, piedras, bombas, comida) se venden mejor que el equipo.",
  "  4. Subir una profesión de fabricación da Puntos de Legado (cuenta) en Forever.",
  "  5. 'Working Overtime' aumenta un 4-20% la probabilidad de subir punto: úsalo al subir.",
  " ",
  "|cffff4040ERRORES TÍPICOS DE NOVATO|r",
  "  - Coger dos profesiones de fabricación al principio = arruinarte.",
  "  - Comprar los materiales en subasta para subir una profesión a nivel bajo.",
  "  - Cambiar de profesión varias veces (pierdes todo el progreso).",
  "  - Encantamiento sin Sastrería ni dinero: es caro y lento de rentabilizar.",
  "  - Mago No-muerto: la misión de clase de nv15 pide 10 Lino. No lo vendas todo.",
}

function GF:ProfText()
  local plan = self.Profesiones.porClase[self:PlayerClass() or ""] or "ARMADURA"
  local out = {}
  for _, l in ipairs(self.Profesiones.textos[plan]) do table.insert(out, l) end
  for _, l in ipairs(self.Profesiones.comun) do table.insert(out, l) end
  return out
end
