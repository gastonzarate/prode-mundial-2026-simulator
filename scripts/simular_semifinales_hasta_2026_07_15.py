from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixture.md"
EQUIPOS = ROOT / "equipos"
PARTIDOS = ROOT / "partidos"
CUTOFF = "2026-07-15"


@dataclass(frozen=True)
class Simulacion:
    fecha: str
    hora: str
    sede: str
    fase: str
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
        Simulacion("2026-07-14", "14:00", "Dallas Stadium, Arlington", "SF · M101", "Francia", "España", 1, 2, (("Kylian Mbappé", 52),), (("Lamine Yamal", 34), ("Pedri", 81)), "William Saliba", "Rodri", (34, 28, 38)),
        Simulacion("2026-07-15", "15:00", "Atlanta Stadium, Atlanta", "SF · M102", "Inglaterra", "Argentina", 1, 2, (("Jude Bellingham", 59),), (("Lionel Messi", 27), ("Lautaro Martínez", 86)), "Declan Rice", "Cristian Romero", (31, 29, 40)),
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


def fila_fixture(sim: Simulacion, estado: str = "⏳ Pendiente", resultado: str = "—", archivo: str = "—") -> str:
    return (
        f"| {sim.fecha} | {sim.hora} | {sim.sede} | {sim.fase} | {sim.local} | {sim.visitante} | "
        f"{estado} | {resultado} | {archivo} |"
    )


def asegurar_fixture_semifinales() -> None:
    texto = FIXTURE.read_text(encoding="utf-8")
    if "### Semifinales" in texto:
        return
    filas = "\n".join(fila_fixture(sim) for sim in SIMULACIONES.values())
    bloque = (
        "\n### Semifinales\n\n"
        "| Fecha | Hora local | Sede | Fase / Partido | Local | Visitante | Estado | Resultado | Archivo |\n"
        "|-------|------------|------|----------------|-------|-----------|--------|-----------|---------|\n"
        f"{filas}\n"
    )
    texto = texto.replace("\n---\n\n**Fuentes consultadas", f"{bloque}\n---\n\n**Fuentes consultadas")
    texto = re.sub(
        r"\*\*Fuentes consultadas \(actualizadas .*?\):\*\*",
        "**Fuentes consultadas (actualizadas 2026-07-13):**",
        texto,
    )
    FIXTURE.write_text(texto, encoding="utf-8")


