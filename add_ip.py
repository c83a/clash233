#!/usr/bin/python3
import re
import asyncio
import geoip2.database
import sys
reader = geoip2.database.Reader('Country.mmdb')
ip_pattern='''^\d+\.\d+\.\d+\.\d+$|^[0-9a-fA-F:]+$'''
dns_cache={}
code_cache={}
def get_location(ip):
  response = reader.country(ip)
  return response.country.iso_code
def get_file():
  try:
    f=open(sys.argv[1])
  except:
    f=sys.stdin
  yield from f
async def print_item(gen):
  for line in gen:
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
  nslookup46=asyncio.get_event_loop().getaddrinfo
  gen=get_file()  
  task_list=[asyncio.create_task(print_item(gen)) for i in range(2)]
  next(gen)
  print('proxies:')
  await asyncio.gather(*task_list,return_exceptions=true)
asyncio.run(main())
