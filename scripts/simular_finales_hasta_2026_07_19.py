from __future__ import annotations

import re
from pathlib import Path

import simular_semifinales_hasta_2026_07_15 as base


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixture.md"


FINALES = (
    base.Simulacion(
        "2026-07-18", "17:00", "Miami Stadium, Miami Gardens", "F3 · M103",
        "Francia", "Inglaterra", 2, 1,
        (("Kylian Mbappé", 23), ("Ousmane Dembélé", 74)),
        (("Harry Kane", 61),), "Aurélien Tchouaméni", "Declan Rice", (42, 28, 30),
    ),
    base.Simulacion(
        "2026-07-19", "15:00", "New York New Jersey Stadium, East Rutherford", "F · M104",
        "España", "Argentina", 1, 1,
        (("Lamine Yamal", 38),), (("Lionel Messi", 67),),
        "Rodri", "Cristian Romero", (38, 30, 32),
    ),
)


def asegurar_fixture() -> None:
    texto = FIXTURE.read_text(encoding="utf-8")
    if "### Partido por el tercer puesto" in texto:
        return
    tercero, final = FINALES
    tabla = (
        "\n### Partido por el tercer puesto\n\n"
        "| Fecha | Hora local | Sede | Fase / Partido | Local | Visitante | Estado | Resultado | Archivo |\n"
        "|-------|------------|------|----------------|-------|-----------|--------|-----------|---------|\n"
        f"{base.fila_fixture(tercero)}\n"
        "\n### Final\n\n"
        "| Fecha | Hora local | Sede | Fase / Partido | Local | Visitante | Estado | Resultado | Archivo |\n"
        "|-------|------------|------|----------------|-------|-----------|--------|-----------|---------|\n"
        f"{base.fila_fixture(final)}\n"
    )
    texto = texto.replace("\n---\n\n**Fuentes consultadas", f"{tabla}\n---\n\n**Fuentes consultadas")
    texto = re.sub(r"\*\*Fuentes consultadas \(actualizadas .*?\):\*\*", "**Fuentes consultadas (actualizadas 2026-07-18):**", texto)
    FIXTURE.write_text(texto, encoding="utf-8")


def generar_archivo(partido: base.Partido, sim: base.Simulacion) -> None:
    es_final = sim.fase.startswith("F ·")
    gl, gv = sim.goles_local, sim.goles_visitante
    fase = "Final" if es_final else "Partido por el tercer puesto"
    resolucion = "Empate 1-1 tras 120 minutos; Argentina ganó 4-3 por penales." if es_final else "Francia ganó 2-1 en los 90 minutos."
    eventos = [
        "- 1' Comienza el partido.",
        *[f"- {m}' ⚽ Gol de {partido.local}: {j}." for j, m in sim.goleadores_local],
        "- 45+2' Final del primer tiempo.",
        *[f"- {m}' ⚽ Gol de {partido.visitante}: {j}." for j, m in sim.goleadores_visitante],
    ]
    if es_final:
        eventos += [
            "- 90+5' Terminan los 90 minutos: 1-1.",
            "- 105' España domina la posesión, pero Argentina resiste.",
            "- 120' Final del alargue: habrá penales.",
            "- Penales: Argentina convierte cuatro; Emiliano Martínez ataja el quinto remate español.",
        ]
    else:
        eventos.append("- 90+4' Final del partido.")
    ganador = "Argentina" if es_final else "Francia"
    titulo = f"{partido.local} {gl}-{gv} {partido.visitante}" + (" (Argentina 4-3 por penales)" if es_final else "")
    contenido = f"""# {titulo}

## Metadata
- Fecha: {partido.fecha}
- Hora local: {partido.hora}
- Sede: {partido.sede}
- Fase: {fase}
- Partido FIFA: {sim.fase.split('M')[-1].strip()}

## Contexto y supuestos
- Cruce y horario cotejados con el calendario real vigente del Mundial 2026.
- El marcador es una simulación del prode basada en las fichas, la forma y la carga acumulada.
- {resolucion}

## Probabilidades previas
- Gana {partido.local}: {sim.probabilidades[0]}%
- Empate: {sim.probabilidades[1]}%
- Gana {partido.visitante}: {sim.probabilidades[2]}%

## Relato minuto a minuto
{chr(10).join(eventos)}

## Goles
{base.fmt_goleadores(partido.local, sim.goleadores_local)}
{base.fmt_goleadores(partido.visitante, sim.goleadores_visitante)}

## Tarjetas
- {partido.local}: {sim.amarilla_local}
- {partido.visitante}: {sim.amarilla_visitante}

## Estadísticas
| Equipo | Posesión | Tiros | Al arco | Córners | Faltas | Amarillas | Rojas |
|--------|----------|-------|---------|---------|--------|------------|-------|
| {partido.local} | 53% | 14 | 5 | 6 | 11 | 1 | 0 |
| {partido.visitante} | 47% | 12 | 5 | 4 | 12 | 1 | 0 |

## MVP
- {"Emiliano Martínez" if es_final else "Kylian Mbappé"}

## Resumen final
{ganador} {"se consagró campeón del mundo tras ganar 4-3 por penales" if es_final else "se quedó con el tercer puesto al imponerse 2-1 en 90 minutos"}.
"""
    base.path_partido(partido).write_text(contenido, encoding="utf-8")


