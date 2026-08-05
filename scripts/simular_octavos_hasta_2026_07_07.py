from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixture.md"
EQUIPOS = ROOT / "equipos"
PARTIDOS = ROOT / "partidos"
CUTOFF = "2026-07-07"


@dataclass(frozen=True)
class Simulacion:
    fecha: str
    local: str
    visitante: str
    goles_local: int
    goles_visitante: int
    goleadores_local: tuple[tuple[str, int], ...]
    goleadores_visitante: tuple[tuple[str, int], ...]
    amarilla_local: str
    amarilla_visitante: str
    probabilidades: tuple[int, int, int]


SIMULACIONES = {
    (s.fecha, s.local, s.visitante): s
    for s in (
        Simulacion("2026-07-04", "Canadá", "Marruecos", 1, 2, (("Jonathan David", 34),), (("Brahim Díaz", 58), ("Achraf Hakimi", 82)), "Moïse Bombito", "Achraf Hakimi", (30, 30, 40)),
        Simulacion("2026-07-04", "Paraguay", "Francia", 0, 2, (), (("Kylian Mbappé", 27), ("Michael Olise", 71)), "Miguel Almirón", "William Saliba", (14, 24, 62)),
        Simulacion("2026-07-05", "Brasil", "Noruega", 2, 1, (("Vinícius Júnior", 22), ("Raphinha", 76)), (("Erling Haaland", 49),), "Marquinhos", "Martin Ødegaard", (55, 25, 20)),
        Simulacion("2026-07-05", "México", "Inglaterra", 1, 2, (("Santiago Giménez", 39),), (("Harry Kane", 54), ("Bukayo Saka", 79)), "César Montes", "Jude Bellingham", (25, 28, 47)),
        Simulacion("2026-07-06", "Portugal", "España", 1, 2, (("Bruno Fernandes", 31),), (("Lamine Yamal", 63), ("Nico Williams", 84)), "Rúben Dias", "Marc Cucurella", (31, 30, 39)),
        Simulacion("2026-07-06", "Estados Unidos", "Bélgica", 1, 2, (("Christian Pulisic", 18),), (("Romelu Lukaku", 52), ("Jérémy Doku", 73)), "Weston McKennie", "Youri Tielemans", (33, 29, 38)),
        Simulacion("2026-07-07", "Argentina", "Egipto", 3, 1, (("Lionel Messi", 16), ("Julián Álvarez", 47), ("Lautaro Martínez", 88)), (("Mohamed Salah", 65),), "Cristian Romero", "Mohamed Elneny", (68, 20, 12)),
        Simulacion("2026-07-07", "Suiza", "Colombia", 1, 2, (("Breel Embolo", 41),), (("Luis Díaz", 60), ("Jhon Córdoba", 86)), "Manuel Akanji", "Dávinson Sánchez", (31, 31, 38)),
    )
}


@dataclass(frozen=True)
class Partido:
    fecha: str
    hora: str
    sede: str
    fase: str
    local: str
    visitante: str
    estado: str
    resultado: str
    archivo: str


