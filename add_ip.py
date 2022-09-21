#!/usr/bin/python3
import re
from socket import gethostbyname as nslookup
import geoip2.database
reader = geoip2.database.Reader('Country.mmdb')
ip_pattern='\d+\.\d+\.\d+\.\d+'
dns_cache={}
code_cache={}
def get_location(ip):
  response = reader.country(ip)
  return response.country.iso_code
with open('speed_short.yaml') as f,open('speed.yaml','w') as g:
  next(f)
  g.write("proxies:\n")
  for line in f:
    for server in re.finditer('server: ([^,]*)',line):
      ip_domain=server.group(1)
      if re.match(ip_pattern,ip_domain):
        ip=ip_domain
      elif ip_domain in dns_cache:
        ip=dns_cache[ip_domain]
      else:
        domain=ip_domain
        try:
          ip=nslookup(domain)
        except:
          ip=None
        dns_cache[domain]=ip
      if ip in code_cache:
          code=code_cache[ip]
      else:
        try:
          code=get_location(ip)
        except:
          code='ZZ'
        code_cache[ip]=code
      g.write("#".join(map(str,(line.strip(), code, ip, "\n"))))
      break

