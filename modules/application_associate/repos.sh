#!/bin/sh

case "$1" in
    "install" )
        sudo python setup.py install
        ;;
    "clean" )
        sudo rm -rf build gdesktopapp.egg-info dist
        ;;
    * ) 
        echo "Help"
        echo "./repos.sh install         => install"
        echo "./repos.sh clean           => clean"
        ;;
    esac