def slug(nombre: str) -> str:
    nombre = unicodedata.normalize("NFKD", nombre)
    nombre = "".join(ch for ch in nombre if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", "-", nombre.lower()).strip("-")


def parse_fixture(texto: str) -> list[Partido]:
    partidos = []
    for linea in texto.splitlines():
        if not linea.startswith("| 2026-"):
            continue
        columnas = [col.strip() for col in linea.strip().strip("|").split("|")]
        if len(columnas) == 9 and columnas[3].startswith("R16"):
            partidos.append(Partido(*columnas))
    return partidos


def path_partido(partido: Partido) -> Path:
    return PARTIDOS / f"{partido.fecha}-{slug(partido.local)}-vs-{slug(partido.visitante)}.md"


def fmt_goleadores(equipo: str, goles: tuple[tuple[str, int], ...]) -> str:
    if not goles:
        return f"- {equipo}: —"
    return f"- {equipo}: " + ", ".join(f"{jugador} {minuto}'" for jugador, minuto in goles)


def generar_archivo(partido: Partido, sim: Simulacion) -> None:
    eventos: list[tuple[float, str]] = [
        (1, f"Comienzan los octavos de final en {partido.sede}."),
        (33, "El partido entra en una fase de presión alta y disputa en el mediocampo."),
        (45.2, "Final del primer tiempo."),
        (63, "Los cuerpos técnicos ajustan piezas para el tramo decisivo."),
        (86, "El equipo que está abajo carga el área en busca de una última oportunidad."),
        (90.5, "Final del partido."),
    ]
    eventos.extend(
        (minuto, f"⚽ Gol de {partido.local}: {jugador} define para el equipo local.")
        for jugador, minuto in sim.goleadores_local
    )
    eventos.extend(
        (minuto, f"⚽ Gol de {partido.visitante}: {jugador} convierte para el visitante.")
        for jugador, minuto in sim.goleadores_visitante
    )
    eventos.sort(key=lambda evento: evento[0])

    def minuto_texto(minuto: float) -> str:
        return "45+2" if minuto == 45.2 else "90+5" if minuto == 90.5 else str(int(minuto))

    gl, gv = sim.goles_local, sim.goles_visitante
    fuerza_local = sim.probabilidades[0] - sim.probabilidades[2]
    posesion_local = max(40, min(60, 50 + fuerza_local // 5))
    tiros_local = 9 + gl * 3
    tiros_visitante = 9 + gv * 3
    ganador = partido.local if gl > gv else partido.visitante
    perdedor = partido.visitante if gl > gv else partido.local
    goles_ganador, goles_perdedor = (gl, gv) if gl > gv else (gv, gl)
    candidatos_mvp = sim.goleadores_local if gl > gv else sim.goleadores_visitante
    mvp = candidatos_mvp[0][0]
    partido_fifa = re.search(r"M(\d+)", partido.fase).group(1)
    pl, pe, pv = sim.probabilidades
    relato = "\n".join(f"- {minuto_texto(m)}' {texto}" for m, texto in eventos)
    contenido = f"""# {partido.local} {gl}-{gv} {partido.visitante}

## Metadata
- Fecha: {partido.fecha}
- Hora local: {partido.hora}
- Sede: {partido.sede}
- Fase: Octavos de final
- Partido FIFA: M{partido_fifa}

## Contexto y supuestos
- Cruce tomado de los clasificados reales publicados para los octavos del Mundial 2026.
- Simulación basada en stats, forma, moral, carga física y disponibilidad de las fichas internas.
- En caso de empate se contemplaban tiempo suplementario y penales; el partido se resolvió en los 90 minutos.

## Probabilidades previas
- Gana {partido.local}: {pl}%
- Empate: {pe}%
- Gana {partido.visitante}: {pv}%

## XI inicial
- {partido.local}: XI titular disponible según la ficha del equipo.
- {partido.visitante}: XI titular disponible según la ficha del equipo.

## Relato minuto a minuto
{relato}

## Goles
{fmt_goleadores(partido.local, sim.goleadores_local)}
{fmt_goleadores(partido.visitante, sim.goleadores_visitante)}

## Tarjetas
- {partido.local}: {sim.amarilla_local}
- {partido.visitante}: {sim.amarilla_visitante}

## Lesiones
- Ninguna lesión nueva de consideración.

## Cambios
- {partido.local}: refrescó mediocampo y ataque durante el segundo tiempo.
- {partido.visitante}: ajustó las bandas para disputar el cierre.

## Estadísticas
| Equipo | Posesión | Tiros | Al arco | Córners | Faltas | Amarillas | Rojas |
|--------|----------|-------|---------|---------|--------|------------|-------|
| {partido.local} | {posesion_local}% | {tiros_local} | {max(3, gl + 3)} | {3 + gl} | {11 + gv} | 1 | 0 |
| {partido.visitante} | {100 - posesion_local}% | {tiros_visitante} | {max(3, gv + 3)} | {3 + gv} | {11 + gl} | 1 | 0 |

## MVP
- {mvp}

## Resumen final
{ganador} venció a {perdedor} por {goles_ganador}-{goles_perdedor} y avanzó a cuartos de final.
"""
    path_partido(partido).write_text(contenido, encoding="utf-8")


def resultado_para_equipo(sim: Simulacion, nombre: str) -> tuple[int, int, str]:
    if nombre == sim.local:
        return sim.goles_local, sim.goles_visitante, sim.visitante
    return sim.goles_visitante, sim.goles_local, sim.local


def actualizar_equipo(sim: Simulacion, nombre: str) -> None:
    path = EQUIPOS / f"{slug(nombre)}.md"
    texto = path.read_text(encoding="utf-8")
    gf, gc, rival = resultado_para_equipo(sim, nombre)
    resultado = f"{gf}-{gc}"
    estado = "Clasificado a cuartos" if gf > gc else "Eliminado"

    carga = re.search(r"(## Carga física acumulada en el Mundial\n- )(\d+)(/100)", texto)
    if carga:
        nueva_carga = min(100, int(carga.group(2)) + 12)
        texto = texto[: carga.start()] + f"{carga.group(1)}{nueva_carga}{carga.group(3)}" + texto[carga.end() :]

    moral = re.search(r"(- Moral: )(\d+)", texto)
    if moral:
        delta = 2 if gf > gc else -2
        nueva_moral = max(0, min(100, int(moral.group(2)) + delta))
        texto = texto[: moral.start()] + f"{moral.group(1)}{nueva_moral}" + texto[moral.end() :]

    fila = f"| Octavos de final | {rival} | {resultado} | {estado} |"
    if fila not in texto:
        texto = re.sub(
            r"(## Fase eliminatoria\n\| Ronda \| Rival \| Resultado \| Estado \|\n\|[-|]+\|\n)",
            rf"\1{fila}\n",
            texto,
        )

    goles = sim.goleadores_local if nombre == sim.local else sim.goleadores_visitante
    if goles:
        lineas = "\n".join(
            f"- {jugador}: 1 gol ({minuto}' vs {rival}, octavos de final)"
            for jugador, minuto in goles
        )
        if lineas not in texto:
            marcador = (
                "### Disciplina en eliminatorias"
                if "### Disciplina en eliminatorias" in texto
                else "### Disciplina y disponibilidad"
            )
            texto = texto.replace(marcador, lineas + "\n\n" + marcador)

    amarilla = sim.amarilla_local if nombre == sim.local else sim.amarilla_visitante
    linea_disciplina = f"- Amarillas: {amarilla} ({sim.fecha} vs {rival})"
    if "### Disciplina en eliminatorias" not in texto:
        bloque = (
            "### Disciplina en eliminatorias\n"
            f"{linea_disciplina}\n"
            "- Las amarillas simples de la fase de grupos quedaron canceladas al terminar esa fase.\n\n"
        )
        texto = texto.replace("### Disciplina y disponibilidad", bloque + "### Disciplina y disponibilidad")
    elif linea_disciplina not in texto:
        texto = texto.replace(
            "### Disciplina en eliminatorias\n",
            f"### Disciplina en eliminatorias\n{linea_disciplina}\n",
        )

    path.write_text(texto, encoding="utf-8")


def actualizar_fixture(objetivos: list[Partido]) -> None:
    texto = FIXTURE.read_text(encoding="utf-8")
    for partido in objetivos:
        sim = SIMULACIONES[(partido.fecha, partido.local, partido.visitante)]
        anterior = (
            f"| {partido.fecha} | {partido.hora} | {partido.sede} | {partido.fase} | "
            f"{partido.local} | {partido.visitante} | {partido.estado} | {partido.resultado} | {partido.archivo} |"
        )
        archivo = path_partido(partido).relative_to(ROOT)
        nuevo = (
            f"| {partido.fecha} | {partido.hora} | {partido.sede} | {partido.fase} | "
            f"{partido.local} | {partido.visitante} | ✅ Jugado | "
            f"{sim.goles_local}-{sim.goles_visitante} | [ver]({archivo}) |"
        )
        texto = texto.replace(anterior, nuevo)

    actualizados = parse_fixture(texto)
    ultimo = max((p for p in actualizados if "Jugado" in p.estado), key=lambda p: (p.fecha, p.hora))
    pendientes = sorted((p for p in actualizados if "Pendiente" in p.estado), key=lambda p: (p.fecha, p.hora))
    proximo = (
        f"{pendientes[0].fecha} — {pendientes[0].local} vs {pendientes[0].visitante} "
        f"({pendientes[0].hora}, {pendientes[0].sede})"
        if pendientes
        else "—"
    )
    encabezado = (
        f"> Último partido simulado: {ultimo.fecha} — {ultimo.local} {ultimo.resultado} {ultimo.visitante}\n"
        f"> Próximo partido pendiente: {proximo}"
    )
    texto = re.sub(
        r"> Último partido simulado: .*\n> Próximo partido pendiente: .*",
        encabezado,
        texto,
    )
    FIXTURE.write_text(texto, encoding="utf-8")


def actualizar_readme() -> None:
    path = ROOT / "README.md"
    texto = path.read_text(encoding="utf-8")
    if "- ✅ Octavos de final completos: 8/8 partidos." not in texto:
        texto = texto.replace(
            "- ✅ Ronda de 32 completa: 16/16 partidos.\n",
            "- ✅ Ronda de 32 completa: 16/16 partidos.\n"
            "- ✅ Octavos de final completos: 8/8 partidos.\n",
        )
    texto = re.sub(
        r"- ⏭ Próximo partido: .*\n",
        "- ⏭ Próximo partido: cuartos de final, pendiente de cargar tras validar el cuadro real.\n",
        texto,
    )
    path.write_text(texto, encoding="utf-8")


def main() -> None:
    partidos = parse_fixture(FIXTURE.read_text(encoding="utf-8"))
    objetivos = [
        partido
        for partido in partidos
        if partido.fecha <= CUTOFF
        and "Pendiente" in partido.estado
        and (partido.fecha, partido.local, partido.visitante) in SIMULACIONES
    ]
    if not objetivos:
        print(f"No hay partidos pendientes de octavos hasta {CUTOFF}.")
        return

    for partido in objetivos:
        sim = SIMULACIONES[(partido.fecha, partido.local, partido.visitante)]
        generar_archivo(partido, sim)
        actualizar_equipo(sim, partido.local)
        actualizar_equipo(sim, partido.visitante)
    actualizar_fixture(objetivos)
    actualizar_readme()
    print(f"Simulados {len(objetivos)} partidos de octavos hasta {CUTOFF}.")


if __name__ == "__main__":
    main()
