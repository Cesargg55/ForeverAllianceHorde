# ForeverHumans&Paladins

Guía paso a paso **1-60** para **World of Warcraft: Forever**, pensada para jugadores nuevos de la **Alianza**, sobre todo **Humano Paladín**. Interfaz en español.

## Qué hace

- **Ruta de misiones en orden:** qué misión recoger, cuál hacer y cuál entregar, con coordenadas. Los pasos se marcan solos al recoger o entregar.
- **Flecha:** marca en el mapa, o flecha en pantalla si tienes [TomTom](https://www.curseforge.com/wow/addons/tomtom).
- **Entrenador:** al abrirlo marca en verde lo que hay que comprar, en amarillo lo opcional y en rojo lo que **no**. Un botón compra solo lo recomendado.
- **Ahorro:** barra de oro con el objetivo según el nivel (montura a 40, montura rápida a 60).
- **Vendedor:** vende los grises y repara solo.
- **Pestañas de ayuda:** Habilidades, Talentos, Oro (farmeos por nivel), Profesiones (qué recetas comprar y qué craftear), JcJ, Clases y Novedades de Forever.
- **Sabe qué misiones puedes coger:** comprueba en el juego tu nivel y si has hecho las misiones previas. Si una misión aún no está disponible, la pospone. Cuando ya puedas cogerla te avisa y, si estás en esa zona, la guía vuelve a ella.
- **Panel de Progreso** (botón **Prog.** o `/fhp progreso`): por dónde vas, % de misiones hechas, lo que te has saltado (con botón **Ir**), lo pendiente y por qué (nivel o misión previa), tu diario y el estado de cada zona.
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
| `/fhp progreso` | Panel de progreso: hecho, saltado y pendiente |
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
- **10-60:** generada con [`tools/planner.py`](tools/planner.py) a partir de los datos de Forever de [QuestieDB](https://github.com/Questie/QuestieDB): IDs de misión, PNJ, coordenadas en los mapas de Forever, nombres en español y experiencia de cada misión. Recorre las zonas en orden clásico de Alianza. **Simula tu experiencia** misión a misión y solo te manda a recoger una misión cuando tendrías el nivel requerido y las previas hechas. Las misiones de clase del Paladín (12, 20, 40 y 60) se colocan en cuanto llegas a su nivel.
- `Data_Misiones.lua` guarda el nivel requerido, las previas y las exclusivas de cada misión, para que el addon lo compruebe en el juego.

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
