import csv
import os
from collections import defaultdict
from datetime import datetime, timedelta

# =====================
# BASE DIR POUR CHEMINS ABSOLUS
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "bloodwars_classement.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")

# =====================
# CONFIG
# =====================
SERVER_TRANSLATION = {
    "R1": "UT1",
    "R2": "UT2",
    "R4": "UT3",
    "R3": "Necropolia II",
    "R7": "Necropolia V",
    "R14": "Necropolia IX"
}

FR_SERVERS = {"R1", "R2", "R4"}
PL_SERVERS = {"R3", "R7", "R14"}

RACE_TRANSLATION = {
    "ŁAPACZ MYŚLI": "CAPTEUR D’ESPRIT",
    "SSAK": "ABSORBEUR",
    "WŁADCA ZWIERZĄT": "SEIGNEUR DES BÊTES",
    "KULTYSTA": "CULTISTE",
    "POTĘPIONY": "DAMNÉ",
}

# =====================
# DEBUG PATHS
# =====================
print("Working directory:", os.getcwd())
print("Using CSV:", CSV_FILE)
print("HTML output:", OUTPUT_HTML)

# =====================
# LOAD CSV
# =====================
def detect_delimiter(path):
    with open(path, encoding="utf-8") as f:
        sample = f.read(2048)
        return ";" if sample.count(";") > sample.count(",") else ","

delimiter = detect_delimiter(CSV_FILE)

data = defaultdict(lambda: defaultdict(list))

with open(CSV_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=delimiter)
    for row in reader:
        date = row["date"]
        server = row["server"]
        race = row["race"]
        race = RACE_TRANSLATION.get(race, race)
        data[date][server].append({
            "position": int(row["position"]),
            "name": row["name"],
            "race": race,
            "points": int(row["points"]),
        })

dates_sorted = sorted(data.keys())
print(f"📄 Dates chargées : {len(dates_sorted)}")

# =====================
# PREP DATA FOR GLOBAL TABLE
# =====================
all_players = []
for date in dates_sorted:
    for server in data[date]:
        display_server = SERVER_TRANSLATION.get(server, server)
        for p in data[date][server]:
            all_players.append({
                "date": date,
                "server": server,
                "display_server": display_server,
                "race": p["race"],
                "name": p["name"],
                "points": p["points"],
                "position": p["position"]
            })

# =====================
# HTML GENERATION
# =====================
html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Classement Bloodwars</title>
<style>
body {{
    font-family: Arial, sans-serif;
    background: #111;
    color: #eee;
    padding: 20px;
}}
h1, h2, h3 {{
    color: #f5c542;
}}
.top-filters {{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:20px;
}}
.filters {{
    flex:1;
}}
.button-group button.active {{
    background-color: #f5c542;
    color: #111;
    font-weight: bold;
}}
.filters label {{
    margin-right: 15px;
    cursor: pointer;
}}
#raceStats {{
    flex:0 0 200px;
    background:#222;
    padding:10px;
    border-radius:5px;
    font-size:0.9em;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
}}
th, td {{
    border: 1px solid #444;
    padding: 6px;
    text-align: left;
}}
th {{
    background: #222;
}}
th.sorting:after, th.sorting_asc:after, th.sorting_desc:after {{
    display: none !important;
}}
#progressTable_wrapper {{
    margin-bottom: 20px;
}}
.button-group {{
    margin-top: 10px;
}}
.button-group button {{
    margin-right: 10px;
    padding: 4px 8px;
    cursor: pointer;
}}
.filter-line {{
    display: flex;
    align-items: flex-end;
    gap: 8px;
    margin-top: 6px;
}}

.dataTables_length select {{
    background-color: #222 !important;
    color: #eee !important;
    border: 1px solid #444 !important;
    padding: 2px 4px;
}}
.dataTables_length {{
    display: none;
}}
</style>

<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

</head>
<body>

<h1>Progressions Bloodwars</h1>

<div class="top-filters">
  <div class="filters">
    <strong>Serveurs :</strong><br>
"""

for s in ["R1", "R2", "R4", "R3", "R7", "R14"]:
    html += f"""
<label>
<input type="checkbox" class="server-filter" value="{s}" checked>
{SERVER_TRANSLATION.get(s, s)}
</label>
"""

html += "<br><br><strong>Races :</strong><br>"
races = sorted(list({p["race"] for p in all_players}))
for r in races:
    html += f"""
