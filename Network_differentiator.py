import wpactrl 
import sys
import os 
import re
import time
import requests
from bs4 import BeautifulSoup


ctrl_interface='/var/run/wpa_supplicant/wlan1'

wpactr=wpactrl.WPACtrl(ctrl_interface)
networks=wpactr.scanresults()

open=[]
open_ssid=[]
open_bssid=[]
wpa2=[]
wpa2_ssid=[]
wpa2_bssid=[]
wpa=[]
wpa_ssid=[]
wpa_bssid=[]
portal_networks=[]
wps=[]
wps_ssid=[]
wps_bssid=[]


def main():

	for network in networks:
		if  checkflags(network)=="[ESS]":
			open.append(network)
			open_bssid.append(get_info(network)[0])
			open_ssid.append(get_info(network)[1])
		if  checkflags(network)=='[WPA2-PSK-CCMP][ESS]':
			wpa2.append(network)
			wpa2_bssid.append(get_info(network)[0])
			wpa2_ssid.append(get_info(network)[1])
		if checkflags(network)=='[WPA-PSK-TKIP][ESS]':
			wpa.append(network)
			wpa_bssid.append(get_info(network)[0])
			wpa_ssid.append(get_info(network)[1])
		if "[WPS]" in checkflags(network):
			wps.append(network)
			wps_bssid.append(get_info(network)[0])
			wps_ssid.append(get_info(network)[1])

	for open_network in open_bssid:
		print open_ssid
		if detectportal(open_network):
			print "Captive Portal detected."
			portal_networks.append(open_network)
	#for mac in wps_bssid:
		#brute_wps(mac)	


def RunCommand(command):
	retry=0
	while 1:
		if retry:
			print "Retry count: "+str(retry)+" for command "+command
		try:
			ret=wpactr.request(command).strip()
			print ret 

			if(ret!="FAIL"): 
				return ret
		except wpactrl.error,error:
			print "Error", error
			print "Retrying command "+command

		retry+=1

		if(retry>=10):
			print "Maximum retries done for the command "+command
			sys.exit(0)
		time.sleep(4)
				

def checkflags(network):
	
	flags=re.findall(r"flags=(.*)",network)
	return flags[0]

def get_info(network):
	
	a=bssid,ssid=re.findall(r"ssid=(.*)",network)
	return a

def detectportal(open_network):
	
	print "Connecting to "+ open_network
	RunCommand("REMOVE_NETWORK all")
	networkid=RunCommand("ADD_NETWORK")
	RunCommand("SET_NETWORK "+networkid+" bssid "+ open_network)
	RunCommand("SET_NETWORK "+networkid+" key_mgmt"+ " NONE")
	RunCommand("ENABLE_NETWORK "+networkid)
	RunCommand("SELECT_NETWORK "+networkid)
	time.sleep(3)

	try:
		r=requests.get("http://clients3.google.com")
		if r.status_code==302:
			return True
		else:
			return False
	except:
		return False 		



def brute_wps(mac):
	for i in range(12340000,99999999):
		print RunCommand("WPS_REG "+mac+" "+str(i))


if __name__ == '__main__':
	main()

	

#https://wpsfinder.com/wps-pin-generator	