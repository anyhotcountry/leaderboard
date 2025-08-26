from datetime import date

WORDLE = "Wordle"
MAX = 100
BRONZE = 1
SILVER = BRONZE * 100
GOLD = SILVER * 100
MS = 86400000
MEDALS = [GOLD, SILVER, BRONZE]

MEDAL_SYMBOLS = {
  GOLD: '🥇',
  SILVER: '🥈',
  BRONZE: '🥉'
};

MEDAL_NAMES = {
  GOLD: 'G',
  SILVER: 'S',
  BRONZE: 'B'
};

symbols = {
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

games = {
    WORDLE: {
      "day": date(2021, 6, 19),
      "heading": 'W',
      "json": 'wordle',
      "useBoard": False,
      "ignore": 0,
      "turns": []
    },
    "Wortel": {
      "day": date(2022, 1, 31),
      "heading": '🥕',
      "json": 'wortel',
      "useBoard": False,
      "ignore": 0,
      "turns": []
    },
    "Daily Quordle": {
      "day": date(2022, 1, 24),
      "heading": 'Q',
      "json": 'quordle',
      "useBoard": True,
      "ignore": 0,
      "max": 10,
      "turns": []
    },
    "Daily Sequence Quordle": {
      "day": date(2022, 1, 24),
      "heading": 'SQ',
      "json": 'sequenceQuordle',
      "useBoard": True,
      "ignore": 570,
      "max": 10,
      "turns": []
    },
    "Daily Octordle": {
      "day": date(2022, 1, 24),
      "heading": 'O',
      "json": 'octordle',
      "useBoard": True,
      "ignore": 0,
      "max": 16,
      "turns": []
    },
    "Daily Sequence Octordle": {
      "day": date(2022, 1, 24),
      "heading": 'SO',
      "json": 'sequenceOctordle',
      "useBoard": True,
      "max": 16,
      "turns": [],
      "ignore": 570,
    },
    "nerdlegame": {
      "day": date(2022, 1, 19),
      "heading": 'N',
      "json": 'nerdle',
      "useBoard": False,
      "ignore": 0,
      "turns": []
    },
    "Obsessie": {
      "day": date(2025, 7, 15),
      "heading": '🌀',
      "json": 'obsessie',
      "useBoard": False,
      "ignore": 0,
      "turns": []
    }
}