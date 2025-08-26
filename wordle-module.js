// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: deep-purple; icon-glyph: table;
// share-sheet-inputs: plain-text;
const Logger = importModule("Logger.js");
const logger = new Logger();

const WORDLE = 'Wordle';
const BRONZE = 1;
const SILVER = BRONZE * 100;
const GOLD = SILVER * 100;
const MS = 86400000;
const MEDALS = [GOLD, SILVER, BRONZE];
const MAX = 100;
const MEDAL_SYMBOLS = {
  [GOLD]: '🥇',
  [SILVER]: '🥈',
  [BRONZE]: '🥉'
};
const MEDAL_NAMES = {
  [GOLD]: 'G',
  [SILVER]: 'S',
  [BRONZE]: 'B'
};


const symbols = {
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
};

module.exports.MEDALS = MEDALS;

module.exports.getMedalSymbol = (m) => MEDAL_SYMBOLS[m];

module.exports.reverseSymbols = Object.keys(symbols).reduce((r, k) => { r[symbols[k]] = k; return r; }, {});

module.exports.analyseWordle = (messages, offset) => {

  const getGameNo = (start) => {
    const today = new Date();
    const day = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()) - offset * MS;
    const game = Math.ceil((day - start) / MS);
    logger.log(game);
    return game;
  };

  const games = {
    [WORDLE]: {
      day: getGameNo(Date.UTC(2021, 5, 19)),
      heading: 'W',
      json: 'wordle',
      useBoard: false,
      ignore: 0,
      turns: []
    },
    "Wortel": {
      day: getGameNo(Date.UTC(2022, 0, 31)),
      heading: '🥕',
      json: 'wortel',
      useBoard: false,
      ignore: 0,
      turns: []
    },
    "Daily Quordle": {
      day: getGameNo(Date.UTC(2022, 0, 24)),
      heading: 'Q',
      json: 'quordle',
      useBoard: true,
      ignore: 0,
      max: 10,
      turns: []
    },
    "Daily Sequence Quordle": {
      day: getGameNo(Date.UTC(2022, 0, 24)),
      heading: 'SQ',
      json: 'sequenceQuordle',
      useBoard: true,
      ignore: 570,
      max: 10,
      turns: []
    },
    "Daily Octordle": {
      day: getGameNo(Date.UTC(2022, 0, 24)),
      heading: 'O',
      json: 'octordle',
      useBoard: true,
      ignore: 0,
      max: 14,
      turns: []
    },
    "Daily Sequence Octordle": {
      day: getGameNo(Date.UTC(2022, 0, 24)),
      heading: 'SO',
      json: 'sequenceOctordle',
      useBoard: true,
      max: 16,
      turns: [],
      ignore: 570,
    },
    "nerdlegame": {
      day: getGameNo(Date.UTC(2022, 0, 19)),
      heading: 'N',
      json: 'nerdle',
      useBoard: false,
      ignore: 0,
      turns: []
    },
    "xDaaglikse Kwartel": {
      day: getGameNo(Date.UTC(2022, 0, 24)),
      heading: 'K',
      json: 'kwartel',
      useBoard: true,
      ignore: 9999,
      max: 10,
      turns: []
    },
      "Obsessie": {
      day: getGameNo(Date.UTC(2025, 6, 15)),
      heading: '🌀',
      json: 'obsessie',
      useBoard: false,
      ignore: 0,
      turns: []
    }
  };

  const calcScore = (board, max) => {
    let score = 0;
    for (let s of Object.keys(symbols)) {
      const count = (board.match(new RegExp(s, "g")) || []).length;
      score += count * Math.min(max, symbols[s]);
    }
    return score;
  }
  const cleanedMessages = messages.replaceAll(' 🎉', '').replaceAll('🙂 ', '').replaceAll('🥕 ', '').replaceAll('🌀 ', '');
 
  const re = /\[\d+\/\d+\/\d+, \d+:\d+:\d+\] ([A-Za-z é&]+): \s*([ ([A-Za-z ]+) #?([0-9,]+)( (\d)\/(\d))?([^\[]+)/gim;
  const matches = [...cleanedMessages.matchAll(re)];

  const players = matches
    .reduce((rv, x) => {
      let game = x[2];
      let name = x[1].split(' ')[0];
      let day = parseInt(x[3].replaceAll(',', ''));
      let turns = parseInt(x[4]);
      let board = x[7];
      let g = games[game];
      if (g && g.day === day) {
        logger.log(x);
        turns = Number.isNaN(turns) ? MAX : turns;
        turns = g.useBoard ? calcScore(board, g.max) : turns;
        const p = rv[name] ?? { games: {} };
        if (!Object.hasOwn(p.games, game)) {
          p.games[game] = { turns };
          g.turns.push(turns);
        }
        rv[name] = p;
      }
      return rv;
    }, {});

  // Work out medals
  for (let n of Object.keys(games)) {
    const g = games[n];
    g.medals = {};
    let medalCount = 0;
    let medalIndex = 0;
    let lastTurn = 0;
    for (let t of g.turns.sort((a, b) => a - b)) {
      if (t > lastTurn) {
        if (medalIndex >= 3) break;
        g.medals[t] = MEDALS[medalIndex];
      }
      medalIndex++;
      lastTurn = t;
    }
  }

  const names = Object.keys(players);
  const payload = [];
  for (let n of names) {
    const obj = { name: n, day: games[WORDLE].day, golds: 0, silvers: 0, bronzes: 0 };
    payload.push(obj);
    const p = players[n];
    p.total = 0;
    for (let gn of Object.keys(p.games)) {
      const medal = games[gn].medals[p.games[gn].turns];
      obj[`${games[gn].json}Turns`] = p.games[gn].turns;
      obj[`${games[gn].json}Medal`] = '';
      if (medal) {
        const ignore = games[gn].day <= games[gn].ignore && games[gn].turns.length !== names.length;
        p.total += ignore ? 0 : medal;
        p.games[gn].medal = medal;
        obj.golds += medal === GOLD ? 1 : 0;
        obj.silvers += medal === SILVER ? 1 : 0;
        obj.bronzes += medal === BRONZE ? 1 : 0;
        obj[`${games[gn].json}Medal`] = MEDAL_NAMES[medal];
      }
      obj.total = p.total;
    }
  }
  let count = 0;
  let total = 0;
  for (let player of payload.sort((a, b) => b.total - a.total)) {
    if (player.total !== total) {
      player.position = count + 1;
    } else {
      player.position = payload[count - 1].position;
    }
    count++
    total = player.total;
  }
  return { names, players, games, payload };
};
