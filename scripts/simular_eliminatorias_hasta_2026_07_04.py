from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixture.md"
EQUIPOS = ROOT / "equipos"
PARTIDOS = ROOT / "partidos"
CUTOFF = "2026-07-04"


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
        Simulacion("2026-06-30", "Costa de Marfil", "Noruega", 1, 2, (("Amad Diallo", 36),), (("Erling Haaland", 18), ("Martin Ødegaard", 72)), "Franck Kessié", "Sander Berge", (30, 28, 42)),
        Simulacion("2026-06-30", "Francia", "Suecia", 2, 1, (("Kylian Mbappé", 24), ("Ousmane Dembélé", 77)), (("Alexander Isak", 58),), "Aurélien Tchouaméni", "Victor Lindelöf", (55, 25, 20)),
        Simulacion("2026-06-30", "México", "Ecuador", 2, 1, (("Santiago Giménez", 31), ("Hirving Lozano", 69)), (("Enner Valencia", 52),), "Edson Álvarez", "Moisés Caicedo", (43, 29, 28)),
        Simulacion("2026-07-01", "Inglaterra", "RD del Congo", 3, 0, (("Harry Kane", 19), ("Bukayo Saka", 47), ("Jude Bellingham", 81)), (), "Declan Rice", "Chancel Mbemba", (66, 21, 13)),
        Simulacion("2026-07-01", "Bélgica", "Senegal", 2, 1, (("Romelu Lukaku", 28), ("Jérémy Doku", 74)), (("Sadio Mané", 61),), "Amadou Onana", "Kalidou Koulibaly", (45, 28, 27)),
        Simulacion("2026-07-01", "Estados Unidos", "Bosnia y Herzegovina", 2, 0, (("Christian Pulisic", 34), ("Folarin Balogun", 79)), (), "Tyler Adams", "Sead Kolašinac", (54, 27, 19)),
        Simulacion("2026-07-02", "España", "Austria", 2, 0, (("Lamine Yamal", 42), ("Nico Williams", 67)), (), "Rodri", "Konrad Laimer", (62, 23, 15)),
        Simulacion("2026-07-02", "Portugal", "Croacia", 2, 1, (("Bruno Fernandes", 38), ("Rafael Leão", 83)), (("Andrej Kramarić", 56),), "João Palhinha", "Joško Gvardiol", (48, 29, 23)),
        Simulacion("2026-07-02", "Suiza", "Argelia", 2, 1, (("Breel Embolo", 21), ("Dan Ndoye", 71)), (("Riyad Mahrez", 49),), "Granit Xhaka", "Ismaël Bennacer", (46, 30, 24)),
        Simulacion("2026-07-03", "Australia", "Egipto", 1, 2, (("Nestory Irankunda", 44),), (("Mohamed Salah", 17), ("Mostafa Mohamed", 76)), "Jackson Irvine", "Hamdi Fathi", (34, 30, 36)),
        Simulacion("2026-07-03", "Argentina", "Cabo Verde", 3, 0, (("Lionel Messi", 15), ("Julián Álvarez", 53), ("Lautaro Martínez", 85)), (), "Rodrigo De Paul", "Ryan Mendes", (72, 18, 10)),
        Simulacion("2026-07-03", "Colombia", "Ghana", 2, 1, (("Luis Díaz", 26), ("Jhon Córdoba", 68)), (("Mohammed Kudus", 51),), "Jefferson Lerma", "Thomas Partey", (49, 28, 23)),
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
        if len(columnas) == 9 and columnas[3].startswith("R32"):
            partidos.append(Partido(*columnas))
    return partidos


def path_partido(partido: Partido) -> Path:
    return PARTIDOS / f"{partido.fecha}-{slug(partido.local)}-vs-{slug(partido.visitante)}.md"


def fmt_goleadores(equipo: str, goles: tuple[tuple[str, int], ...]) -> str:
    if not goles:
        return f"- {equipo}: —"
    return f"- {equipo}: " + ", ".join(f"{jugador} {minuto}'" for jugador, minuto in goles)


