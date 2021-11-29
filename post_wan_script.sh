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
while true;do
  [ "0$link" != "0up" ] && break
  [ "0" == "0$wan_if" ] && break
  dhcp6c_pid=`pidof dhcp6c`
  [ 0 != $? ] && break
  ipv6=`ifconfig $wan_if | grep inet6 | grep Global | awk '{print $3}'`
  if [ 0 == $? ]; then
    ifconfig br0 add $ipv6
    ipv6_gw=`ip -6 route | grep "default via" | head -n 1 | awk '{print $3}'`
    ebtables -t broute --list | grep "\-p ! IPv6 -i $wan_if -j DROP"
    [ 0 == $? ] || ebtables -t broute -A BROUTING -p ! IPv6 -i $wan_if -j DROP
    brctl addif br0 $wan_if
    ip -6 route change default via $ipv6_gw dev br0
    break
  else
    sleep 5
  fi
done
}
brctl delif br0 $wan_if
sleep 5
bridge_ipv6
#    sleep 30
[ "0up" == "0$link" ] && /etc/storage/crontabs_script.sh up &
logger  "#####WAN_SCRIPT_END#####"
