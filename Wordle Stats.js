// Variables used by Scriptable.
// These must be at the very top of the file. Do not edit.
// always-run-in-app: true; icon-color: deep-purple;
// icon-glyph: table; share-sheet-inputs: plain-text;
const Logger = importModule("Logger.js");
const { analyseWordle, getMedalSymbol, MEDALS, reverseSymbols } = importModule("wordle-module.js");
const logger = new Logger();

const uploadToExcel = async (data) => {
  const url = 'https://prod-19.northeurope.logic.azure.com:443/workflows/65f2b4997aa647b085c3c8d1c2d5615c/triggers/manual/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=hHVEPsNVSLNEpDsSrONfOF_yPiyawvyzQhg_VXM-meI';
  const req = new Request(url);
  req.method = "POST";
  req.headers = {
    "Content-Type": "application/json"
  };
  req.body = JSON.stringify(allResults);
  await req.loadJSON();
};

const writeToFile = (data) => {
  const fm = FileManager.iCloud();
  const filePath = fm.joinPath(fm.bookmarkedPath('Pythonista 3'), 'wordle.json');
  fm.writeString(filePath, JSON.stringify(data));
};

let offset = 0;
const messages = args.shortcutParameter;

try {
  let hasResults = true;
  let allResults = [];
  while (hasResults) {
    const { payload } = analyseWordle(messages, offset);
    // logger.log(JSON.stringify(payload));
    allResults = [...allResults, ...payload];
    hasResults = offset === 0 || payload.length > 0;
    offset++;
  }
  writeToFile(allResults);
} catch (error) {
  logger.error(error);
}
