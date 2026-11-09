# ForeverHumans&Paladins

Guía paso a paso **1-60** para **World of Warcraft: Forever**, pensada para jugadores nuevos de la **Alianza**, sobre todo **Humano Paladín**. Interfaz en español.

## Qué hace

- **Ruta de misiones en orden:** qué misión recoger, cuál hacer y cuál entregar, con coordenadas. Los pasos se marcan solos al recoger o entregar.
- **Flecha:** marca en el mapa, o flecha en pantalla si tienes [TomTom](https://www.curseforge.com/wow/addons/tomtom).
- **Entrenador:** al abrirlo marca en verde lo que hay que comprar, en amarillo lo opcional y en rojo lo que **no**. Un botón compra solo lo recomendado.
- **Ahorro:** barra de oro con el objetivo según el nivel (montura a 40, montura rápida a 60).
- **Vendedor:** vende los grises y repara solo.
- **Pestañas de ayuda:** Habilidades, Talentos, Oro (farmeos por nivel), Profesiones (qué recetas comprar y qué craftear), JcJ, Clases y Novedades de Forever.
- **Progreso por personaje.** Si una versión nueva cambia la ruta, el addon te recoloca en tu paso.

## Instalación

1. Descarga la última versión desde [Releases](../../releases), o pulsa **Code → Download ZIP**.
2. Copia la carpeta `ForeverHumansPaladins` a:
   `World of Warcraft\_forever_\Interface\AddOns\`
   (Si descargaste el ZIP de "Code", renombra la carpeta `ForeverHumansPaladins-main` a `ForeverHumansPaladins`.)
3. Reinicia el juego y escribe `/fhp`.

## Comandos

| Comando | Qué hace |
|---|---|
| `/fhp` o `/guia` | Muestra la ventana y la lista de comandos |
| `/fhp habilidades` | Qué habilidades comprar y cuáles no |
| `/fhp talentos` | Qué talentos coger |
| `/fhp oro` | Farmeos de oro para tu nivel y reglas de ahorro |
| `/fhp prof` | Profesiones, recetas y qué craftear |
| `/fhp jcj` | Consejos de JcJ para tu clase |
| `/fhp clases` | Qué clase elegir con Humano |
| `/fhp novedades` | Qué hay de nuevo en Forever |
| `/fhp nivel` | Salta al paso de la guía de tu nivel |
| `/fhp paso N` | Ve al paso N |
| `/fhp objetivo 150` | Objetivo de ahorro en oro (0 = automático) |
| `/fhp vender` · `reparar` · `avisos` | Activa o desactiva los automatismos |

## Cómo está hecha la ruta

- **1-10 (Elwynn):** escrita a mano.
- **10-60:** generada con [`tools/planner.py`](tools/planner.py) a partir de los datos de Forever de [QuestieDB](https://github.com/Questie/QuestieDB): IDs de misión, PNJ, coordenadas en los mapas de Forever y nombres en español. Recorre las zonas en orden clásico de Alianza. En cada zona recoges las misiones, haces los objetivos por cercanía y las entregas, y las cadenas se desbloquean en orden. Las misiones de clase del Paladín (12, 20, 40 y 60) están escritas a mano.

Para regenerar la ruta:

```sh
# 1) Copia en una carpeta los archivos de QuestieDB: data/Forever/*.lua, data/Forever/conversion.json
#    y l10n/Forever/{lookupQuests,lookupNpcs,lookupObjects}/esES.lua (como es_<tipo>.lua)
py -I tools/extract.py <carpeta_questiedb> <carpeta_json>
# 2) Genera la ruta
QDB_JSON=<carpeta_json> py -I tools/planner.py Data_Ruta_10_60.lua
```

## Limitaciones conocidas

- Las zonas nuevas de Forever (Riverglades, Shen'dralas, Monte Hyjal, Dalaran) todavía no tienen misiones en QuestieDB. Aparecen como resumen de zona.
- No se distinguen las misiones de élite o de grupo. Si una es demasiado difícil en solitario, pulsa **>>**.
- Si una misión no está donde dice, pulsa **>>** para saltarla. Cualquier corrección es bienvenida: abre un *issue* o un *pull request*.

## Licencia

GPL-3.0 (igual que QuestieDB, de donde salen los datos de la ruta). Mira [LICENSE](LICENSE).

Datos de misiones: © [Questie / QuestieDB](https://github.com/Questie/QuestieDB), GPL-3.0. World of Warcraft es una marca de Blizzard Entertainment. Este proyecto no está afiliado a Blizzard.
