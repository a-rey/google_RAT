#!/usr/bin/env python3
import base64
import logging
import requests
import argparse


if __name__ == '__main__':
  # parse user arguments
  parser = argparse.ArgumentParser()
  parser.add_argument('srv', help='google apps server URL', type=str)
  parser.add_argument('-k', dest='master_key', help='master key for server', type=str)
  parser.add_argument('-l', dest='logging_level', default='INFO', help='logging level for output', type=str)
  args = parser.parse_args()
  # setup logger
  logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%d %b %Y %H:%M:%S', level=args.logging_level)
  logging.SUCCESS = logging.CRITICAL + 1
  logging.addLevelName(logging.SUCCESS, '\033[0m\033[1;32mOK\033[0m')
  logging.addLevelName(logging.ERROR,   '\033[0m\033[1;31mERROR\033[0m')
  logging.addLevelName(logging.WARNING, '\033[0m\033[1;33mWARN\033[0m')
  logging.addLevelName(logging.INFO,    '\033[0m\033[1;36mINFO\033[0m')
  logging.success = lambda msg, *args: logging.getLogger(__name__)._log(logging.SUCCESS, msg, args)
  logging.info('starting tests ...')
  # ---------------------------------------------------------------------------
  # create a new client on the server
  # ---------------------------------------------------------------------------
  r = requests.get(args.srv,{'i':base64.b64encode('TEST-USER|TEST-HOST'.encode('UTF-8'))})
  uuid = r.content.decode('UTF-8')
  assert(uuid)
  logging.info('new client UUID: {0}'.format(uuid))
  # ---------------------------------------------------------------------------
  # check that the client exists on the server
  # ---------------------------------------------------------------------------
  r = requests.get(args.srv, params={'k':args.master_key,'u':uuid,'d':'info'})
  old_info = r.content.decode('UTF-8').split('|')
  logging.info('client info before:')
  for x in old_info:
    print(x)
  assert(old_info[0] == uuid)
  assert(old_info[3] == 'IDLE')
  # ---------------------------------------------------------------------------
  # check that client has no data before we add some
  # ---------------------------------------------------------------------------
  r = requests.get(args.srv, params={'u': uuid})
  assert(not r.content.decode('UTF-8'))
  # ---------------------------------------------------------------------------
  # send encoded/chunked data to server for client to download
  # ---------------------------------------------------------------------------
  msg = 'this is a test'
  for word in msg.split(' '):
    chunk = base64.b64encode(word.encode('UTF-8')).decode('UTF-8')
    r = requests.post(args.srv, data={'k':args.master_key,'u': uuid,'d':chunk})
    logging.info('[upload] master encoded chunk: {0}'.format(chunk))
  # ---------------------------------------------------------------------------
  # signal to server that we are done uploading data
  # ---------------------------------------------------------------------------
  r = requests.post(args.srv, data={'k':args.master_key,'u':uuid,'d':''})
  # ---------------------------------------------------------------------------
  # pull encoded/chunked data from server for client
  # ---------------------------------------------------------------------------
  buf = []
  while True:
    r = requests.get(args.srv, params={'u':uuid})
    if not r.content:
      break
    buf.append(base64.b64decode(r.content).decode('UTF-8'))
    logging.info('[download] client decoded chunk: {0}'.format(buf[-1]))
  assert(msg == ' '.join(buf))
  # ---------------------------------------------------------------------------
  # check that client update time has changed
  # ---------------------------------------------------------------------------
  r = requests.get(args.srv, params={'k':args.master_key,'u':uuid,'d':'info'})
  new_info = r.content.decode('UTF-8').split('|')
  logging.info('client info after:')
  for x in new_info:
    print(x)
  assert(new_info[0] == old_info[0])
  assert(new_info[1] != old_info[1])
  assert(new_info[3] == 'UPLOADING')
  logging.success('DONE - all tests passed')
