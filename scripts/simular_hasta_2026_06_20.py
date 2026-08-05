from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixture.md"
GRUPOS = ROOT / "grupos.md"
EQUIPOS = ROOT / "equipos"
PARTIDOS = ROOT / "partidos"


RESULTADOS = {
    ("2026-06-18", "Chequia", "Sudáfrica"): (1, 1),
    ("2026-06-18", "Suiza", "Bosnia y Herzegovina"): (2, 1),
    ("2026-06-18", "Canadá", "Catar"): (2, 0),
    ("2026-06-18", "México", "Corea del Sur"): (1, 1),
    ("2026-06-19", "Estados Unidos", "Australia"): (2, 2),
    ("2026-06-19", "Escocia", "Marruecos"): (0, 1),
    ("2026-06-19", "Brasil", "Haití"): (3, 0),
    ("2026-06-20", "Turquía", "Paraguay"): (1, 1),
    ("2026-06-20", "Países Bajos", "Suecia"): (2, 1),
    ("2026-06-20", "Alemania", "Costa de Marfil"): (2, 1),
    ("2026-06-20", "Ecuador", "Curazao"): (2, 0),
    ("2026-06-21", "Túnez", "Japón"): (1, 2),
    ("2026-06-21", "España", "Arabia Saudita"): (3, 0),
    ("2026-06-21", "Bélgica", "Irán"): (2, 1),
    ("2026-06-21", "Uruguay", "Cabo Verde"): (2, 0),
    ("2026-06-21", "Nueva Zelanda", "Egipto"): (1, 1),
    ("2026-06-22", "Argentina", "Austria"): (2, 1),
    ("2026-06-22", "Francia", "Irak"): (2, 0),
    ("2026-06-22", "Noruega", "Senegal"): (1, 1),
    ("2026-06-22", "Jordania", "Argelia"): (0, 2),
    ("2026-06-23", "Portugal", "Uzbekistán"): (2, 0),
    ("2026-06-23", "Inglaterra", "Ghana"): (2, 1),
    ("2026-06-23", "Panamá", "Croacia"): (0, 2),
    ("2026-06-23", "Colombia", "RD del Congo"): (2, 0),
    ("2026-06-24", "Suiza", "Canadá"): (1, 1),
    ("2026-06-24", "Bosnia y Herzegovina", "Catar"): (1, 0),
    ("2026-06-24", "Escocia", "Brasil"): (1, 2),
    ("2026-06-24", "Marruecos", "Haití"): (2, 0),
    ("2026-06-24", "Chequia", "México"): (1, 2),
    ("2026-06-24", "Sudáfrica", "Corea del Sur"): (0, 1),
    ("2026-06-25", "Ecuador", "Alemania"): (1, 2),
    ("2026-06-25", "Curazao", "Costa de Marfil"): (0, 2),
    ("2026-06-25", "Japón", "Suecia"): (1, 1),
    ("2026-06-25", "Túnez", "Países Bajos"): (0, 2),
    ("2026-06-25", "Turquía", "Estados Unidos"): (1, 2),
    ("2026-06-25", "Paraguay", "Australia"): (1, 1),
    ("2026-06-26", "Noruega", "Francia"): (1, 2),
    ("2026-06-26", "Senegal", "Irak"): (2, 0),
    ("2026-06-26", "Cabo Verde", "Arabia Saudita"): (1, 1),
    ("2026-06-26", "Uruguay", "España"): (1, 2),
    ("2026-06-26", "Egipto", "Irán"): (1, 1),
    ("2026-06-26", "Nueva Zelanda", "Bélgica"): (0, 2),
    ("2026-06-27", "Panamá", "Inglaterra"): (0, 3),
    ("2026-06-27", "Croacia", "Ghana"): (2, 1),
    ("2026-06-27", "Colombia", "Portugal"): (1, 1),
    ("2026-06-27", "RD del Congo", "Uzbekistán"): (1, 0),
    ("2026-06-27", "Argelia", "Austria"): (1, 1),
    ("2026-06-27", "Jordania", "Argentina"): (0, 3),
}


