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
                "points": p["points"]
            })

# =====================
# HTML GENERATION
# =====================
html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Classements BloodWars</title>
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
/* Top filters + race stats side by side */
.top-filters {{
    display:flex;
    justify-content:space-between;
    align-items:flex-start;
    margin-bottom:20px;
}}
.filters {{
    flex:1;
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
/* Supprimer flèches de tri */
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
    padding: 5px 10px;
    cursor: pointer;
}}

/* Correction couleur menu "Afficher X entrées" DataTables */
.dataTables_length select {{
    background-color: #222 !important;
    color: #eee !important;
    border: 1px solid #444 !important;
    padding: 2px 4px;
}}
</style>

<!-- DataTables -->
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css">
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>

</head>
<body>

<h1>Classements BloodWars – Top 200</h1>

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

html += "<br><strong>Races :</strong><br>"
races = sorted(list({p["race"] for p in all_players}))
for r in races:
    html += f"""
<label>
<input type="checkbox" class="race-filter" value="{r}" checked>
{r}
</label>
"""

# date selection + presets
html += "<br><br><strong>Durée / Dates :</strong><br>"
html += "De : <select id='date_start'>"
for d in dates_sorted:
    html += f"<option value='{d}'>{d}</option>"
html += "</select> À : <select id='date_end'>"
for d in dates_sorted:
    selected = "selected" if d == dates_sorted[-1] else ""
    html += f"<option value='{d}' {selected}>{d}</option>"
html += "</select>"

# boutons presets 7/30 jours
html += """
<div class="button-group">
<button id="last7">7 derniers jours</button>
<button id="last30">30 derniers jours</button>
</div>
</div>

  <div id="raceStats">
    <!-- Stats races ici -->
  </div>
</div>

<h2>Tableau de progression globale</h2>
<table id="progressTable" class="display">
<thead>
<tr>
<th>Joueur</th>
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
// Données envoyées depuis Python
const allData = """ + str(all_players).replace("'", '"') + """;
const dates_sorted = """ + str(dates_sorted).replace("'", '"') + """;

function updateProgression() {
    const selectedServers = Array.from(document.querySelectorAll('.server-filter:checked')).map(cb => cb.value);
    const selectedRaces = Array.from(document.querySelectorAll('.race-filter:checked')).map(cb => cb.value);
    const dateStart = document.getElementById('date_start').value;
    const dateEnd = document.getElementById('date_end').value;

    const scores = {};
    allData.forEach(p => {
        const key = p.name + '||' + p.server + '||' + p.race;
        if (!scores[key]) scores[key] = {};
        scores[key][p.date] = p.points;
        scores[key].display_server = p.display_server;
    });

    let tableData = [];
    for (let key in scores) {
        const [name, server, race] = key.split('||');
        if (!selectedServers.includes(server) || !selectedRaces.includes(race)) continue;
        const startScore = scores[key][dateStart] || 0;
        const endScore = scores[key][dateEnd] || 0;
        const prog = endScore - startScore;
        tableData.push({name, server, race, display_server: scores[key].display_server, startScore, endScore, prog});
    }

    const dt = $('#progressTable').DataTable();
    dt.clear();
    dt.rows.add(tableData.map(p => [p.name,p.display_server,p.race,p.startScore,p.endScore,p.prog]));
    dt.draw();
    updateRaceStats(); // mettre à jour les stats races
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
}

// fonction pour compter races affichées selon Top N
function updateRaceStats() {
    const dt = $('#progressTable').DataTable();
    const raceCounts = {};
    let total = 0;
    let rowsData = dt.rows({ search: 'applied', order: 'applied' }).data().toArray();
    const topN = dt.page.len();
    rowsData = rowsData.slice(0, topN);
    rowsData.forEach(row => {
        const race = row[2];
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
        "order": [[5,"desc"]]
    });

    document.querySelectorAll('.server-filter, .race-filter').forEach(el => {
        el.addEventListener('change', updateProgression);
    });
    document.getElementById('date_start').addEventListener('change', updateProgression);
    document.getElementById('date_end').addEventListener('change', updateProgression);
    document.getElementById('last7').addEventListener('click', ()=> applyPreset(7));
    document.getElementById('last30').addEventListener('click', ()=> applyPreset(30));

    $('#progressTable').on('draw.dt', function () {
        updateRaceStats();
    });

    updateProgression();
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