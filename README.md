# Prode Mundial 2026

Sistema para simular partido a partido el Mundial 2026 (FIFA World Cup 2026, USA/Canadá/México, 48 selecciones) y generar predicciones para un prode.

## Cómo funciona

1. **Bootstrap**: invocar la skill `inicializar-mundial` una sola vez. La skill usa WebSearch para bajar el fixture oficial y las plantillas de las 48 selecciones, y genera:
   - `equipos/<pais>.md` × 48 — DT, plantilla, stats, historial.
   - `fixture.md` — los 72 partidos de fase de grupos, ordenados por fecha y hora, todos `⏳ Pendiente`.
   - `grupos.md` — las 12 tablas de posiciones en cero.

2. **Simular partidos**: invocar la skill `simular-partido` sin argumentos para simular el próximo partido pendiente, o con argumento `local vs visitante` para forzar uno específico. La skill:
   - Lee `fixture.md` y los dos MDs de equipo.
   - Busca en internet el clima de la sede, el árbitro designado y el historial cara a cara.
   - Corre 10 simulaciones Monte Carlo silenciosas para calcular probabilidades.
   - Corre 1 simulación oficial relatada minuto a minuto.
   - Escribe `partidos/YYYY-MM-DD-<local>-vs-<visitante>.md`.
   - Actualiza los MDs de los dos equipos, `fixture.md` y `grupos.md`.

3. **Iterar**: repetir paso 2 hasta completar los partidos. El prode se completa con los resultados de la corrida oficial de cada partido.

## Cómo se infieren las stats numéricas

Cada equipo tiene 8 stats (0-100): Ataque, Mediocampo, Defensa, Arco, Físico, Moral, Cohesión, Experiencia. Se generan así al inicializar:

- **Base**: ranking FIFA invertido y normalizado (top 1 ≈ 95, top 50 ≈ 70).
- **Ataque/Defensa/Arco/Mediocampo**: promedio ponderado del rating individual de los jugadores titulares de esa zona del campo, donde el rating individual se infiere del nivel del club (top-5 liga europea: 85-95, primera europea sólida: 75-85, ligas medias: 65-75, otros: 50-65).
- **Físico**: media ponderada por edad (penalización suave a >32 años).
- **Moral**: 70 base + ajustes por forma reciente (últimos 5 partidos pre-Mundial).
- **Cohesión**: alta si el cuerpo técnico lleva ≥2 años, media si <2, baja si hubo cambio reciente.
- **Experiencia**: minutos de Mundial y Copa América/Euro/Asiática promediados en titulares.

Estas stats luego evolucionan partido a partido (carga, moral, lesiones, suspendidos).

## Estructura del repo

- `equipos/<pais>.md` — MD vivo por selección.
- `fixture.md` — calendario y resultados.
- `grupos.md` — tablas de posiciones.
- `partidos/YYYY-MM-DD-<local>-vs-<visitante>.md` — relato y stats de cada partido jugado.
- `dashboard/` — visual HTML estática para ver resultados y tablas.
- `docs/superpowers/specs/` — diseño.
- `docs/superpowers/plans/` — plan de implementación.
- `.claude/skills/` — las dos skills.

## Dashboard HTML

Para ver una interfaz bonita en navegador con datos en vivo desde `fixture.md` y `grupos.md`:

```bash
cd /home/andy/repos/prode-mundial-2026-simulator
python3 -m http.server 8080
```

Después abrir:

- `http://localhost:8080/dashboard/`

## Marco narrativo

Ver sección 8 del spec en `docs/superpowers/specs/2026-05-26-prode-mundial-design.md`.

## Idioma

Todo en **español argentino**: relatos, archivos, comentarios.

## Estado

- ✅ Skills implementadas: `inicializar-mundial`, `simular-partido`.
- ✅ Fase de grupos completa: 72/72 partidos.
- ✅ Ronda de 32 completa: 16/16 partidos.
- ✅ Octavos de final completos: 8/8 partidos.
- ✅ Cuartos de final completos: 4/4 partidos.
- ✅ Semifinales completas: 2/2 partidos.
- 🌐 La fase eliminatoria sigue el cuadro oficial real de FIFA; la fase de grupos conserva la simulación histórica del repo.
- ✅ Partido por el tercer puesto y final completos: 2/2 partidos.
- 🏆 Campeón simulado: Argentina (4-3 por penales ante España tras empatar 1-1).
