import requests
import json

API_KEY = "34298185cbmshd11d8fed41ad3a9p167782jsnd9b2e9b554d9"
url_leagues = "https://free-api-live-football-data.p.rapidapi.com/football-get-all-leagues-with-countries"
headers = {
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}

response = requests.get(url_leagues, headers=headers)
data = response.json()

# Buscar ligas que contengan "Ukraine"
for country in data["response"]["leagues"]:
    if country["name"].lower() == "ukraine":
        print(json.dumps(country, indent=2))
