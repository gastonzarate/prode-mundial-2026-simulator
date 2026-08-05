const statusFilter = document.getElementById("status-filter");
const groupFilter = document.getElementById("group-filter");

function lines(s) {
  return s.split(/\r?\n/);
}

function parseFixture(md) {
  const rows = [];
  for (const line of lines(md)) {
    if (!line.startsWith("| 2026-")) continue;
    const cols = line.split("|").map((x) => x.trim());
    rows.push({
      fecha: cols[1],
      hora: cols[2],
      sede: cols[3],
      fase: cols[4],
      grupo: /^[A-L]$/.test(cols[4]) ? cols[4] : "",
      ronda: cols[4].match(/^(R32|R16|QF|SF|F3|F)/)?.[1] || "Grupos",
      partido: cols[4].match(/M(\d+)/)?.[1] || "",
      local: cols[5],
      visitante: cols[6],
      estado: cols[7],
      resultado: cols[8],
      archivo: cols[9],
    });
  }
  return rows;
}

function parseGroups(md) {
  const out = {};
  let current = null;
  for (const line of lines(md)) {
    const g = line.match(/^## Grupo ([A-L])/);
    if (g) {
      current = g[1];
      out[current] = [];
      continue;
    }
    if (!current || !line.startsWith("|")) continue;
    if (line.includes("| Pos |") || line.includes("|-----")) continue;
    const cols = line.split("|").map((x) => x.trim());
    if (!/^\d+$/.test(cols[1])) continue;
    out[current].push({
      pos: cols[1],
      equipo: cols[2],
      pj: cols[3],
      dg: cols[8],
      pts: cols[9],
    });
  }
  return out;
}

function getHeaderInfo(md) {
  const last =
    md.match(/^> Último partido simulado:\s*(.*)$/m)?.[1] ||
    md.match(/^> Último:\s*(.*)$/m)?.[1] ||
    "—";
  const next =
    md.match(/^> Próximo partido pendiente:\s*(.*)$/m)?.[1] ||
    md.match(/^> Próximo:\s*(.*)$/m)?.[1] ||
    "—";
  return { last, next };
}

function renderSummary(matches) {
  const played = matches.filter((m) => m.estado.includes("Jugado")).length;
  const pending = matches.filter((m) => m.estado.includes("Pendiente")).length;
  const totalGoals = matches
    .filter((m) => /^\d+-\d+$/.test(m.resultado))
    .reduce((acc, m) => {
      const [a, b] = m.resultado.split("-").map(Number);
      return acc + a + b;
    }, 0);

  document.getElementById("summary").innerHTML = `
    <article class="summary-card"><div class="label">Partidos jugados</div><div class="value">${played}</div></article>
    <article class="summary-card"><div class="label">Partidos pendientes</div><div class="value">${pending}</div></article>
    <article class="summary-card"><div class="label">Goles convertidos</div><div class="value">${totalGoals}</div></article>
    <article class="summary-card"><div class="label">Total programados</div><div class="value">${matches.length}</div></article>
  `;
}

function renderNext(matches) {
  const pending = matches.filter((m) => m.estado.includes("Pendiente")).slice(0, 6);
  if (pending.length === 0) {
    document.getElementById("next-matches").innerHTML = `
      <article class="next-item">
        <div class="next-time">Fixture cargado completo</div>
        <div><strong>No quedan partidos pendientes.</strong></div>
        <div class="subtle">Todos los partidos disponibles en fixture.md tienen resultado.</div>
      </article>
    `;
    return;
  }
  document.getElementById("next-matches").innerHTML = pending
    .map(
      (m) => `
      <article class="next-item">
        <div class="next-time">${m.fecha} ${m.hora}</div>
        <div><strong>${m.local}</strong> vs <strong>${m.visitante}</strong></div>
        <div class="subtle">${m.grupo ? `Grupo ${m.grupo}` : m.fase} · ${m.sede}</div>
      </article>
    `
    )
    .join("");
}

function renderKnockout(matches) {
  const knockout = matches.filter((m) => ["R32", "R16", "QF", "SF", "F3", "F"].includes(m.ronda));
  const target = document.getElementById("knockout-grid");
  if (knockout.length === 0) {
    target.innerHTML = '<p class="subtle">El cuadro eliminatorio todavía no está cargado.</p>';
    return;
  }
  target.innerHTML = knockout
    .map((m) => {
      const played = m.estado.includes("Jugado");
      return `
        <article class="knockout-match ${played ? "played" : "pending"}">
          <div class="knockout-meta">M${m.partido} · ${m.fecha} ${m.hora}</div>
          <div class="knockout-team"><span>${m.local}</span><strong>${played ? m.resultado.split("-")[0] : "—"}</strong></div>
          <div class="knockout-team"><span>${m.visitante}</span><strong>${played ? m.resultado.split("-")[1] : "—"}</strong></div>
          <div class="subtle">${m.sede}</div>
        </article>
      `;
    })
    .join("");
}

function renderFixture(matches) {
  const status = statusFilter.value;
  const group = groupFilter.value;

  const filtered = matches.filter((m) => {
    const statusOk =
      status === "all" ||
      (status === "played" && m.estado.includes("Jugado")) ||
      (status === "pending" && m.estado.includes("Pendiente"));
    const groupOk = group === "all" || m.grupo === group || m.ronda === group;
    return statusOk && groupOk;
  });

  document.getElementById("fixture-body").innerHTML = filtered
    .map((m) => {
      const klass = m.estado.includes("Jugado") ? "played" : "pending";
      return `
        <tr>
          <td>${m.fecha}</td>
          <td>${m.hora}</td>
          <td>${m.grupo ? `Grupo ${m.grupo}` : m.fase}</td>
          <td>${m.local} vs ${m.visitante}</td>
          <td><span class="status ${klass}">${m.estado.replace("✅", "").replace("⏳", "").trim()}</span></td>
          <td>${m.resultado}</td>
        </tr>
      `;
    })
    .join("");
}

function renderGroups(groups) {
  const keys = Object.keys(groups).sort();
  document.getElementById("groups-grid").innerHTML = keys
    .map((g) => {
      const rows = groups[g]
        .map(
          (r) => `<tr><td>${r.pos}</td><td>${r.equipo}</td><td>${r.pj}</td><td>${r.dg}</td><td>${r.pts}</td></tr>`
        )
        .join("");
      return `
        <article class="group-card">
          <h3>Grupo ${g}</h3>
          <table class="group-table">
            <thead><tr><th>#</th><th>Equipo</th><th>PJ</th><th>DG</th><th>Pts</th></tr></thead>
            <tbody>${rows}</tbody>
          </table>
        </article>
      `;
    })
    .join("");
}

function initFilters(matches) {
  const groups = [...new Set(matches.map((m) => m.grupo))].sort();
  for (const g of groups) {
    if (!g) continue;
    const opt = document.createElement("option");
    opt.value = g;
    opt.textContent = `Grupo ${g}`;
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "R32")) {
    const opt = document.createElement("option");
    opt.value = "R32";
    opt.textContent = "Ronda de 32";
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "R16")) {
    const opt = document.createElement("option");
    opt.value = "R16";
    opt.textContent = "Octavos de final";
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "QF")) {
    const opt = document.createElement("option");
    opt.value = "QF";
    opt.textContent = "Cuartos de final";
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "SF")) {
    const opt = document.createElement("option");
    opt.value = "SF";
    opt.textContent = "Semifinales";
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "F3")) {
    const opt = document.createElement("option");
    opt.value = "F3";
    opt.textContent = "Tercer puesto";
    groupFilter.append(opt);
  }
  if (matches.some((m) => m.ronda === "F")) {
    const opt = document.createElement("option");
    opt.value = "F";
    opt.textContent = "Final";
    groupFilter.append(opt);
  }
}

async function boot() {
  const [fixtureMd, groupsMd] = await Promise.all([
    fetch(`../fixture.md?v=${Date.now()}`, { cache: "no-store" }).then((r) => r.text()),
    fetch(`../grupos.md?v=${Date.now()}`, { cache: "no-store" }).then((r) => r.text()),
  ]);

  const matches = parseFixture(fixtureMd);
  const groups = parseGroups(groupsMd);
  const header = getHeaderInfo(fixtureMd);

  document.getElementById("sync-info").textContent = `Último: ${header.last} | Próximo: ${header.next}`;

  initFilters(matches);
  renderSummary(matches);
  renderNext(matches);
  renderKnockout(matches);
  renderFixture(matches);
  renderGroups(groups);

  statusFilter.addEventListener("change", () => renderFixture(matches));
  groupFilter.addEventListener("change", () => renderFixture(matches));
}

boot().catch((err) => {
  document.getElementById("sync-info").textContent = "No se pudieron cargar fixture.md y grupos.md. Abrí con servidor local.";
  console.error(err);
});
