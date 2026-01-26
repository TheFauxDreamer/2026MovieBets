import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# CONFIGURATION
PLAYERS = {
    "Ethan": {
        "picks": ["The Super Mario Galaxy Movie", "Cold Storage", "GOAT", "Iron Lung", "You, Me & Tuscany", "The Moment", "Shelter"],
        "bomb": "Supergirl: Woman of Tomorrow"
    },
    "Paul": {
        "picks": ["Spider-Man: Brand New Day", "Project Hail Mary", "Ready or Not 2: Here I Come", "Wuthering Heights", "Reminders of Him", "The Undertone", "Lee Cronin's The Mummy"],
        "bomb": "Resident Evil"
    },
    "Timms": {
        "picks": ["The Odyssey", "Michael", "Scream 7", "Hoppers", "The Drama", "The Pout-Pout Fish", "Scarlet"],
        "bomb": "Street Fighter"
    }
}

URL = "https://www.fantasyboxofficegame.com/calendar"
DATA_FILE = "data.json"

def scrape():
    try:
        response = requests.get(URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    movies = {}
    # Target the specific rows found in the provided source
    rows = soup.find_all('tr', class_='cursor-pointer')
    
    for row in rows:
        # Title is in the second cell (index 1)
        cols = row.find_all('td')
        if len(cols) < 3: continue
        
        title = cols[1].get_text(strip=True)
        
        # Pull the 'Net' or 'Box Office' value. 
        # Using index 2 as per the table structure in the source
        raw_val = cols[2].get_text(strip=True).replace('$', '').replace(',', '')
        
        try:
            if 'M' in raw_val:
                value = float(raw_val.replace('M', '')) * 1_000_000
            elif 'K' in raw_val:
                value = float(raw_val.replace('K', '')) * 1_000
            else:
                value = float(raw_val)
        except ValueError:
            value = 0.0
            
        movies[title] = value

    snapshot = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "players": {}
    }

    for player, data in PLAYERS.items():
        movie_results = {m: movies.get(m, 0.0) for m in data["picks"]}
        # Total = Sum of picks minus the Bomb performance
        bomb_penalty = movies.get(data["bomb"], 0.0)
        total_score = sum(movie_results.values()) - bomb_penalty
        
        snapshot["players"][player] = {
            "total": total_score,
            "bomb": bomb_penalty,
            "movies": movie_results
        }

    # Maintain history
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                history = json.load(f)
            except: history = []
    else:
        history = []

    history.append(snapshot)
    with open(DATA_FILE, 'w') as f:
        json.dump(history[-100:], f, indent=2)

if __name__ == "__main__":
    scrape()
