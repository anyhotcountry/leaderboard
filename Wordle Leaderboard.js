// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// icon-color: deep-purple; icon-glyph: table;
// share-sheet-inputs: plain-text;
const Logger = importModule("Logger.js");
const { analyseWordle, getMedalSymbol, MEDALS, reverseSymbols } = importModule("wordle-module.js");
const logger = new Logger();

const offset = parseInt(args.plainTexts[0]);
const messages = args.shortcutParameter;

try {
  const { names, players, games, payload } = analyseWordle(messages, offset);
  logger.log(JSON.stringify(payload));
  
  const sorted = names.sort((a, b) => players[b].total - players[a].total);
  let table = ['<table class="table table-bordered table-sm table-striped border-primary">', '<tr>', `<th scope="col">#${games['Wordle'].day}</th>`];
  const gs = Object.keys(games).filter(g => games[g].turns.length > 0);
  table = [...table, ...gs.map(g => `<th scope="col">${games[g].heading}</th>`)];
  table.push('<th scope="col">Total</th></tr>');
  
  for (let name of sorted) {
    const p = players[name];
    table.push(`<tr><td>${name}</td>`);
    for (let g of gs) {
      const turns = p.games[g]?.turns ?? -1;
      const medal = p.games[g]?.medal ?? -1;
      const text = `<td>${reverseSymbols[turns] ?? turns} ${getMedalSymbol(medal) ?? ''}</td>`;
      table.push(text);
    }
  
    let total = p.total;
    let text = '<td>';
    for (let m of MEDALS) {
      for (; total >= m; total -= m) {
        text += `${getMedalSymbol(m)} `;
      }
    }
    text += '</td></tr>';
    table.push(text);
  }
  table.push('</table>');
  
  const output = {
    html: table.join(''),
    players: sorted.length,
    games: gs.length
  };
  
  Script.setShortcutOutput(JSON.stringify(output));
} catch (error) {
  logger.error(error);
}
