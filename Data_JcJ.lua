-- ForeverAlliance&Horde - JcJ (Europa, ruleset JcJ) y novedades de Forever
-- JcJ.general[Facción] = consejos de tu facción · JcJ[CLASE] = consejos de tu clase
local _, GF = ...

GF.JcJ.comun = {
  "|cffffd100JcJ EN FOREVER (Europa)|r",
  "  - Forever NO tiene reinos: hay 'conjuntos de reglas' (Normal, JcJ, RP, RP-JcJ). Si elegiste JcJ:",
  "  - Campo de batalla nuevo: Darkspear Islands. Temporadas JcJ renovadas en primavera/verano 2027.",
}

GF.JcJ.general = {}
GF.JcJ.general.Alliance = {
  "  - Cualquier jugador de la Horda te puede atacar en zonas disputadas (casi todo a partir de nv 20).",
  " ",
  "|cff33ff66SUPERVIVENCIA EN MUNDO ABIERTO|r",
  "  1. Ten SIEMPRE la vida llena antes de pelear con un bicho en zona disputada.",
  "  2. Si un Horda de mucho más nivel te mata, no resucites al lado: espera o resucita en el cementerio.",
  "  3. Humano: pícaros/druidas en sigilo, usa PERCEPCIÓN al notar algo raro.",
  "  4. Humano: aturdido, VOLUNTAD DE SUPERVIVENCIA rompe el aturdimiento. Ponla en una tecla fácil.",
  "  5. Lleva vendas y pociones. Una poción a tiempo gana el combate.",
  "  6. Ingeniería (bombas y redes) es la profesión más fuerte en JcJ.",
}
GF.JcJ.general.Horde = {
  "  - Cualquier jugador de la Alianza te puede atacar en zonas disputadas (casi todo a partir de nv 20).",
  "  - Zonas calientes para la Horda: Laderas de Trabalomas (Molino Tarren vs Costasur), Vega de Tuercespina, Tierras Inhóspitas.",
  " ",
  "|cff33ff66SUPERVIVENCIA EN MUNDO ABIERTO|r",
  "  1. Ten SIEMPRE la vida y el maná llenos antes de pelear con un bicho en zona disputada.",
  "  2. Si un Alianza de mucho más nivel te mata, no resucites al lado: espera o resucita en el cementerio.",
  "  3. No-muerto: te meten miedo, encantamiento o sueño, usa VOLUNTAD DE LOS RENEGADOS. Ponla en una tecla fácil.",
  "  4. Ojo con los Humanos: en Forever tienen una racial que rompe aturdimientos. No gastes tu control justo después de que la usen.",
  "  5. Lleva vendas y pociones. Una poción a tiempo gana el combate.",
  "  6. Ingeniería (bombas y redes) es la profesión más fuerte en JcJ.",
}

GF.JcJ.teclas = {
  " ",
  "|cff3fbfffATAJOS DE TECLADO RECOMENDADOS|r",
  "  - Racial, aturdir/miedo/congelar, quitar efectos, escapar, inmunidad: TODO en teclas, no con clic.",
  "  - Pon 'Seleccionar enemigo más cercano' (Tab) y 'Enfoque' (focus).",
}

GF.JcJ.PALADIN = {
  "|cff33ff66PALADÍN EN JcJ|r",
  "  - Combo básico Reprensión: Sello de mando -> golpea -> Sentencia -> Martillo de justicia -> golpea con 2 manos.",
  "  - Cuando están bajos (<20%): Martillo de cólera para rematar a distancia.",
  "  - Te ralentizan: Bendición de libertad. Contra pícaros/guerreros: Bendición de protección.",
  "  - Vida baja: Escudo divino -> Luz Sagrada / Destello -> sigue pegando.",
  "  - Limpiar: quita venenos, enfermedades y magia (ralentizaciones de mago, miedos de brujo/sacerdote en aliados).",
  "  - En campos de batalla: eres muy difícil de matar; protege la bandera o al sanador.",
  "  - Arrepentimiento (talento a 40): incapacita, ideal para escapar o curarte.",
}

