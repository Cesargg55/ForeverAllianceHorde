# ForeverAlliance&Horde

Guía paso a paso **1-60** para **World of Warcraft: Forever**, para jugadores nuevos de **Alianza y Horda**. Interfaz en español.

Un solo addon para todos tus personajes: al entrar mira tu **raza**, tu **facción** y tu **clase**, y te pone la ruta que toca con las misiones de TU clase.

> 🤖 **Hecho con vibe coding.** Este addon lo he hecho haciendo *vibe coding*: yo decido qué quiero y lo pruebo, y el código, las rutas y los textos los escribe una IA (Claude). La lógica se prueba fuera del juego con una simulación (`tools/test_addon.py`), pero puede haber fallos dentro del juego, misiones mal colocadas o consejos que no encajen con los cambios de Forever. Si ves algo raro, abre un *issue*.

| Ruta | Razas | Empieza en | Misiones de clase incluidas |
|---|---|---|---|
| `alianza` | Humano | Abadía de Northshire → Elwynn (1-10 a mano) | Paladín (12, 20, 40, 60) |
| `horda` | No-muerto | Camposanto → Claros de Tirisfal | Mago (1, 10, 15, 26, 30-40, 35-40, 50+) y la carta de nv1 de Guerrero, Pícaro, Sacerdote y Brujo |

Si tu raza aún no tiene ruta propia (Enano, Gnomo, Elfo de la noche, Orco, Tauren, Trol, Skyborne…) usas la de tu facción y el addon te avisa. Puedes cambiarla con `/guia ruta`.

## Qué hace