def generar_archivo(partido: Partido, sim: Simulacion) -> None:
    eventos = [(1, f"Comienza el cruce de ronda de 32 en {partido.sede}.")]
    for jugador, minuto in sim.goleadores_local:
        eventos.append((minuto, f"⚽ Gol de {partido.local}: {jugador} convierte para el equipo local."))
    for jugador, minuto in sim.goleadores_visitante:
        eventos.append((minuto, f"⚽ Gol de {partido.visitante}: {jugador} define y cambia el marcador."))
    eventos.extend(
        [
            (33, "El partido entra en una fase de presión alta y disputas en el mediocampo."),
            (45.2, "Final del primer tiempo."),
            (63, "Los dos cuerpos técnicos ajustan piezas para el tramo decisivo."),
            (86, "El equipo que está abajo carga el área en busca de una última oportunidad."),
            (90.5, "Final del partido."),
        ]
    )
    eventos.sort(key=lambda evento: evento[0])

    def minuto_texto(minuto: float) -> str:
        if minuto == 45.2:
            return "45+2"
        if minuto == 90.5:
            return "90+5"
        return str(int(minuto))

    gl, gv = sim.goles_local, sim.goles_visitante
    fuerza_local = sim.probabilidades[0] - sim.probabilidades[2]
    posesion_local = max(42, min(61, 51 + fuerza_local // 5))
    tiros_local = 9 + gl * 3
    tiros_visitante = 9 + gv * 3
    ganador = partido.local if gl > gv else partido.visitante
    marcador_ganador = f"{gl}-{gv}" if gl > gv else f"{gv}-{gl}"
    perdedor = partido.visitante if gl > gv else partido.local
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
- Fase: Ronda de 32
- Partido FIFA: M{partido_fifa}

## Contexto y supuestos
- Simulación basada en las stats, forma, moral, carga física y disponibilidad registradas en las fichas internas.
- Sede neutral, con una ventaja ambiental moderada cuando correspondía.
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
- {partido.visitante}: agregó velocidad por bandas para disputar el cierre.

## Estadísticas
| Equipo | Posesión | Tiros | Al arco | Córners | Faltas | Amarillas | Rojas |
|--------|----------|-------|---------|---------|--------|------------|-------|
| {partido.local} | {posesion_local}% | {tiros_local} | {max(3, gl + 3)} | {3 + gl} | {11 + gv} | 1 | 0 |
| {partido.visitante} | {100 - posesion_local}% | {tiros_visitante} | {max(3, gv + 3)} | {3 + gv} | {11 + gl} | 1 | 0 |

## MVP
- {mvp}

## Resumen final
{ganador} ganó {marcador_ganador} ante {perdedor} y avanzó a octavos de final.
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
    estado = "Clasificado a octavos" if gf > gc else "Eliminado"

    carga = re.search(r"(## Carga física acumulada en el Mundial\n- )(\d+)(/100)", texto)
    if carga:
        nueva_carga = min(100, int(carga.group(2)) + 12)
        texto = texto[: carga.start()] + f"{carga.group(1)}{nueva_carga}{carga.group(3)}" + texto[carga.end() :]

    moral = re.search(r"(- Moral: )(\d+)", texto)
    if moral:
        delta = 2 if gf > gc else -2
        nueva_moral = max(0, min(100, int(moral.group(2)) + delta))
        texto = texto[: moral.start()] + f"{moral.group(1)}{nueva_moral}" + texto[moral.end() :]

    fila = f"| Ronda de 32 | {rival} | {resultado} | {estado} |"
    if "## Fase eliminatoria" not in texto:
        bloque = (
            "## Fase eliminatoria\n"
            "| Ronda | Rival | Resultado | Estado |\n"
            "|-------|-------|-----------|--------|\n"
            f"{fila}\n\n"
        )
        texto = texto.replace("### Goleadores propios", bloque + "### Goleadores propios")
    elif fila not in texto:
        texto = re.sub(
            r"(## Fase eliminatoria\n\| Ronda \| Rival \| Resultado \| Estado \|\n\|[-|]+\|\n)",
            rf"\1{fila}\n",
            texto,
        )

    goles = sim.goleadores_local if nombre == sim.local else sim.goleadores_visitante
    if goles:
        lineas = "\n".join(
            f"- {jugador}: 1 gol ({minuto}' vs {rival}, ronda de 32)"
            for jugador, minuto in goles
        )
        if lineas not in texto:
            texto = texto.replace("### Disciplina y disponibilidad", lineas + "\n\n### Disciplina y disponibilidad")

    amarilla = sim.amarilla_local if nombre == sim.local else sim.amarilla_visitante
    disciplina = (
        "### Disciplina en eliminatorias\n"
        f"- Amarillas: {amarilla} ({sim.fecha} vs {rival})\n"
        "- Las amarillas simples de la fase de grupos quedaron canceladas al terminar esa fase.\n\n"
    )
    if "### Disciplina en eliminatorias" not in texto:
        texto = texto.replace("### Disciplina y disponibilidad", disciplina + "### Disciplina y disponibilidad")

    path.write_text(texto, encoding="utf-8")


def actualizar_fixture(partidos: list[Partido], objetivos: list[Partido]) -> None:
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
    texto = re.sub(r"- 🏃 Ronda de 32 en curso: \d+/16 partidos\.", "- ✅ Ronda de 32 completa: 16/16 partidos.", texto)
    texto = re.sub(r"- ⏭ Próximo partido: .*\n", "- ⏭ Próximo partido: pendiente de cargar en el fixture.\n", texto)
    path.write_text(texto, encoding="utf-8")


def main() -> None:
    texto = FIXTURE.read_text(encoding="utf-8")
    partidos = parse_fixture(texto)
    objetivos = [
        partido
        for partido in partidos
        if partido.fecha <= CUTOFF
        and "Pendiente" in partido.estado
        and (partido.fecha, partido.local, partido.visitante) in SIMULACIONES
    ]
    if not objetivos:
        print(f"No hay partidos pendientes hasta {CUTOFF}.")
        return

    for partido in objetivos:
        sim = SIMULACIONES[(partido.fecha, partido.local, partido.visitante)]
        generar_archivo(partido, sim)
        actualizar_equipo(sim, partido.local)
        actualizar_equipo(sim, partido.visitante)
    actualizar_fixture(partidos, objetivos)
    actualizar_readme()
    print(f"Simulados {len(objetivos)} partidos pendientes hasta {CUTOFF}.")


if __name__ == "__main__":
    main()