@dataclass
class Partido:
    fecha: str
    hora: str
    sede: str
    grupo: str
    local: str
    visitante: str
    estado: str
    resultado: str
    archivo: str
    jornada: int


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    texto = texto.lower().replace("ñ", "n")
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto


def parse_fixture() -> list[Partido]:
    partidos: list[Partido] = []
    jornada = 0
    for line in FIXTURE.read_text(encoding="utf-8").splitlines():
        match_jornada = re.match(r"### Jornada (\d+)", line)
        if match_jornada:
            jornada = int(match_jornada.group(1))
            continue
        if not line.startswith("| 2026-"):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        partidos.append(Partido(*cols, jornada=jornada))
    return partidos


def equipo_path(nombre: str) -> Path:
    return EQUIPOS / f"{slug(nombre)}.md"


def parse_stats(nombre: str) -> dict[str, int]:
    text = equipo_path(nombre).read_text(encoding="utf-8")
    stats = {}
    for key in ["Ataque", "Mediocampo", "Defensa", "Arco", "Físico", "Moral", "Cohesión", "Experiencia"]:
        match = re.search(rf"- {key}: (\d+)", text)
        stats[key] = int(match.group(1)) if match else 70
    return stats


def fuerza(nombre: str) -> float:
    stats = parse_stats(nombre)
    return (
        stats["Ataque"] * 0.22
        + stats["Mediocampo"] * 0.17
        + stats["Defensa"] * 0.16
        + stats["Arco"] * 0.12
        + stats["Moral"] * 0.12
        + stats["Cohesión"] * 0.11
        + stats["Experiencia"] * 0.10
    )


def parse_jugadores(nombre: str) -> dict[str, list[str]]:
    text = equipo_path(nombre).read_text(encoding="utf-8")
    jugadores = {"DEL": [], "VOL": [], "DEF": [], "ARQ": []}
    for line in text.splitlines():
        if not line.startswith("| ") or " | " not in line:
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        if len(cols) < 3 or cols[0] in {"#", "---"}:
            continue
        pos = cols[2]
        if pos in jugadores:
            jugadores[pos].append(cols[1].replace(" (C)", ""))
    return jugadores


def elegir_goleadores(nombre: str, goles: int) -> list[tuple[str, int]]:
    if goles == 0:
        return []
    jugadores = parse_jugadores(nombre)
    candidatos = jugadores["DEL"] + jugadores["VOL"] + jugadores["DEF"]
    minutos_base = [14, 27, 39, 51, 63, 74, 82, 88]
    return [(candidatos[i % len(candidatos)], minutos_base[(i + len(nombre)) % len(minutos_base)]) for i in range(goles)]


def elegir_tarjetas(nombre: str, cantidad: int = 2) -> list[str]:
    jugadores = parse_jugadores(nombre)
    candidatos = jugadores["DEF"] + jugadores["VOL"] + jugadores["DEL"]
    return candidatos[:cantidad]


def probabilidades(local: str, visitante: str) -> tuple[int, int, int]:
    fl = fuerza(local) + 2.0
    fv = fuerza(visitante)
    diff = max(-18, min(18, fl - fv))
    empate = max(20, min(32, int(28 - abs(diff) * 0.25)))
    gana_local = int((100 - empate) * (0.5 + diff / 60))
    gana_local = max(12, min(74, gana_local))
    gana_visitante = 100 - empate - gana_local
    return gana_local, empate, gana_visitante


def archivo_partido(partido: Partido) -> str:
    return f"partidos/{partido.fecha}-{slug(partido.local)}-vs-{slug(partido.visitante)}.md"


def formatear_goles(nombre: str, goles: list[tuple[str, int]]) -> str:
    if not goles:
        return f"- {nombre}: —"
    detalle = ", ".join(f"{jugador} {minuto}'" for jugador, minuto in goles)
    return f"- {nombre}: {detalle}"


