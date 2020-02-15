#!/bin/bash
dhclient -r wlan0
ifdown wlan0
ifup wlan0
dhclient -v wlan0