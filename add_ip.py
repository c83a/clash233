#!/usr/bin/python3
import os
import re
import geoip2.database
reader = geoip2.database.Reader('Country.mmdb')
ip_pattern='\d+.\d+.\d+.\d'
def get_location(ip):
  response = reader.country(ip)
  return response.country.iso_code
with open('speed.yaml') as f,open('speed_c.yaml','w') as g:
  for line in f:
    for server in re.finditer('"server":"([^"]*)"',line):
      ip_domain=server.group(1)
      if re.match(ip_pattern,ip_domain):
        ip=ip_domain
      else:
        domain=ip_domain
        a = os.popen("nslookup " + domain+ '|grep -v "^$"')
        output=a.readlines()
        ip=re.findall(ip_pattern,output[-1])[0]
      try:
        country=get_location(ip)
      except:
        country='ZZ'
      g.write(line.strip() + ',' + ','.join((ip,country)) + "\n")
      break

