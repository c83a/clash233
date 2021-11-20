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
      if re.match(ip_pattern,server.group(1)):
        try:
          country=get_location(server.group(1))
        except:
          country='ZZ'
      else:
        a = os.popen("nslookup " + server.group(1)+ '|grep -v "^$"')
        output=a.readlines()
        try:
            country=get_location(re.findall(ip_pattern,output[-1])[0])
        except:
            country='ZZ'
      g.write(line.strip() + ',' + country + "\n")
      break

