import sys

sys.path.append("/workspaces/leaderboard/")

import unittest
import json
import os
from unittest.mock import patch
from datetime import date
from wordle import (
    daily_results_summary,
    load_chats,
    clean_chats,
    parse_plays,
    group_plays_by_date_and_game,
    assign_medals,
    day_results_per_player,
)


def read_json(path):
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "r") as f:
        return json.load(f)


def read_chats(path):
    abs_path = os.path.join(os.path.dirname(__file__), path)
    with open(abs_path, "r") as f:
        return f.read()


class TestWordle(unittest.TestCase):
    def setUp(self):
        # read json from file
        self.expected = read_json("./expected.json")
        self.expected.sort(key=lambda x: x["name"])
        self.maxDiff = None  # to see full diff on failure
        self.chats = read_chats("./chats.txt")

    def test_parse_plays(self):
        chats = clean_chats(self.chats)
        plays = parse_plays(chats)
        actual = [(play["person"], play["heading"], play["score"]) for play in plays]
        # order by person, then by score
        actual.sort(key=lambda x: (x[0], x[1]))
        expected = [
            ("Alan", "N", 3),
            ("Alan", "O", 70),
            ("Alan", "Q", 22),
            ("Alan", "SO", 71),
            ("Alan", "SQ", 19),
            ("Alan", "W", 3),
            ("Alan", "🌀", 5),
            ("Buzz", "N", 4),
            ("Buzz", "O", 59),
            ("Buzz", "Q", 22),
            ("Buzz", "SO", 74),
            ("Buzz", "SQ", 21),
            ("Buzz", "W", 3),
            ("Buzz", "🌀", 4),
            ("Michael", "O", 62),
            ("Michael", "Q", 22),
            ("Michael", "SO", 68),
            ("Michael", "SQ", 26),
            ("Michael", "W", 4),
            ("Michael", "🌀", 4),
            ("Neil", "N", 3),
            ("Neil", "O", 61),
            ("Neil", "Q", 22),
            ("Neil", "SO", 66),
            ("Neil", "SQ", 23),
            ("Neil", "W", 4),
            ("Neil", "🌀", 4),
            ("Pete", "N", 4),
            ("Pete", "O", 68),
            ("Pete", "Q", 27),
            ("Pete", "SO", 79),
            ("Pete", "SQ", 22),
            ("Pete", "🌀", 4),
        ]
        self.assertEqual(actual, expected)

    def test_assign_medals(self):
        chats = clean_chats(self.chats)
        plays = parse_plays(chats)
        grouped = group_plays_by_date_and_game(plays)
        assign_medals(grouped)
        actual = [
            (play["person"], play["heading"], play["score"], play.get("medal"))
            for game in grouped[date(2025, 8, 23)].values()
            for play in game
        ]
        actual.sort(key=lambda x: (x[1], x[2]))
        expected = [
            ("Neil", "N", 3, 10000),
            ("Alan", "N", 3, 10000),
            ("Buzz", "N", 4, 1),
            ("Pete", "N", 4, 1),
            ("Buzz", "O", 59, 10000),
            ("Neil", "O", 61, 100),
            ("Michael", "O", 62, 1),
            ("Pete", "O", 68, 0),
            ("Alan", "O", 70, 0),
            ("Neil", "Q", 22, 10000),
            ("Buzz", "Q", 22, 10000),
            ("Alan", "Q", 22, 10000),
            ("Michael", "Q", 22, 10000),
            ("Pete", "Q", 27, 0),
            ("Neil", "SO", 66, 10000),
            ("Michael", "SO", 68, 100),
            ("Alan", "SO", 71, 1),
            ("Buzz", "SO", 74, 0),
            ("Pete", "SO", 79, 0),
            ("Alan", "SQ", 19, 10000),
            ("Buzz", "SQ", 21, 100),
            ("Pete", "SQ", 22, 1),
            ("Neil", "SQ", 23, 0),
            ("Michael", "SQ", 26, 0),
            ("Buzz", "W", 3, 10000),
            ("Alan", "W", 3, 10000),
            ("Neil", "W", 4, 1),
            ("Michael", "W", 4, 1),
            ("Neil", "🌀", 4, 10000),
            ("Buzz", "🌀", 4, 10000),
            ("Pete", "🌀", 4, 10000),
            ("Michael", "🌀", 4, 10000),
            ("Alan", "🌀", 5, 0),
        ]
        self.assertEqual(actual, expected)

    def test_day_results_per_player(self):
        chats = clean_chats(self.chats)
        plays = parse_plays(chats)
        grouped_by_date_and_game = group_plays_by_date_and_game(plays)
        assign_medals(grouped_by_date_and_game)
        actual = day_results_per_player(grouped_by_date_and_game)
        actual.sort(key=lambda x: x["name"])
        for x in actual:
            x["day"] = str(x["day"])

        self.assertEqual(actual, self.expected)

    def test_day_results_per_player(self):
        chats = clean_chats(self.chats)
        plays = parse_plays(chats)
        grouped_by_date_and_game = group_plays_by_date_and_game(plays)
        assign_medals(grouped_by_date_and_game)
        player_results = day_results_per_player(grouped_by_date_and_game)
        end_date = date(2025, 8, 23)
        actual = daily_results_summary(player_results, end_date)
        expected = [
            {
                "O": "62🥉",
                "Q": "22🥇",
                "SO": "68🥈",
                "SQ": "26",
                "medals": "🥇🥇🥈🥉🥉",
                "W": "4️⃣",
                "N": "❎", 
                "name": "Michael",
                "🌀": "4️⃣",
                "📅": 0,
                "position": 4,
            },
            {
                "N": "3️⃣",
                "O": "61🥈",
                "Q": "22🥇",
                "SO": "66🥇",
                "SQ": "23",
                "medals": "🥇🥇🥇🥇🥈🥉",
                "W": "4️⃣",
                "name": "Neil",
                "🌀": "4️⃣",
                "📅": 1,
                "position": 1,
            },
            {
                "N": "3️⃣",
                "O": "70",
                "Q": "22🥇",
                "SO": "71🥉",
                "SQ": "19🥇",
                "medals": "🥇🥇🥇🥇🥉",
                "W": "3️⃣",
                "name": "Alan",
                "🌀": "5️⃣",
                "📅": 0,
                "position": 3,
            },
            {
                "N": "4️⃣",
                "O": "68",
                "Q": "27",
                "SO": "79",
                "SQ": "22🥉",
                "medals": "🥇🥉🥉",
                "W": "❎",
                "name": "Pete",
                "🌀": "4️⃣",
                "📅": 0,
                "position": 5,
            },
            {
                "N": "4️⃣",
                "O": "59🥇",
                "Q": "22🥇",
                "SO": "74",
                "SQ": "21🥈",
                "medals": "🥇🥇🥇🥇🥈🥉",
                "W": "3️⃣",
                "name": "Buzz",
                "🌀": "4️⃣",
                "📅": 1,
                "position": 1,
            },
        ]
        self.assertCountEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
