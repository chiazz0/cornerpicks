from telegram import Bot
from telegram.utils.request import Request
import time
import requests
import re

BOT_TOKEN = "8768687936:AAFZ5jGgDZjqo0OSmhFVPTKrAJWr52fzQA0"
CHAT_ID = -1003788581481
API_KEY = "34298185cbmshd11d8fed41ad3a9p167782jsnd9b2e9b554d9"

request = Request(con_pool_size=8)
bot = Bot(token=BOT_TOKEN, request=request)

url_matches = "https://free-api-live-football-data.p.rapidapi.com/football-current-live"
url_leagues = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-leagues-with-countries"

headers = {
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

league_map = {}
notified_matches = set()
last_reset = time.time()  # ⏱️ control para reinicio cada hora

def load_leagues():
    global league_map
    response = requests.get(url_leagues, headers=headers)
    print(f"Estado de respuesta ligas: {response.status_code}")

    try:
        data = response.json()
    except Exception as e:
        print(f"Error al convertir JSON: {e}")
        return

    leagues_data = data.get("response", {}).get("leagues", [])
    print(f"Cantidad de países en respuesta: {len(leagues_data)}")

    for country in leagues_data:
        if isinstance(country, dict):
            for league in country.get("leagues", []):
                league_map[league["id"]] = {
                    "name": league["name"],
                    "country": country["name"]
                }

    print(f"Ligas cargadas: {len(league_map)}")

def parse_minute(live_time):
    short_val = live_time.get("short", "")
    try:
        match = re.match(r"(\d+)", short_val.strip())
        if match:
            return int(match.group(1))
        return 0
    except Exception as e:
        print(f"Error parseando minuto: {e}")
        return 0

def check_matches():
    global last_reset, notified_matches

    # ♻️ Reinicio del filtro cada hora
    if time.time() - last_reset > 3600:
        notified_matches.clear()
        last_reset = time.time()
        print("♻️ Reiniciando filtro de partidos notificados...")

    print("Revisando partidos en vivo...")
    response = requests.get(url_matches, headers=headers)
    print(f"Estado de respuesta partidos: {response.status_code}")
    try:
        matches = response.json()
    except Exception as e:
        print(f"Error al convertir JSON de partidos: {e}")
        return

    for match in matches.get("response", {}).get("live", []):
        match_id = match["id"]
        if match_id in notified_matches:
            continue  # ya fue notificado

        home = match["home"]["name"]
        away = match["away"]["name"]
        score_home = int(match["home"]["score"])
        score_away = int(match["away"]["score"])
        minute = parse_minute(match["status"]["liveTime"])
        league_id = match.get("leagueId")

        diff = abs(score_home - score_away)
        print(f"DEBUG: {home} vs {away} | Minuto={minute} | Marcador={score_home}-{score_away} | Diff={diff}")

        league_info = league_map.get(league_id, {"name": "Desconocida", "country": "N/A"})
        league_name = league_info["name"]
        league_country = league_info["country"]

        # Condiciones ajustadas: minuto entre 83 y 89 inclusive
        if diff <= 1 and 83 <= minute < 90:
            mensaje = (
                f"⚽ ALERTA: {home} vs {away}\n"
                f"Marcador: {score_home}-{score_away}\n"
                f"Minuto: {minute}\n"
                f"Liga: {league_name} ({league_country})\n"
                f"👉 Pick sugerido"
            )
            print(f"✅ Enviando alerta: {mensaje}")
            bot.send_message(chat_id=CHAT_ID, text=mensaje)
            notified_matches.add(match_id)

print("🔔 Enviando mensaje de prueba al grupo...")
bot.send_message(chat_id=CHAT_ID, text="✅ Test de conexión: el bot está funcionando.")

if __name__ == "__main__":
    load_leagues()
    while True:
        check_matches()
        time.sleep(60)
