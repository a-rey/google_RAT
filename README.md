# google_RAT
A RAT (Remote Access Tool) for Windows systems using google apps script as the middle man

### TODO
* add extra encryption on top of b64
* get around expected Unicode PS encryption for `-enc` commands

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