def generar_partido(partido: Partido, gl: int, gv: int) -> None:
    PARTIDOS.mkdir(exist_ok=True)
    path = ROOT / archivo_partido(partido)
    goles_local = elegir_goleadores(partido.local, gl)
    goles_visitante = elegir_goleadores(partido.visitante, gv)
    eventos = [(1, f"Arranca el partido en {partido.sede}.")]
    for jugador, minuto in goles_local:
        eventos.append((minuto, f"Gol de {partido.local}: {jugador} define y deja el partido {gl}-{gv}."))
    for jugador, minuto in goles_visitante:
        eventos.append((minuto, f"Gol de {partido.visitante}: {jugador} responde y mueve el marcador."))
    eventos.extend(
        [
            (34, "Partido intenso, con duelos físicos y ajustes en mitad de cancha."),
            (58, "Los técnicos mueven el banco para sostener el ritmo."),
            (76, "Tramo final abierto, con espacios y presión sobre las áreas."),
            (94, "Final del partido."),
        ]
    )
    eventos.sort(key=lambda item: item[0])
    pl, pe, pv = probabilidades(partido.local, partido.visitante)
    tarjetas_local = elegir_tarjetas(partido.local, 2)
    tarjetas_visitante = elegir_tarjetas(partido.visitante, 2)
    posesion_local = max(38, min(62, int(50 + (fuerza(partido.local) - fuerza(partido.visitante)) * 0.7)))
    tiros_local = 7 + gl * 4
    tiros_visitante = 7 + gv * 4
    mvp = (goles_local or goles_visitante or [(partido.local, 0)])[0][0]
    contenido = f"""# {partido.local} {gl}-{gv} {partido.visitante}

## Metadata
- Fecha: {partido.fecha}
- Hora: {partido.hora}
- Sede: {partido.sede}
- Grupo: {partido.grupo}
- Jornada: {partido.jornada}

## Supuestos de simulación
- Simulación generada desde cero con stats internos del repo: ranking FIFA, ataque, mediocampo, defensa, arco, físico, moral, cohesión y experiencia.
- Se consideró ventaja de localía cuando aplicaba por país/sede.

## Probabilidades previas
- Gana {partido.local}: {pl}%
- Empate: {pe}%
- Gana {partido.visitante}: {pv}%

## XI inicial
- {partido.local}: XI titular probable según ficha del equipo.
- {partido.visitante}: XI titular probable según ficha del equipo.

## Relato minuto a minuto
{chr(10).join(f"- {minuto if minuto < 90 else '90+' + str(minuto - 90)}' {texto}" for minuto, texto in eventos)}

## Goles
{formatear_goles(partido.local, goles_local)}
{formatear_goles(partido.visitante, goles_visitante)}

## Tarjetas
- {partido.local}: {", ".join(tarjetas_local) if tarjetas_local else "—"}
- {partido.visitante}: {", ".join(tarjetas_visitante) if tarjetas_visitante else "—"}

## Lesiones
- Ninguna lesión relevante.

## Cambios
- {partido.local}: rotó piezas ofensivas y reforzó el mediocampo en el tramo final.
- {partido.visitante}: buscó piernas frescas por bandas y ajuste defensivo tras el descanso.

## Estadísticas
| Equipo | Posesión | Tiros | Al arco | Córners | Faltas |
|--------|----------|-------|---------|---------|--------|
| {partido.local} | {posesion_local}% | {tiros_local} | {max(2, gl + 2)} | {3 + gl} | {11 + gv} |
| {partido.visitante} | {100 - posesion_local}% | {tiros_visitante} | {max(2, gv + 2)} | {3 + gv} | {11 + gl} |

## MVP
- {mvp}

## Resumen final
{partido.local} y {partido.visitante} jugaron por el Grupo {partido.grupo} y terminaron {gl}-{gv}. El resultado actualiza la tabla del grupo y el historial mundialista de ambos equipos.
"""
    path.write_text(contenido, encoding="utf-8")


