#!/bin/sh
cp com.deepin.passwdservice.service /usr/share/dbus-1/system-services/ 
echo "Copy .service file to /usr/share/dbus-1/system-services/"

cp com.deepin.passwdservice.policy /usr/share/polkit-1/actions/
echo "Copy .policy file to /usr/share/polkit-1/actions/"

cp com.deepin.passwdservice.conf /etc/dbus-1/system.d/
echo "Copy .conf file to /etc/dbus-1/system.d/"

cp passwdservice.py /usr/lib/
echo "cp passwdservice.py"
