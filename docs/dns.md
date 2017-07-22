# dns

## Ubuntu
```
# install pdns
sudo apt-get install -y pdns-server pdns-backend-mysql

cat << EOS | sudo tee /etc/powerdns/pdns.d/pdns.local.gmysql.conf
launch+=gmysql

gmysql-host=localhost
gmysql-port=3306
gmysql-dbname=pdns
gmysql-user=fabkit
gmysql-password=fabkit
gmysql-dnssec=yes
EOS

sudo service pdns restart
```

```
# stop dnsmasq
sudo lsof -i:53
COMMAND  PID            USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
dnsmasq 1672 libvirt-dnsmasq    5u  IPv4  21345      0t0  UDP 192.168.122.1:domain
dnsmasq 2197          nobody    4u  IPv4  25540      0t0  UDP owner-All-Series:domain
dnsmasq 2197          nobody    5u  IPv4  25541      0t0  TCP owner-All-Series:domain (LISTEN)

sudo sed -i 's/^dns=dnsmasq/#&/' /etc/NetworkManager/NetworkManager.conf

sudo service network-manager restart
sudo service networking restart

sudo killall dnsmasq
```
