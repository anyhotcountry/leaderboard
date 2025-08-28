from zipfile import ZipFile
import re
from datetime import date, timedelta
from games import games, symbols, MAX, MEDALS, GOLD, SILVER, BRONZE, NO_MEDAL, MEDAL_NAMES
import json


def calc_score(board, max_score):
    score = 0
    for symbol, value in symbols.items():
        count = board.count(symbol)
        score += count * min(max_score, value)
    return score


def load_chats(zip_path, chat_filename):
    with ZipFile(zip_path, "r") as zf:
        chat_bytes = zf.read(chat_filename)
        chats = chat_bytes.decode()
    return chats


def clean_chats(chats):
    for emoji in [" 🎉", "🙂 ", "🥕 ", "🌀 "]:
        chats = chats.replace(emoji, "")
    return chats


def parse_plays(chats):
    pattern = r"\[\d+\/\d+\/\d+, \d+:\d+:\d+\] ([A-Za-z é&]+): \s*([ ([A-Za-z ]+) #?(\d,?\d+)( (\d)\/(\d))?([^\[]+)"
    matches = re.findall(pattern, chats)
    plays = []
    for match in matches:
        name = match[0].split()[0]
        game_name = match[1]
        game_keys = [key for key in games if key in game_name]
        if not game_keys:
            continue
        game_key = game_keys[0]
        game = games[game_key]
        day = int(match[2].replace(",", ""))
        game_date = game["day"] + timedelta(days=day)
        board = ""
        score = MAX
        if game["useBoard"]:
            board = match[6]
            score = calc_score(board, game["max"])
        elif match[4]:
            score = int(match[4])
        plays.append(
            {
                "date": game_date,
                "person": name,
                "heading": game["heading"],
                "game": game_key,
                "score": score,
                "medal": NO_MEDAL
            }
        )
    return plays

def group_plays_by_date_and_game(plays):
    grouped = {}
    for play in plays:
        play_date = play["date"]
        game_key = play["game"]
        if play_date not in grouped:
            grouped[play_date] = {key: [] for key in games.keys()}
        grouped[play_date][game_key].append(play)
    return grouped


def assign_medals(grouped):
    for day_games in grouped.values():
        for players in day_games.values():
            scores = sorted([player["score"] for player in players])
            medals = {score: NO_MEDAL for score in set(scores)} 
            medal_index = 0
            last_score = 0
            # Go through scores and assign medals
            for score in scores:
                if score > last_score:
                    if medal_index >= 3:
                        break
                    medals[score] = MEDALS[medal_index]
                last_score = score
                medal_index += 1
            # Assign medals to players
            for player in players:
                player["medal"] = medals[player["score"]]

def day_results_per_player(grouped):
    results = []
    for day, day_games in grouped.items():
        day_results = []
        # merge all plays for the day
        plays = [play for game_plays in day_games.values() for play in game_plays]
        persons = {play["person"] for play in plays}
        players = set(persons)
        for player in players:
            player_day = {
                "name": player,
                "day": day,
                "golds": 0,
                "silvers": 0,
                "bronzes": 0,
                "total": 0,
            }
            player_plays = [play for play in plays if play["person"] == player]
            for play in player_plays:
                game = games[play["game"]]
                medal = play.get("medal")
                player_day["total"] += medal
                player_day["golds"] += 1 if medal == GOLD else 0
                player_day["silvers"] += 1 if medal == SILVER else 0
                player_day["bronzes"] += 1 if medal == BRONZE else 0
                turnsKey = game["json"]+"Score"
                medalsKey = game["json"]+"Medal"
                player_day[turnsKey] = play.get("score")
                player_day[medalsKey] = MEDAL_NAMES[medal]
            day_results.append(player_day)
            results.append(player_day)
          # Rank players by total, assigning positions (handling ties)
        sorted_players = sorted(day_results, key=lambda x: x["total"], reverse=True)
        count = 0
        last_total = -1
        last_position = 0
        for player in sorted_players:
            count += 1
            if player["total"] != last_total:
                player["position"] = count
                last_position = count
            else:
                player["position"] = last_position
            last_total = player["total"]
    return results


def main():
    chats = load_chats("./data/export.zip", "_chat.txt")
    chats = clean_chats(chats)
    plays = parse_plays(chats)
    grouped = group_plays_by_date_and_game(plays)
    assign_medals(grouped)
    persons = day_results_per_player(grouped)
    day = date.today() - timedelta(days=2)


if __name__ == "__main__":
    main()
