import os
import time
import re
import csv
from datetime import date
from collections import Counter
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# =====================
# CONFIG SERVEURS
# =====================
SERVERS = [
    # -------- FR --------
    {
        "code": "R1",
        "portal": "https://fr.bloodwars.net",
        "server_url": "https://r1.fr.bloodwars.net",
        "realm": "201",
        "races": [
            "CAPTEUR D’ESPRIT",
            "ABSORBEUR",
            "SEIGNEUR DES BÊTES",
            "CULTISTE",
            "DAMNÉ"
        ]
    },
    {
        "code": "R2",
        "portal": "https://fr.bloodwars.net",
        "server_url": "https://r2.fr.bloodwars.net",
        "realm": "202",
        "races": [
            "CAPTEUR D’ESPRIT",
            "ABSORBEUR",
            "SEIGNEUR DES BÊTES",
            "CULTISTE",
            "DAMNÉ"
        ]
    },
    {
        "code": "R4",
        "portal": "https://fr.bloodwars.net",
        "server_url": "https://r4.fr.bloodwars.net",
        "realm": "204",
        "races": [
            "CAPTEUR D’ESPRIT",
            "ABSORBEUR",
            "SEIGNEUR DES BÊTES",
            "CULTISTE",
            "DAMNÉ"
        ]
    },

    # -------- PL --------
    {
        "code": "R3",
        "portal": "https://bloodwars.pl",
        "server_url": "https://r3.bloodwars.pl",
        "realm": "3",
        "races": [
            "ŁAPACZ MYŚLI",
            "SSAK",
            "WŁADCA ZWIERZĄT",
            "KULTYSTA",
            "POTĘPIONY"
        ]
    },
    {
        "code": "R7",
        "portal": "https://bloodwars.pl",
        "server_url": "https://r7.bloodwars.pl",
        "realm": "7",
        "races": [
            "ŁAPACZ MYŚLI",
            "SSAK",
            "WŁADCA ZWIERZĄT",
            "KULTYSTA",
            "POTĘPIONY"
        ]
    },
    {
        "code": "R14",
        "portal": "https://bloodwars.pl",
        "server_url": "https://r14.bloodwars.pl",
        "realm": "14",
        "races": [
            "ŁAPACZ MYŚLI",
            "SSAK",
            "WŁADCA ZWIERZĄT",
            "KULTYSTA",
            "POTĘPIONY"
        ]
    },
]

# =====================
# CSV
# =====================

CSV_PATH = r"C:\Users\Julien\Desktop\bots\burns-20.github.io\bloodwars_classement.csv"
TODAY = date.today().isoformat()

# =====================
# ENV
# =====================
load_dotenv()

# =====================
# DRIVER
# =====================
options = Options()
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 20)

# =====================
# UTILS
# =====================
def is_connected():
    if driver.find_elements(By.NAME, "login"):
        return False
    if driver.find_elements(By.NAME, "password"):
        return False
    return True

def get_credentials(server_code):
    login = os.getenv(f"BW_{server_code}_LOGIN")
    password = os.getenv(f"BW_{server_code}_PASSWORD")
    if not login or not password:
        raise Exception(f"❌ Identifiants manquants pour {server_code}")
    return login, password

# =====================
# CSV INIT
# =====================
file_exists = os.path.isfile(CSV_PATH)
csv_file = open(CSV_PATH, "a", newline="", encoding="utf-8")
writer = csv.DictWriter(
    csv_file,
    fieldnames=["date", "server", "position", "name", "race", "points"],
    delimiter=";",
    quoting=csv.QUOTE_ALL
)

if not file_exists:
    writer.writeheader()

# =====================
# MAIN LOOP
# =====================
for server in SERVERS:
    SERVER_CODE = server["code"]
    PORTAL_URL = server["portal"]
    SERVER_URL = server["server_url"]
    REALM_VALUE = server["realm"]
    RACES = server["races"]

    LOGIN, PASSWORD = get_credentials(SERVER_CODE)

    print(f"\n🌍 Ouverture portail {SERVER_CODE}")
    driver.get(PORTAL_URL)

    wait.until(EC.presence_of_element_located((By.NAME, "login")))

    Select(driver.find_element(By.ID, "i_realm")).select_by_value(REALM_VALUE)
    driver.find_element(By.NAME, "login").send_keys(LOGIN)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    time.sleep(3)

    links = driver.find_elements(By.XPATH, "//a[contains(text(),'Cliquez ici')]")
    if links:
        driver.execute_script("arguments[0].click();", links[0])
        time.sleep(3)

    print(f"📍 URL actuelle : {driver.current_url}")

    if not driver.current_url.startswith(SERVER_URL):
        print(f"❌ Échec connexion {SERVER_CODE}")
        continue

    if not is_connected():
        print(f"❌ Toujours sur un formulaire ({SERVER_CODE})")
        continue

    print(f"✅ Connecté au serveur {SERVER_CODE}")

    for page in range(1, 5):
        print(f"📊 Lecture classement page {page}")
        driver.get(f"{SERVER_URL}/?a=rank&page={page}")
        time.sleep(3)

        rows = driver.find_elements(By.XPATH, "//tr")

        for row in rows:
            text = row.text.strip()
            if not text or text.startswith("PLACE NOM") or not re.match(r"^\d+\.", text):
                continue

            parts = text.split()

            try:
                position = int(parts[0].replace(".", ""))
                points = int(parts[-1])

                race = None
                race_index = None
                for r in RACES:
                    r_parts = r.split()
                    for i in range(len(parts)):
                        if parts[i:i+len(r_parts)] == r_parts:
                            race = r
                            race_index = i
                            break
                    if race:
                        break

                if race is None:
                    continue

                name = " ".join(parts[1:race_index])

                writer.writerow({
                    "date": TODAY,
                    "server": SERVER_CODE,
                    "position": position,
                    "name": name,
                    "race": race,
                    "points": points
                })

            except Exception:
                continue

csv_file.close()
driver.quit()

print("\n✅ Scraping terminé – CSV mis à jour")