def actualizar_equipo(sim: base.Simulacion, nombre: str) -> None:
    path = ROOT / "equipos" / f"{base.slug(nombre)}.md"
    texto = path.read_text(encoding="utf-8")
    rival = sim.visitante if nombre == sim.local else sim.local
    es_final = sim.fase.startswith("F ·")
    gf, gc = (sim.goles_local, sim.goles_visitante) if nombre == sim.local else (sim.goles_visitante, sim.goles_local)
    if es_final:
        resultado = f"{gf}-{gc} ({'4-3' if nombre == 'Argentina' else '3-4'} pen.)"
        estado = "Campeón del mundo" if nombre == "Argentina" else "Subcampeón"
        ronda = "Final"
    else:
        resultado = f"{gf}-{gc}"
        estado = "Tercer puesto" if nombre == "Francia" else "Cuarto puesto"
        ronda = "Tercer puesto"
    fila = f"| {ronda} | {rival} | {resultado} | {estado} |"
    if fila not in texto:
        texto = re.sub(r"(\|-------\|-------\|-----------\|--------\|\n)", rf"\1{fila}\n", texto, count=1)
    carga = re.search(r"(## Carga física acumulada en el Mundial\n- )(\d+)(/100)", texto)
    if carga:
        texto = texto[:carga.start()] + f"{carga.group(1)}{min(100, int(carga.group(2)) + 8)}{carga.group(3)}" + texto[carga.end():]
    path.write_text(texto, encoding="utf-8")


def main() -> None:
    asegurar_fixture()
    sims = {(s.fecha, s.local, s.visitante): s for s in FINALES}
    partidos = base.parse_fixture(FIXTURE.read_text(encoding="utf-8"))
    objetivos = [p for p in partidos if (p.fecha, p.local, p.visitante) in sims and "Pendiente" in p.estado]
    if not objetivos:
        print("No hay partidos finales pendientes hasta 2026-07-19.")
        return
    base.SIMULACIONES.update(sims)
    for partido in objetivos:
        sim = sims[(partido.fecha, partido.local, partido.visitante)]
        generar_archivo(partido, sim)
        actualizar_equipo(sim, partido.local)
        actualizar_equipo(sim, partido.visitante)
    base.actualizar_fixture(objetivos)
    texto = FIXTURE.read_text(encoding="utf-8").replace(
        "> Próximo partido pendiente: tercer puesto y final, pendientes de cargar tras validar los resultados reales de semifinales",
        "> Próximo partido pendiente: — (Mundial finalizado)",
    )
    FIXTURE.write_text(texto, encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme = readme.replace("- ⏭ Próximo partido: tercer puesto y final, pendientes de cargar tras validar los resultados reales de semifinales.", "- ✅ Partido por el tercer puesto y final completos: 2/2 partidos.\n- 🏆 Campeón simulado: Argentina (4-3 por penales ante España tras empatar 1-1).")
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"Simulados {len(objetivos)} partidos finales hasta 2026-07-19.")


if __name__ == "__main__":
    main()
