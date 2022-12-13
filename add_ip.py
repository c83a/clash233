#!/usr/bin/python3
import re
from socket import gethostbyname as nslookup
from socket import getaddrinfo as nslookup46
import geoip2.database
import sys
reader = geoip2.database.Reader('Country.mmdb')
ip_pattern='''^\d+\.\d+\.\d+\.\d+$|^[0-9a-fA-F:]+$'''
dns_cache={}
code_cache={}
def get_location(ip):
  response = reader.country(ip)
  return response.country.iso_code
def get_filename():
  return sys.argv[1]
next(f)
print("proxies:")
for line in sys.stdin:
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
          ip=nslookup46(domain,80)[0][4][0]
        except:
          pass
        if not ip:
          try:
            ip=nslookup(domain)
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