<label>
<input type="checkbox" class="race-filter" value="{r}" checked>
{r}
</label>
"""

# -------------------- Dates --------------------
html += """
<br><br>
<div class="filter-line">
<strong>Dates </strong>
du <select id='date_start'>
"""
for d in dates_sorted:
    html += f"<option value='{d}'>{d}</option>"
html += """
</select>
au <select id='date_end'>
"""
for d in dates_sorted:
    selected = "selected" if d == dates_sorted[-1] else ""
    html += f"<option value='{d}' {selected}>{d}</option>"
html += "</select></div>"

# -------------------- Presets --------------------
html += """
<div class="filter-line">
<strong>Durée :</strong>
<span class="button-group">
    <button id="alltime">Globale</button>
    <button id="last30">Un mois</button>
    <button id="last7">Une semaine</button>
    <button id="last1">Un jour</button>
</span>
</div>
</div>

<div id="raceStats">
    <!-- Stats races ici -->
</div>
</div>

<div class="button-group" id="pageSizeButtons" style="margin-bottom:10px;">
    <strong>Nombre de joueurs :</strong><br>
    <button data-size="10" class="active">10</button>
    <button data-size="25">25</button>
    <button data-size="50">50</button>
    <button data-size="100">100</button>
    <button data-size="200">200</button>
</div>

<table id="progressTable" class="display">
<thead>
<tr>
<th>Joueur</th>
<th>Position</th>
<th>Serveur</th>
<th>Race</th>
<th>Score début</th>
<th>Score fin</th>
<th>Progression</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<script>
const allData = """ + str(all_players).replace("'", '"') + """;
const dates_sorted = """ + str(dates_sorted).replace("'", '"') + """;

function updateProgression() {
    const selectedServers = Array.from(document.querySelectorAll('.server-filter:checked')).map(cb => cb.value);
    const selectedRaces = Array.from(document.querySelectorAll('.race-filter:checked')).map(cb => cb.value);
    const dateStart = document.getElementById('date_start').value;
    const dateEnd = document.getElementById('date_end').value;

    // Grouper les données par joueur + serveur
    const playerServerMap = {};

    allData.forEach(p => {
        if (!selectedServers.includes(p.server)) return;
        if (!selectedRaces.includes(p.race)) return;

        const key = p.name + '||' + p.server;
        if (!playerServerMap[key]) {
            playerServerMap[key] = {
                name: p.name,
                server: p.server,
                display_server: p.display_server,
                races: {},
                positions: {},
                startScore: 0,
                endScore: 0
            };
        }

        // Race et position pour les dates sélectionnées
        if (p.date === dateStart) {
            playerServerMap[key].races.start = p.race;
            playerServerMap[key].startScore = p.points;
            playerServerMap[key].positions.start = p.position;
        }
        if (p.date === dateEnd) {
            playerServerMap[key].races.end = p.race;
            playerServerMap[key].endScore = p.points;
            playerServerMap[key].positions.end = p.position;
        }
    });

    // Construire le tableau à afficher
    let tableData = [];
    for (let key in playerServerMap) {
        const p = playerServerMap[key];

        if (p.startScore === 0) continue;

        // Race affichée
        let raceDisplay = p.races.start || p.races.end || '';
        if (p.races.start && p.races.end && p.races.start !== p.races.end) {
            raceDisplay = p.races.start + ' → ' + p.races.end;
        }

        // Position affichée
        let posDisplay = '';
        if (p.positions.start && p.positions.end && p.positions.start !== p.positions.end) {
            posDisplay = `${p.positions.start} → ${p.positions.end}`;
        } else if (p.positions.end) {
            posDisplay = `${p.positions.end}`;
        } else if (p.positions.start) {
            posDisplay = `${p.positions.start}`;
        }

        const prog = p.endScore - p.startScore;

        tableData.push({
            name: p.name,
            display_server: p.display_server,
            race: raceDisplay,
            startScore: p.startScore,
            endScore: p.endScore,
            prog: prog,
            position: posDisplay
        });
    }

    const dt = $('#progressTable').DataTable();
    dt.clear();
    dt.rows.add(
        tableData.map(p => [
            `<span style="color:${p.startScore===0 ? 'lime' : p.endScore===0 ? 'red' : 'inherit'}">${p.name}</span>`,
            p.position,
            p.display_server,
            p.race,
            p.startScore,
            p.endScore,
            p.prog
        ])
    );
    dt.draw();
    updateRaceStats();
}

