#!/bin/bash

create_user()
{
/usr/sbin/useradd -u 2020 STD-MO -g wheel
cat ./STD-MO > /etc/ssh/authorized_keys/STD-MO
}

DP()
{
cp ./recordInfoNew.sh /home/STD-MO/
echo "#Ansible: 2310 by STD-MO-ITS
10 23 * * * /usr/bin/sudo /usr/bin/systemctl poweroff -i > /dev/null 2>&1
#Ansible: recordInfoUp by STD-MO-ITS
20 7 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1
#Ansible: recordInfoUp2 by STD-MO-ITS
00 8 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1" > /var/spool/cron/STD-MO

mkdir /var/opt/iSTD/
cp ./imp_callback.py /var/opt/iSTD/
cp ./config.ini /var/opt/iSTD/
cp ./istd_monitor.py /home/jcdcn-jv-std/
chmod 755 /var/opt/iSTD/imp_callback.py
chmod 755 /home/jcdcn-jv-std/istd_monitor.py
chmod 755 /var/opt/iSTD/config.ini
chown -R jcdcn-jv-std:jcdcn-jv-std /var/opt/iSTD/
chown jcdcn-jv-std:jcdcn-jv-std /home/jcdcn-jv-std/istd_monitor.py
echo "#Ansible: iSTD running
*/2 * * * * /usr/bin/python3.6 /var/opt/iSTD/imp_callback.py > /dev/null 2>&1 &
#Ansible: istd_monitor running
0 */1 * * * /usr/bin/python /home/jcdcn-jv-std/istd_monitor.py > /dev/null 2>&1 &" > /var/spool/cron/jcdcn-jv-std

/usr/bin/timedatectl set-local-rtc 1
hwclock -r
hwclock -w
}

LED()
{
cp ./recordInfoNew.sh /home/STD-MO
echo "#Ansible: 2205 by STD-MO-ITS
05 22 * * * /usr/bin/sudo /usr/bin/systemctl poweroff -i > /dev/null 2>&1
#Ansible: recordInfoUp by STD-MO-ITS
20 7 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1
#Ansible: recordInfoUp2 by STD-MO-ITS
00 8 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1" > /var/spool/cron/STD-MO

mkdir /var/opt/iSTD/
cp ./imp_callback.py /var/opt/iSTD/
cp ./config.ini /var/opt/iSTD/
cp ./istd_monitor.py /home/jcdcn-jv-std/
chmod 755 /var/opt/iSTD/imp_callback.py
chmod 755 /home/jcdcn-jv-std/istd_monitor.py
chmod 755 /var/opt/iSTD/config.ini
chown -R jcdcn-jv-std:jcdcn-jv-std /var/opt/iSTD/
chown jcdcn-jv-std:jcdcn-jv-std /home/jcdcn-jv-std/istd_monitor.py

echo "#Ansible: iSTD running
*/2 * * * * /usr/bin/python3.6 /var/opt/iSTD/imp_callback.py > /dev/null 2>&1 &
#Ansible: istd_monitor running
0 */1 * * * /usr/bin/python /home/jcdcn-jv-std/istd_monitor.py > /dev/null 2>&1 &" > /var/spool/cron/jcdcn-jv-std

/usr/bin/timedatectl set-local-rtc 1
hwclock -r
hwclock -w
}

SPE()
{
cp ./recordInfoNew.sh /home/STD-MO
echo "#Ansible: recordInfoUp by STD-MO-ITS
20 7 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1
#Ansible: recordInfoUp2 by STD-MO-ITS
00 8 * * * /usr/bin/sudo /usr/bin/sh /home/STD-MO/recordInfoNew.sh >/dev/null 2>&1" > /var/spool/cron/STD-MO

cp ./istd_monitor.py /home/jcdcn-jv-std/
chmod 755 /home/jcdcn-jv-std/istd_monitor.py
chown jcdcn-jv-std:jcdcn-jv-std /home/jcdcn-jv-std/istd_monitor.py

echo "#Ansible: istd_monitor running
0 */1 * * * /usr/bin/python /home/jcdcn-jv-std/istd_monitor.py > /dev/null 2>&1 &" > /var/spool/cron/jcdcn-jv-std

/usr/bin/timedatectl set-local-rtc 1
hwclock -r
hwclock -w
}

create_user
$1