- **Ruta de misiones en orden:** qué misión recoger, cuál hacer y cuál entregar, con coordenadas. Los pasos se marcan solos al recoger o entregar.
- **Solo ves lo de tu clase:** un Paladín no ve las misiones de mago y al revés.
- **Flecha:** marca en el mapa, o flecha en pantalla si tienes [TomTom](https://www.curseforge.com/wow/addons/tomtom).
- **Entrenador:** al abrirlo marca en verde lo que hay que comprar, en amarillo lo opcional y en rojo lo que **no**. Un botón compra solo lo recomendado. Listas detalladas: Paladín, Guerrero y Mago.
- **Ahorro:** barra de oro con el objetivo según el nivel (montura a 40, montura rápida a 60; gratis a 40 para Paladín y Brujo).
- **Vendedor:** vende los grises y repara solo.
- **Pestañas de ayuda:** Habilidades, Talentos, Oro (farmeos de tu facción + trucos de tu clase), Profesiones (plan para clases de armadura o de tela), JcJ (de tu facción y tu clase), Clases (según tu raza) y Novedades de Forever.
- **Sabe qué misiones puedes coger:** comprueba en el juego tu nivel y si has hecho las misiones previas. Si una misión aún no está disponible, la pospone; cuando ya puedas cogerla te avisa y, si estás en esa zona, la guía vuelve a ella.
- **Panel de Progreso** (botón **Prog.** o `/fah progreso`): por dónde vas, % de misiones hechas, lo que te has saltado (con botón **Ir**), lo pendiente y por qué, tu diario y el estado de cada zona.
- **Progreso por personaje.** Si una versión nueva cambia la ruta, el addon te recoloca en tu paso.

## Instalación

1. Copia la carpeta `ForeverAllianceHorde` a `World of Warcraft\_forever_\Interface\AddOns\`.
2. **Borra o desactiva** los addons antiguos `ForeverHumansPaladins` y `ForeverNoDeathMage`: este los sustituye (todos usan `/guia`).
3. Reinicia el juego y escribe `/fah`.

> Vienes del addon antiguo: el progreso guardado no se pasa (es otro addon), pero la guía mira en el juego qué misiones ya hiciste. Escribe `/guia nivel` y te deja en tu sitio saltando lo que ya tienes hecho.

## Comandos

| Comando | Qué hace |
|---|---|
| `/fah` o `/guia` | Muestra la ventana y la lista de comandos |
| `/fah progreso` | Panel de progreso: hecho, saltado y pendiente |
| `/fah habilidades` · `talentos` · `oro` · `prof` · `jcj` · `clases` · `novedades` | Pestañas de ayuda |
| `/fah nivel` | Salta al paso de la guía de tu nivel |
| `/fah paso N` | Ve al paso N |
| `/fah ruta alianza` · `horda` · `auto` | Cambia de ruta (normalmente se elige sola) |
| `/fah objetivo 150` | Objetivo de ahorro en oro (0 = automático) |
| `/fah vender` · `reparar` · `avisos` | Activa o desactiva los automatismos |

## Cómo está hecho

| Archivo | Qué hay |
|---|---|
| `Core.lua` | Lógica, eventos, comandos y **`GF.RutaMeta`** (qué razas usan cada ruta) |
| `Data_Ruta_Elwynn.lua` | Alianza 1-10, escrita a mano |
| `Data_Ruta_Alianza.lua` · `Data_Ruta_Horda.lua` | Rutas generadas |
| `Data_Misiones_*.lua` | Nivel requerido, previas y exclusivas de cada misión (generado) |
| `Data_Clases.lua` | Habilidades SÍ/OPC/NO y talentos por clase · «¿qué clase elijo?» por raza |
| `Data_Oro.lua` · `Data_Profesiones.lua` · `Data_JcJ.lua` | Ayuda por facción y por clase |

Un paso con `cl="MAGE"` (o `PALADIN`, `WARRIOR`…) solo lo ve esa clase. Sin `cl`, lo ven todos.

Las rutas se generan con [`tools/planner.py`](tools/planner.py) a partir de los datos de Forever de [QuestieDB](https://github.com/Questie/QuestieDB): IDs de misión, PNJ, coordenadas en los mapas de Forever, nombres en español y experiencia de cada misión. Solo coge misiones de tu raza y de PNJ de tu facción, **simula tu experiencia** misión a misión y solo te manda a recoger una misión cuando tendrías el nivel y las previas. Si a una zona le faltan uno o dos niveles, te dice que subas allí mismo.

### Añadir cosas

- **Otra clase:** en `tools/planner.py` escribe sus bloques de misiones de clase (como `pal12` o `mage10`) y añádelos a `clases` de su facción. Sus habilidades van en `Data_Clases.lua` y sus consejos de JcJ en `Data_JcJ.lua`.
- **Otra raza de una facción que ya existe:** si empieza en otra zona, crea una ruta nueva en `RUTAS` del planner (con su zona de inicio al principio del `plan`) y regístrala en `GF.RutaMeta` y `GF.RutaOrden` de `Core.lua`. Su texto de «¿qué clase elijo?» va en `GF.ClasesTexto.<Raza>`.

### Regenerar las rutas

```sh
# 1) Copia en una carpeta los archivos de QuestieDB: data/Forever/*.lua, data/Forever/conversion.json
#    y l10n/Forever/{lookupQuests,lookupNpcs,lookupObjects}/esES.lua (como es_<tipo>.lua)
#    (y opcional l10n/Forever/traces/... como tr_<tipo>.lua)
py -I tools/extract.py <carpeta_questiedb> <carpeta_json>
# 2) Copia support/Forever/QuestXP/xpDB-classic.lua y xpDB-traces.lua a <carpeta_json> como xpDB.lua y xpTr.lua
# 3) Genera las rutas
QDB_JSON=<carpeta_json> py -I tools/planner.py alianza
QDB_JSON=<carpeta_json> py -I tools/planner.py horda
# 4) Prueba la lógica fuera del juego con varios personajes (pip install lupa)
py -I tools/test_addon.py <carpeta_de_lupa> .
```

## Limitaciones conocidas

- Las zonas nuevas de Forever (Riverglades, Shen'dralas, Monte Hyjal, Dalaran) todavía no tienen misiones en QuestieDB. Aparecen como resumen de zona.
- Las zonas de nivel alto tienen menos misiones (muchas cadenas empiezan en otra zona o en una ciudad); ahí la guía te avisa de subir matando bichos o en mazmorras.
- Forever ha cambiado talentos, hechizos y raciales. Los consejos del Mago y de las raciales de No-muerto son los clásicos: si algo no se llama igual, sigue la misma idea.
- No se distinguen las misiones de élite o de grupo. Si una es demasiado difícil en solitario, pulsa **>>**.
- Si una misión no está donde dice, pulsa **>>** para saltarla. Cualquier corrección es bienvenida.

## Licencia

GPL-3.0 (igual que QuestieDB, de donde salen los datos de la ruta). Mira [LICENSE](LICENSE).

Datos de misiones: © [Questie / QuestieDB](https://github.com/Questie/QuestieDB), GPL-3.0. World of Warcraft es una marca de Blizzard Entertainment. Este proyecto no está afiliado a Blizzard.