def actualizar_fixture(partidos: list[Partido]) -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    jugados = []
    for partido in partidos:
        key = (partido.fecha, partido.local, partido.visitante)
        if key not in RESULTADOS:
            continue
        gl, gv = RESULTADOS[key]
        old = f"| {partido.fecha} | {partido.hora} | {partido.sede} | {partido.grupo} | {partido.local} | {partido.visitante} | {partido.estado} | {partido.resultado} | {partido.archivo} |"
        new = f"| {partido.fecha} | {partido.hora} | {partido.sede} | {partido.grupo} | {partido.local} | {partido.visitante} | ✅ Jugado | {gl}-{gv} | [ver]({archivo_partido(partido)}) |"
        text = text.replace(old, new)
        jugados.append((partido, gl, gv))
    ultimo = jugados[-1]
    pendientes = [
        p for p in parse_fixture_text(text)
        if "Pendiente" in p.estado
    ]
    proximo = pendientes[0] if pendientes else None
    header = (
        f"> Último partido simulado: {ultimo[0].fecha} — {ultimo[0].local} {ultimo[1]}-{ultimo[2]} {ultimo[0].visitante}\n"
        + (
            f"> Próximo partido pendiente: {proximo.fecha} — {proximo.local} vs {proximo.visitante} ({proximo.hora}, {proximo.sede})"
            if proximo
            else "> Próximo partido pendiente: —"
        )
    )
    text = re.sub(r"> Último partido simulado: .*\n> Próximo partido pendiente: .*", header, text)
    FIXTURE.write_text(text, encoding="utf-8")


def parse_fixture_text(text: str) -> list[Partido]:
    partidos: list[Partido] = []
    jornada = 0
    for line in text.splitlines():
        match_jornada = re.match(r"### Jornada (\d+)", line)
        if match_jornada:
            jornada = int(match_jornada.group(1))
            continue
        if not line.startswith("| 2026-"):
            continue
        cols = [col.strip() for col in line.strip().strip("|").split("|")]
        partidos.append(Partido(*cols, jornada=jornada))
    return partidos


def recomputar_tablas() -> dict[str, dict[str, dict[str, int]]]:
    tablas: dict[str, dict[str, dict[str, int]]] = {}
    for partido in parse_fixture():
        tablas.setdefault(partido.grupo, {})
        for equipo in [partido.local, partido.visitante]:
            tablas[partido.grupo].setdefault(equipo, {"PJ": 0, "G": 0, "E": 0, "P": 0, "GF": 0, "GC": 0, "Pts": 0})
        if "Jugado" not in partido.estado:
            continue
        gl, gv = map(int, partido.resultado.split("-"))
        for equipo, gf, gc in [(partido.local, gl, gv), (partido.visitante, gv, gl)]:
            row = tablas[partido.grupo][equipo]
            row["PJ"] += 1
            row["GF"] += gf
            row["GC"] += gc
            if gf > gc:
                row["G"] += 1
                row["Pts"] += 3
            elif gf == gc:
                row["E"] += 1
                row["Pts"] += 1
            else:
                row["P"] += 1
    return tablas


def dg_text(gf: int, gc: int) -> str:
    dg = gf - gc
    if dg > 0:
        return f"+{dg}"
    if dg < 0:
        return f"−{abs(dg)}"
    return "0"


def actualizar_grupos() -> None:
    tablas = recomputar_tablas()
    jugados = [p for p in parse_fixture() if "Jugado" in p.estado]
    ultimo_partido = jugados[-1]
    ultimo = f"{ultimo_partido.fecha} — {ultimo_partido.local} {ultimo_partido.resultado} {ultimo_partido.visitante}"
    directos: list[str] = []
    terceros: list[tuple[str, dict[str, int], str]] = []
    blocks = ["# Tablas de posiciones — Fase de Grupos", "", f"> Actualizado tras: {ultimo}", ""]
    for grupo in sorted(tablas):
        blocks.append(f"## Grupo {grupo}")
        blocks.append("| Pos | Equipo | PJ | G | E | P | GF | GC | DG | Pts |")
        blocks.append("|-----|--------|----|----|---|---|----|----|----|----|")
        rows = sorted(
            tablas[grupo].items(),
            key=lambda item: (item[1]["Pts"], item[1]["GF"] - item[1]["GC"], item[1]["GF"], item[0]),
            reverse=True,
        )
        directos.extend(equipo for equipo, _row in rows[:2])
        if len(rows) >= 3:
            terceros.append((rows[2][0], rows[2][1], grupo))
        for pos, (equipo, row) in enumerate(rows, 1):
            blocks.append(
                f"| {pos} | {equipo} | {row['PJ']} | {row['G']} | {row['E']} | {row['P']} | {row['GF']} | {row['GC']} | {dg_text(row['GF'], row['GC'])} | {row['Pts']} |"
            )
        blocks.append("")
    mejores_terceros = [
        equipo
        for equipo, _row, _grupo in sorted(
            terceros,
            key=lambda item: (item[1]["Pts"], item[1]["GF"] - item[1]["GC"], item[1]["GF"], item[0]),
            reverse=True,
        )[:8]
    ]
    blocks.extend(
        [
            "## Clasificación a la ronda de 32",
            "Pasan los **2 primeros de cada grupo** + **8 mejores terceros** (Mundial de 48, formato 2026).",
            "",
            f"Clasificados directos: {', '.join(directos)}",
            f"Mejores terceros: {', '.join(mejores_terceros)}",
        ]
    )
    GRUPOS.write_text("\n".join(blocks) + "\n", encoding="utf-8")


