#!/bin/sh

set -x
### Custom user script
### Called after internal WAN up/down action
### $1 - WAN action (up/down)
### $2 - WAN interface name (e.g. eth3 or ppp0)
### $3 - WAN IPv4 address
logger  "运行后 WAN 状态:" "WAN 状态:【$1】, WAN 接口:【$2】, WAN IP:【$3】"
link=$1
wan_if=$2

bridge_ipv6(){
if [ "0$link" == "0down" ] && [ "0" != "0$wan_if" ]; then
  logger "del $wan_if from bridge br0" && brctl delif br0 $wan_if
  logger "flush BROUTING table" && ebtables -t broute -F BROUTING
  ipv6=`ifconfig br0 | grep inet6 | grep Global | awk '{print $3}'`
  [ 0 == $? ] && logger "del ipv6 address $ipv6 on br0" && ifconfig br0 del $ipv6
  logger "flush all ipv6 route" && ip -6 route flush all
fi
[ "0$link" != "0up" ] && return
[ "0" == "0$wan_if" ] && return
while true;do
  dhcp6c_pid=`pidof dhcp6c`
  [ 0 != $? ] && break
  ipv6=`ifconfig $wan_if | grep inet6 | grep Global | awk '{print $3}'`
#  logger "WAN IPv6: $ipv6"
  if [ "0" == "0$ipv6" ]; then
    sleep 5
  else
    logger "WAN IPv6: $ipv6"
    ifconfig br0 add $ipv6
    ipv6_gw=`ip -6 route | grep "default via" | head -n 1 | awk '{print $3}'`
    ebtables -t broute --list | grep "\-p ! IPv6 -i $wan_if -j DROP"
    [ 0 == $? ] || ebtables -t broute -A BROUTING -p ! IPv6 -i $wan_if -j DROP
    brctl addif br0 $wan_if
    ip -6 route change default via $ipv6_gw dev br0
    break
  fi
done
}

bridge_ipv6
#    sleep 30
[ "0up" == "0$link" ] && /etc/storage/crontabs_script.sh up &
logger  "#####WAN_SCRIPT_END#####"