function setActiveMode(mode) {
    ['last1','last7','last30','alltime'].forEach(id => {
        document.getElementById(id).classList.remove('active');
    });

    if (mode) {
        document.getElementById(mode).classList.add('active');
    }
}

function setActivePageSize(size) {
    document.querySelectorAll('#pageSizeButtons button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.size == size) {
            btn.classList.add('active');
        }
    });
}

function applyPageSize(size) {
    const dt = $('#progressTable').DataTable();
    dt.page.len(size).draw();
    setActivePageSize(size);
}

function applyPreset(days) {
    const end = dates_sorted[dates_sorted.length - 1];
    const endDate = new Date(end);
    const startDate = new Date(endDate);
    startDate.setDate(startDate.getDate() - days);
    const startStr = startDate.toISOString().slice(0,10);

    let closestStart = dates_sorted[0];
    for (let d of dates_sorted) {
        if (d >= startStr) {
            closestStart = d;
            break;
        }
    }

    document.getElementById('date_start').value = closestStart;
    document.getElementById('date_end').value = end;
    updateProgression();
    if (days === 1) setActiveMode('last1');
    else if (days === 7) setActiveMode('last7');
    else if (days === 30) setActiveMode('last30');

}

function applyAllTime() {
    document.getElementById('date_start').value = dates_sorted[0];
    document.getElementById('date_end').value = dates_sorted[dates_sorted.length - 1];
    updateProgression();
    setActiveMode('alltime');
}

function updateRaceStats() {
    const dt = $('#progressTable').DataTable();
    const raceCounts = {};
    let total = 0;
    let rowsData = dt.rows({ search: 'applied', order: 'applied' }).data().toArray();
    const topN = dt.page.len();
    rowsData = rowsData.slice(0, topN);
    rowsData.forEach(row => {
        const race = row[3]; // colonne Race
        raceCounts[race] = (raceCounts[race] || 0) + 1;
        total++;
    });

    let html = `<strong>Total joueurs affichés :</strong> ${total}<br><br>`;
    for (let race in raceCounts) {
        html += `${race} : <strong>${raceCounts[race]}</strong><br>`;
    }
    document.getElementById('raceStats').innerHTML = html;
}

$(document).ready(function() {
    const dt = $('#progressTable').DataTable({
        "pageLength": 10,
        "lengthMenu": [10,25,50,100,200],
        "order": [[6,"desc"]]
    });

    // Rendre la barre de recherche native capable de gérer le | comme OR (regex)
    $('#progressTable_filter input[type="search"]').off()  // retire l'écoute par défaut
    .on('input', function() {
        const val = this.value.trim();
        const dt = $('#progressTable').DataTable();
        if (val.length === 0) {
            dt.search('', false, false, true).draw();
        } else {
            // search(val, regex=true, smart=false, caseInsensitive=true)
            dt.search(val, true, false, true).draw();
        }
    });


    $('#progressTable_filter').prepend('<div style="color:#aaa; font-size:0.85em; margin-bottom:2px;">Recherche multiple avec | (ex: Alice|Bob)</div>');

    // Boutons nombre de joueurs
    document.querySelectorAll('#pageSizeButtons button').forEach(btn => {
        btn.addEventListener('click', () => {
            applyPageSize(parseInt(btn.dataset.size));
        });
    });

    // Filtres serveurs & races
    document.querySelectorAll('.server-filter, .race-filter').forEach(el => {
        el.addEventListener('change', updateProgression);
    });

    // Sélecteurs de dates
    document.getElementById('date_start').addEventListener('change', () => {
        setActiveMode(null);
        updateProgression();
    });

    document.getElementById('date_end').addEventListener('change', () => {
        setActiveMode(null);
        updateProgression();
    });

    // Boutons presets
    document.getElementById('last7').addEventListener('click', () => applyPreset(7));
    document.getElementById('last30').addEventListener('click', () => applyPreset(30));
    document.getElementById('last1').addEventListener('click', () => applyPreset(1));
    document.getElementById('alltime').addEventListener('click', applyAllTime);

    // Stats races à chaque redraw
    $('#progressTable').on('draw.dt', function () {
        updateRaceStats();
    });

    // État initial
    applyPreset(7);
    setActiveMode('last7');
    setActivePageSize(10);
});
</script>

</body>
</html>
"""

# =====================
# WRITE FILE
# =====================
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ index.html généré avec succès")