GF.JcJ.WARRIOR = {
  "|cff33ff66GUERRERO EN JcJ|r",
  "  - Cargar -> Seccionar SIEMPRE (no deja huir) -> Golpe mortal -> Abrumar si esquiva -> Ejecutar.",
  "  - Si te alejan: Interceptar (Actitud rabiosa).",
  "  - Contra lanzadores: Golpe de escudo / Zurrar para cortar sus hechizos.",
  "  - Contra miedos (brujo/sacerdote): Ira rabiosa ANTES del miedo.",
  "  - Desarmar contra pícaros y otros guerreros.",
  "  - Con un sanador al lado eres de lo más mortal del juego; solo eres vulnerable a ralentizaciones.",
}

GF.JcJ.MAGE = {
  "|cff33ff66MAGO EN JcJ|r",
  "  - Regla número uno: DISTANCIA. Si te alcanzan los cuerpo a cuerpo, Nova de Escarcha -> Traslación -> sigue lanzando.",
  "  - Combo Escarcha: Descarga de Escarcha -> Descarga -> (se acerca) Nova -> aléjate -> Descarga (crítico con Hacerse añicos) -> Explosión de fuego.",
  "  - Contra sanadores y lanzadores: Contrahechizo en su curación o hechizo grande (los deja 'mudos' de esa escuela unos segundos).",
  "  - Contra dos enemigos: Polimorfia a uno (al enfoque) y mata al otro.",
  "  - Vida baja: Barrera de hielo (talento) -> Bloque de hielo -> Gélido para reiniciar Nova y Bloque.",
  "  - Pícaros: tenlos siempre lentos; Nova en cuanto salgan del sigilo. Guerreros y paladines: Descarga de Escarcha y Cono de frío, nunca te quedes quieto.",
  "  - Eliminar maldición menor: quita maldiciones de brujos a tus aliados.",
  "  - En campos de batalla: quédate detrás de tu grupo; Ventisca y Nova en los puntos de la bandera / base.",
}

GF.Novedades = {
  "|cffffd100¿QUÉ HAY NUEVO EN WOW FOREVER? (lanzado 4 nov 2026)|r",
  "  - Es 'Classic+': nivel máximo 60, pero con zonas, misiones y cambios nuevos. Incluido en la suscripción.",
  "  - Sin reinos: eliges conjunto de reglas (Normal/JcJ/RP/RP-JcJ; Hardcore más adelante).",
  "  - +1000 misiones nuevas. Zonas nuevas: Riverglades (35-45), Shen'dralas (40-53), Monte Hyjal (60), Zephras Isle (inicio Skyborne).",
  "  - Zonas clásicas ampliadas y Dalaran en las Montañas de Alterac.",
  "  - Raza nueva Skyborne (los de Alianza pueden ser magos).",
  "  - Mazmorras nuevas: Krol'dok Stronghold (40-45), Alcaz Prison. Raids (9 dic): Barrow Deeps, Cumbre Hyjal, Guarida de Onyxia.",
  "  - Todas las clases cambiadas. Paladín: sin Bendición de salvación ni de luz; Furia recta a nv10.",
  "  - Mago y resto de clases: si un talento o hechizo no se llama igual, mira las notas del parche en el juego.",
  "  - Doble especialización a nivel 40 (50g). El coste de reiniciar talentos baja con el tiempo hasta 1g.",
  "  - Raciales nuevas: Humano tiene Voluntad de supervivencia (rompe aturdimientos), Percepción, Ruthless, The Human Spirit.",
  "  - Profesiones: Puntos de Legado, Working Overtime, Dedicated Study, Camping, patrones BoP para armeros.",
  "  - Poción de sanación menor pasa de Alquimia a Primeros auxilios.",
  "  - Transfiguración opcional (para lucir la armadura que quieras), Colecciones de cuenta.",
  "  - Monedas nuevas: Tarnished Undermine Reals (mazmorras 55+, Bahía del Botín). Merchant's Favor para recetas altas.",
  "  - Campo de batalla nuevo: Darkspear Islands.",
  " ",
  "|cff9d9d9dDatos de guías de la beta y del lanzamiento. Algunos valores pueden cambiar con parches.|r",
}
