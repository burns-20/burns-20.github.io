import csv
import os
from collections import defaultdict

# =====================
# CONFIG
# =====================
CSV_FILE = "bloodwars_classement.csv"
OUTPUT_HTML = "index.html"

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

print(f"📄 Dates chargées : {len(data)}")

# =====================
# HTML GENERATION
# =====================
html = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Classements BloodWars</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #111;
    color: #eee;
    padding: 20px;
}
h1, h2 {
    color: #f5c542;
}
.filters {
    margin-bottom: 20px;
}
.filters label {
    margin-right: 15px;
    cursor: pointer;
}
.server-block {
    margin-bottom: 40px;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
}
th, td {
    border: 1px solid #444;
    padding: 6px;
    text-align: left;
}
th {
    background: #222;
}
</style>

<script>
function toggleServers() {
    const checked = Array.from(document.querySelectorAll(".server-filter"))
        .filter(cb => cb.checked)
        .map(cb => cb.value);

    document.querySelectorAll(".server-block").forEach(div => {
        div.style.display = checked.includes(div.dataset.server) ? "block" : "none";
    });
}
</script>
</head>
<body>

<h1>Classements BloodWars – Top 200</h1>

<div class="filters">
<strong>Serveurs :</strong><br>
"""

for s in ["R1", "R2", "R4", "R3", "R7", "R14"]:
    html += f"""
<label>
<input type="checkbox" class="server-filter" value="{s}" checked onchange="toggleServers()">
{s}
</label>
"""

html += "</div>"

# =====================
# CONTENT
# =====================
for date in sorted(data.keys(), reverse=True):
    html += f"<h2>Date : {date}</h2>"

    for server in sorted(data[date].keys()):
        region = "FR" if server in FR_SERVERS else "PL"

        html += f"""
<div class="server-block" data-server="{server}">
<h3>{server} ({region})</h3>
<table>
<tr>
<th>Position</th>
<th>Nom</th>
<th>Race</th>
<th>Points</th>
</tr>
"""

        for p in sorted(data[date][server], key=lambda x: x["position"]):
            html += f"""
<tr>
<td>{p['position']}</td>
<td>{p['name']}</td>
<td>{p['race']}</td>
<td>{p['points']}</td>
</tr>
"""

        html += "</table></div>"

html += """
<script>
toggleServers();
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