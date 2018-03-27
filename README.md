# google_RAT
A RAT (Remote Access Tool) for Windows systems using google apps script as the middle man

**NOTE:** Current limit to data upload and download is 8.5 MB. This is due to the [limits of google sheets](https://gsuitetips.com/tips/sheets/google-spreadsheet-limitations/).

### TODO
* add extra encryption on top of b64
* test chunked upload of files
* add code for chunked file downloads
* add timestamps to google drive output
* implement data reset from `script.py` for a stale client
* figure out how to send over powershell STDERR as well as STDOUT in result

### Setup
* Create a fake Google account
* Create a spreadsheet in the fake account's Google drive
* Make it public:
  * `File` > `Share...` > Give it a random name > `Get sharable link`
* Paste the link into the `SPREADSHEET_URL` variable in `server.gs`
  * remove the `?usp=sharing` at the end as well. URL should end in `/edit`
* Visit [Google Scripts](https://www.google.com/script/start/) and paste the code in `server.gs`
* Publish the server:
  * Save and name the project something
  * `Publish` > `Deploy as web app`
    * Fill in the blank with something
    * Make sure the app is executed as `Me`
    * Make sure `Anyone, even anonymous` can access the app
  * `Review Permissions` > Select your fake account > `Advanced` > `Go to Untitled project (unsafe)` > enter 'Continue' > `Allow`
  * Copy the URL and paste it into `$srv` of `script.ps1`

## Fun Test Commands:
* `(new-object -com SAPI.SpVoice).speak('self destruct in 9 8 7 6 5 4 3 2 1 boom')`
* `$e=new-object -com internetexplorer.application; $e.visible=$true; $e.navigate('https://www.youtube.com/watch?v=dQw4w9WgXcQ');`
