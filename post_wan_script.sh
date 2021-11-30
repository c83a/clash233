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
change_route6(){
src="$1"
dst="$2"
[ "0" == "0$src" ] || [ "0" == "0$dst" ] && return
ip -6 route list  | grep $src | awk '!a[$0]++' | sed -E "s/$src/$dst/g;s/expires .*//g" | awk '{print "ip -6 route change",$0}' | sh
}
bridge_ipv6(){
if [ "0$link" == "0down" ] && [ "0" != "0$wan_if" ]; then
  logger "change route6 from br0 to $wan_if" && change_route6 "br0" "$wan_if"
  ipv6=`ifconfig br0 | grep inet6 | grep Global | awk '{print $3}'`
  [ 0 == $? ] && logger "del ipv6 address $ipv6 on br0" && ifconfig br0 del $ipv6
  logger "del $wan_if from bridge br0" && brctl delif br0 $wan_if
  logger "flush BROUTING table" && ebtables -t broute -F BROUTING
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
    ebtables -t broute --list | grep "\-p ! IPv6 -i $wan_if -j DROP"
    [ 0 == $? ] || ebtables -t broute -A BROUTING -p ! IPv6 -i $wan_if -j DROP
    brctl addif br0 $wan_if
    change_route6 $wan_if br0
    break
  fi
done
}

bridge_ipv6
#    sleep 30
[ "0up" == "0$link" ] && /etc/storage/crontabs_script.sh up &
logger  "#####WAN_SCRIPT_END#####"
