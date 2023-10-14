#!/usr/bin/python3
import re
import asyncio
import contextvars
import concurrent.futures
import sys
ip_pattern='''^\d+\.\d+\.\d+\.\d+$|^[0-9a-fA-F:]+$'''
dns_cache={}
code_cache={}
loop_var = contextvars.ContextVar('loop')
nslookup46_var = contextvars.ContextVar('nslookup46')
try:
  import maxminddb
  reader = maxminddb.open_database('Country.mmdb',mode=maxminddb.MODE_MEMORY)
except:
  reader = None
  get_location=lambda x: 'ZZ'
else:
  def get_location(ip):
    response = reader.get(ip)
    return response['country']['iso_code']
def get_file():
  try:
    with open(sys.argv[1]) as f:
      pass
  except:
    f=sys.stdin
  if f.closed:
    with open(sys.argv[1]) as f:
      yield from f
  else:
    yield from f
async def a_read():
  loop=loop_var.get()
  gen=get_file()
  end=EOFError()
  with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
    while True:
        r = await loop.run_in_executor(pool, next, gen, end)
        if r is end: break
        yield r
async def get_code_ip(ip_domain, nslookup46):
        if re.match(ip_pattern,ip_domain):
          ip=ip_domain
        elif ip_domain in dns_cache:
          ip=dns_cache[ip_domain]
        else:
          domain=ip_domain
          ip=None
          try:
            ip=(await asyncio.wait_for(nslookup46(domain,80),timeout=10.0))[0][4][0]
          except:
            pass
          dns_cache[domain]=ip
        if ip in code_cache:
            code=code_cache[ip]
        else:
          try:
            code=get_location(ip)
          except:
            code='ZZ'
          code_cache[ip]=code
        return (code, ip)
async def print_item(agen,alock):
  nslookup46=nslookup46_var.get()
  end=EOFError()
  while True:
    async with alock:
        line=await anext(agen, end)
    if line is end:
        break
    else:
      await asyncio.sleep(0)
      for server in re.finditer('server: ([^,]*)',line):
        code, ip = await get_code_ip(server.group(1), nslookup46)
        print("#".join(map(str,(line.rstrip(), code, ip))))
        break
async def main():
  loop=asyncio.get_running_loop()
  loop_var.set(loop)
  nslookup46_var.set(loop.getaddrinfo)
  alock=asyncio.Lock()
  agen=a_read()
  task_list=[asyncio.create_task(print_item(agen,alock)) for i in range(20)]
  print('proxies:')
  await asyncio.gather(*task_list,return_exceptions=True)
if __name__ == '__main__': 
  asyncio.run(main())