def parse_fixture(texto: str) -> list[Partido]:
    partidos: list[Partido] = []
    for linea in texto.splitlines():
        if not linea.startswith("| 2026-"):
            continue
        columnas = [col.strip() for col in linea.strip().strip("|").split("|")]
        if len(columnas) == 9:
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
        (1, f"Arranca la semifinal en {partido.sede}."),
        (18, "Los dos equipos miden riesgos y buscan ventajas por los costados."),
        (45.2, "Final del primer tiempo."),
        (66, "Los cambios empiezan a pesar en el ritmo del partido."),
        (90.4, "Final del partido."),
    ]
    eventos.extend((minuto, f"⚽ Gol de {partido.local}: {jugador} aparece en el momento justo.") for jugador, minuto in sim.goleadores_local)
    eventos.extend((minuto, f"⚽ Gol de {partido.visitante}: {jugador} define una jugada clave.") for jugador, minuto in sim.goleadores_visitante)
    eventos.sort(key=lambda evento: evento[0])

    def minuto_texto(minuto: float) -> str:
        return "45+2" if minuto == 45.2 else "90+4" if minuto == 90.4 else str(int(minuto))

    gl, gv = sim.goles_local, sim.goles_visitante
    fuerza_local = sim.probabilidades[0] - sim.probabilidades[2]
    posesion_local = max(40, min(60, 50 + fuerza_local // 6))
    ganador = partido.local if gl > gv else partido.visitante
    perdedor = partido.visitante if gl > gv else partido.local
    goles_ganador, goles_perdedor = (gl, gv) if gl > gv else (gv, gl)
    candidatos_mvp = sim.goleadores_local if gl > gv else sim.goleadores_visitante
    mvp = candidatos_mvp[-1][0]
    partido_fifa = re.search(r"M(\d+)", partido.fase).group(1)
    pl, pe, pv = sim.probabilidades
    relato = "\n".join(f"- {minuto_texto(m)}' {texto}" for m, texto in eventos)
    contenido = f"""# {partido.local} {gl}-{gv} {partido.visitante}

## Metadata
- Fecha: {partido.fecha}
- Hora local: {partido.hora}
- Sede: {partido.sede}
- Fase: Semifinales
- Partido FIFA: M{partido_fifa}

## Contexto y supuestos
- Cruce tomado del cuadro real de semifinales publicado para el Mundial 2026.
- El resultado es una simulación del prode, ponderando stats internas, moral, carga física y disponibilidad.
- En caso de empate se contemplaban alargue y penales; el partido se resolvió en los 90 minutos.

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
- {partido.local}: buscó piernas frescas para sostener presión y salida rápida.
- {partido.visitante}: ajustó el mediocampo para controlar mejor los últimos metros.

## Estadísticas
| Equipo | Posesión | Tiros | Al arco | Córners | Faltas | Amarillas | Rojas |
|--------|----------|-------|---------|---------|--------|------------|-------|
| {partido.local} | {posesion_local}% | {10 + gl * 3} | {max(3, gl + 3)} | {3 + gl} | {10 + gv} | 1 | 0 |
| {partido.visitante} | {100 - posesion_local}% | {10 + gv * 3} | {max(3, gv + 3)} | {3 + gv} | {10 + gl} | 1 | 0 |

## MVP
- {mvp}

## Resumen final
{ganador} venció a {perdedor} por {goles_ganador}-{goles_perdedor} y avanzó a la final.
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
    estado = "Clasificado a la final" if gf > gc else "Eliminado en semifinales; jugará tercer puesto"

    carga = re.search(r"(## Carga física acumulada en el Mundial\n- )(\d+)(/100)", texto)
    if carga:
        nueva_carga = min(100, int(carga.group(2)) + 10)
        texto = texto[: carga.start()] + f"{carga.group(1)}{nueva_carga}{carga.group(3)}" + texto[carga.end() :]

    moral = re.search(r"(- Moral: )(\d+)", texto)
    if moral:
        delta = 2 if gf > gc else -2
        nueva_moral = max(0, min(100, int(moral.group(2)) + delta))
        texto = texto[: moral.start()] + f"{moral.group(1)}{nueva_moral}" + texto[moral.end() :]

    fila = f"| Semifinales | {rival} | {resultado} | {estado} |"
    if fila not in texto:
        texto = re.sub(
            r"(## Fase eliminatoria\n(?:> .+\n\n)?\| Ronda \| Rival \| Resultado \| Estado \|\n\|[-|]+\|\n)",
            rf"\1{fila}\n",
            texto,
        )

    goles = sim.goleadores_local if nombre == sim.local else sim.goleadores_visitante
    if goles:
        lineas = "\n".join(
            f"- {jugador}: 1 gol ({minuto}' vs {rival}, semifinales)"
            for jugador, minuto in goles
        )
        if lineas not in texto:
            texto = texto.replace("### Disciplina en eliminatorias", lineas + "\n\n### Disciplina en eliminatorias")

    amarilla = sim.amarilla_local if nombre == sim.local else sim.amarilla_visitante
    linea_disciplina = f"- Amarillas: {amarilla} ({sim.fecha} vs {rival})"
    if linea_disciplina not in texto:
        texto = texto.replace("### Disciplina en eliminatorias\n", f"### Disciplina en eliminatorias\n{linea_disciplina}\n")

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
        else "tercer puesto y final, pendientes de cargar tras validar los resultados reales de semifinales"
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
    if "- ✅ Semifinales completas: 2/2 partidos." not in texto:
        texto = texto.replace(
            "- ✅ Cuartos de final completos: 4/4 partidos.\n",
            "- ✅ Cuartos de final completos: 4/4 partidos.\n"
            "- ✅ Semifinales completas: 2/2 partidos.\n",
        )
    texto = re.sub(
        r"- ⏭ Próximo partido: .*\n",
        "- ⏭ Próximo partido: tercer puesto y final, pendientes de cargar tras validar los resultados reales de semifinales.\n",
        texto,
    )
    path.write_text(texto, encoding="utf-8")


def main() -> None:
    asegurar_fixture_semifinales()
    partidos = parse_fixture(FIXTURE.read_text(encoding="utf-8"))
    objetivos = [
        partido
        for partido in partidos
        if partido.fase.startswith("SF")
        and partido.fecha <= CUTOFF
        and "Pendiente" in partido.estado
        and (partido.fecha, partido.local, partido.visitante) in SIMULACIONES
    ]
    if not objetivos:
        print(f"No hay partidos pendientes de semifinales hasta {CUTOFF}.")
        return

    for partido in objetivos:
        sim = SIMULACIONES[(partido.fecha, partido.local, partido.visitante)]
        generar_archivo(partido, sim)
        actualizar_equipo(sim, partido.local)
        actualizar_equipo(sim, partido.visitante)
    actualizar_fixture(objetivos)
    actualizar_readme()
    print(f"Simulados {len(objetivos)} partidos de semifinales hasta {CUTOFF}.")


if __name__ == "__main__":
    main()
