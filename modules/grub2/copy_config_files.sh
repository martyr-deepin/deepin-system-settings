#! /bin/bash
#This file is used for testing only!!!

if [ "$1" == "install" ];then
    cp -v data/com.deepin.grub2.service /usr/share/dbus-1/system-services
    cp -v data/com.deepin.grub2.conf /etc/dbus-1/system.d
    cp -v data/com.deepin.grub2.policy /usr/share/polkit-1/actions
fi

if [ "$1" == "uninstall" ];then
    rm -vf /usr/share/dbus-1/system-services/com.deepin.grub2.service
    rm -vf /etc/dbus-1/system.d/com.deepin.grub2.conf
    rm -vf /usr/share/polkit-1/actions/com.deepin.grub2.policy
fi
