#!/usr/bin/python3
import re
import asyncio
import concurrent.futures
import maxminddb
import sys
reader = maxminddb.open_database('Country.mmdb',mode=maxminddb.MODE_MEMORY)
ip_pattern='''^\d+\.\d+\.\d+\.\d+$|^[0-9a-fA-F:]+$'''
dns_cache={}
code_cache={}
def get_location(ip):
  response = reader.get(ip)
  return response['country']['iso_code']
def get_file():
  try:
    open(sys.argv[1]) as f:
  except:
    f=sys.stdin
  yield from f
async def a_read(gen):
  loop=asyncio.get_running_loop()
  with concurrent.futures.ThreadPoolExecutor(max_worker=1) as pool:
    try:
      r = await loop.run_in_executor(pool, lambda: next(gen))
      yield r
    except StopIteration:
      pass
async def print_item(agen):
  nslookup46=asyncio.get_running_loop().getaddrinfo
  async for line in agen:
    await asyncio.sleep(0)
    for server in re.finditer('server: ([^,]*)',line):
      ip_domain=server.group(1)
      if re.match(ip_pattern,ip_domain):
        ip=ip_domain
      elif ip_domain in dns_cache:
        ip=dns_cache[ip_domain]
      else:
        domain=ip_domain
        ip=None
        try:
          ip=(await nslookup46(domain,80))[0][4][0]
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
      print("#".join(map(str,(line.strip(), code, ip))))
      break
async def main():
  agen=a_read(get_file())
  task_list=[asyncio.create_task(print_item(agen) for i in range(20)]
  print('proxies:')
  await asyncio.gather(*task_list,return_exceptions=True)
asyncio.run(main())
