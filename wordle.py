from zipfile import ZipFile
import re
from datetime import date, timedelta

WORDLE = "Wordle"
MAX = 100
NO_MEDAL = 0
BRONZE = 1
SILVER = BRONZE * 100
GOLD = SILVER * 100
MS = 86400000
MEDALS = [GOLD, SILVER, BRONZE]

MEDAL_SYMBOLS = {
  NO_MEDAL: "",
  "G": '🥇',
  "S": '🥈',
  "B": '🥉'
};

MEDAL_NAMES = {
  NO_MEDAL: "",
  GOLD: 'G',
  SILVER: 'S',
  BRONZE: 'B'
};

SYMBOLS = {
  "❎": -1,
  "0️⃣": 0,
  "1️⃣": 1,
  "2️⃣": 2,
  "3️⃣": 3,
  "4️⃣": 4,
  "5️⃣": 5,
  "6️⃣": 6,
  "7️⃣": 7,
  "8️⃣": 8,
  "9️⃣": 9,
  "🔟": 10,
  "🕚": 11,
  "🕛": 12,
  "🕐": 13,
  "⓮": 14,
  "⓯": 15,
  "🟥": MAX
}

GAMES = {
    WORDLE: {
      "day": date(2021, 6, 19),
      "heading": 'W',
      "json": 'wordle',
      "useBoard": False
    },
    # "Wortel": {
    #   "day": date(2022, 1, 31),
    #   "heading": '🥕',
    #   "json": 'wortel',
    #   "useBoard": False
    # },
    "Daily Quordle": {
      "day": date(2022, 1, 24),
      "heading": 'Q',
      "json": 'quordle',
      "useBoard": True,
      "max": 10
    },
    "Daily Sequence Quordle": {
      "day": date(2022, 1, 24),
      "heading": 'SQ',
      "json": 'sequenceQuordle',
      "useBoard": True,
      "max": 10
    },
    "Daily Octordle": {
      "day": date(2022, 1, 24),
      "heading": 'O',
      "json": 'octordle',
      "useBoard": True,
      "max": 14
    },
    "Daily Sequence Octordle": {
      "day": date(2022, 1, 24),
      "heading": 'SO',
      "json": 'sequenceOctordle',
      "useBoard": True,
      "max": 16
    },
    "nerdlegame": {
      "day": date(2022, 1, 19),
      "heading": 'N',
      "json": 'nerdle',
      "useBoard": False
    },
    "Obsessie": {
      "day": date(2025, 7, 15),
      "heading": '🌀',
      "json": 'obsessie',
      "useBoard": False
    }
}

def format_score(game, score, medal):
    medal_symbol = MEDAL_SYMBOLS.get(medal, "")
    if score is None or score < 0:
        return "❎"
    if game["useBoard"]:
        return str(score) + medal_symbol
    for k, v in SYMBOLS.items():
        if v == score:
            return k + medal_symbol
    


def calc_score(board, max_score):
    score = 0
    for symbol, value in SYMBOLS.items():
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
        game_keys = [key for key in GAMES if key in game_name]
        if not game_keys:
            continue
        game_key = game_keys[0]
        game = GAMES[game_key]
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
                "medal": NO_MEDAL,
            }
        )
    return plays


def group_plays_by_date_and_game(plays):
    grouped = {}
    for play in plays:
        play_date = play["date"]
        game_key = play["game"]
        if play_date not in grouped:
            grouped[play_date] = {key: [] for key in GAMES.keys()}
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
                game = GAMES[play["game"]]
                medal = play.get("medal")
                player_day["total"] += medal
                player_day["golds"] += 1 if medal == GOLD else 0
                player_day["silvers"] += 1 if medal == SILVER else 0
                player_day["bronzes"] += 1 if medal == BRONZE else 0
                turnsKey = game["json"] + "Score"
                medalsKey = game["json"] + "Medal"
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


def daily_results_summary(results, target_date):
    day_summary = []
    start_date = target_date.replace(day=1)
    month_results = [p for p in results if start_date <= p["day"] <= target_date]
    names = set({p["name"] for p in month_results})
    for name in names:
        player = {}
        medals = []
        player["name"] = name
        player["position"] = 9999
        day_results = [
            p for p in month_results if p["name"] == name and p["day"] == target_date
        ]
        if day_results:
            day_result = day_results[0]
            for game in GAMES.values():
                scoreKey = game["json"] + "Score"
                medalsKey = game["json"] + "Medal"
                score = day_result.get(scoreKey, -1)
                medal = day_result.get(medalsKey, "")
                heading = game["heading"]
                player["position"] = day_result["position"]
                player[heading] = format_score(game, score, medal)
                medals.append(MEDAL_SYMBOLS.get(medal, ""))
        player["wins"] = sum(
            [1 for p in month_results if p["name"] == name and p["position"] == 1]
        )
        player["medals"] = "".join(sorted(medals))
        day_summary.append(player)
    return day_summary


def html(chats, target_date):
    chats = clean_chats(chats)
    plays = parse_plays(chats)
    grouped_by_date_and_game = group_plays_by_date_and_game(plays)
    assign_medals(grouped_by_date_and_game)
    persons = day_results_per_player(grouped_by_date_and_game)
    day_summary = daily_results_summary(persons, target_date)
    table = f'<table class="table table-bordered table-sm table-striped border-primary"><tr><th scope="col">{target_date}</th><th>'
    table += "</th><th>".join([g["heading"] for g in GAMES.values()])
    table += "</th><th>🏆</th><th>Medals</th></tr>"
    for player in sorted(day_summary, key=lambda x: (x["position"], x["name"])):
        table += f"<tr><td>{player['name']}</td><td>"
        table += "</td><td>".join(
            [player.get(g["heading"], "") for g in GAMES.values()]
        )
        table += f"<td>{player['wins']}</td><td>{player['medals']}</td></tr>"
    table += "</table></body></html>"
    html_content = f'''
        <html lang="en">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Wordle</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
            </head>
            <body>
                {table}
            </body>
        </html>
    '''
    return html_content


def main():
    chats = load_chats("./data/export.zip", "_chat.txt")
    end_date = date(2025, 8, 23)
    html_output = html(chats, end_date)
    print(html_output)


if __name__ == "__main__":
    main()
