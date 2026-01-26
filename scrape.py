import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# CONFIGURATION: Add your movie picks here (must match the name on the website exactly)
PLAYERS = {
    "Player 1": {
        "picks": ["Gladiator II", "Wicked", "Moana 2"],
        "bomb": "Sonic the Hedgehog 3"
    },
    "Player 2": {
        "picks": ["Mufasa: The Lion King", "Nosferatu", "A Complete Unknown"],
        "bomb": "Better Man"
    },
    "Player 3": {
        "picks": ["Paddington in Peru", "Captain America: Brave New World", "Snow White"],
        "bomb": "The Amateur"
    }
}

URL = "https://www.fantasyboxofficegame.com/calendar"
DATA_FILE = "data.json"

def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the movie table - based on the source structure
    movies = {}
    rows = soup.find_all('tr', class_=lambda x: x and 'cursor-pointer' in x)
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3: continue
        
        title = cols[1].get_text(strip=True)
        # Domestic Box Office is typically the 3rd or 4th column
        # Profit/Loss or Multiplier is usually later
        try:
            raw_bo = cols[2].get_text(strip=True).replace('$', '').replace(',', '')
            box_office = float(raw_bo) if raw_bo else 0.0
            
            # Assuming the 'Net' or 'Performance' is in a specific column 
            # If not available, we use the raw Box Office
            performance = box_office 
        except:
            performance = 0.0

        movies[title] = performance

    # Process Player Data
    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "players": {}
    }

    for player, data in PLAYERS.items():
        total = sum(movies.get(m, 0) for m in data["picks"])
        bomb_perf = movies.get(data["bomb"], 0)
        snapshot["players"][player] = {
            "total": total,
            "bomb": bomb_perf,
            "movies": {m: movies.get(m, 0) for m in data["picks"]}
        }

    # Store Data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []

    history.append(snapshot)
    
    # Keep only the last 100 entries to save space
    with open(DATA_FILE, 'w') as f:
        json.dump(history[-100:], f, indent=2)

if __name__ == "__main__":
    scrape()