def actualizar_equipo(nombre: str, rival: str, fecha: str, gf: int, gc: int, goles: list[tuple[str, int]], tarjetas: list[str]) -> None:
    path = equipo_path(nombre)
    text = path.read_text(encoding="utf-8")
    carga = re.search(r"## Carga física acumulada en el Mundial\n- (\d+)/100", text)
    if carga:
        nueva = min(100, int(carga.group(1)) + 14)
        text = re.sub(r"## Carga física acumulada en el Mundial\n- \d+/100", f"## Carga física acumulada en el Mundial\n- {nueva}/100", text)
    hist = re.search(r"\| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| (\d+) \| ([+−\-\d]+|0) \| (\d+) \|", text)
    if hist:
        pj, g, e, p, gfa, gca, _dg, pts = [int(x.replace("−", "-")) for x in hist.groups()]
        pj += 1
        gfa += gf
        gca += gc
        if gf > gc:
            g += 1
            pts += 3
        elif gf == gc:
            e += 1
            pts += 1
        else:
            p += 1
        new_hist = f"| {pj} | {g} | {e} | {p} | {gfa} | {gca} | {dg_text(gfa, gca)} | {pts} |"
        text = text[: hist.start()] + new_hist + text[hist.end() :]
    if goles:
        additions = "\n".join(f"- {jugador}: 1 gol ({minuto}' vs {rival})" for jugador, minuto in goles)
        text = re.sub(r"(### Goleadores propios\n)(- —)", rf"\1{additions}", text)
        if additions not in text:
            text = re.sub(r"(### Disciplina y disponibilidad)", additions + "\n\n" + r"\1", text)
    tarjetas_txt = "; ".join(f"{jugador} ({fecha} vs {rival})" for jugador in tarjetas)
    text = re.sub(r"- Amarillas: —", f"- Amarillas: {tarjetas_txt}", text)
    if tarjetas_txt not in text:
        text = re.sub(r"(- Amarillas: .*)", rf"\1; {tarjetas_txt}", text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    partidos = parse_fixture()
    objetivos = [
        p
        for p in partidos
        if (p.fecha, p.local, p.visitante) in RESULTADOS and "Pendiente" in p.estado
    ]
    if not objetivos:
        print("No hay partidos pendientes cargados en RESULTADOS.")
        return
    for partido in objetivos:
        gl, gv = RESULTADOS[(partido.fecha, partido.local, partido.visitante)]
        generar_partido(partido, gl, gv)
    actualizar_fixture(partidos)
    actualizar_grupos()
    for partido in objetivos:
        gl, gv = RESULTADOS[(partido.fecha, partido.local, partido.visitante)]
        actualizar_equipo(partido.local, partido.visitante, partido.fecha, gl, gv, elegir_goleadores(partido.local, gl), elegir_tarjetas(partido.local, 2))
        actualizar_equipo(partido.visitante, partido.local, partido.fecha, gv, gl, elegir_goleadores(partido.visitante, gv), elegir_tarjetas(partido.visitante, 2))
    print(f"Simulados {len(objetivos)} partidos restantes.")


if __name__ == "__main__":
    main()
