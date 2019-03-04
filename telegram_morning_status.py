from urllib.request import (urlopen, HTTPError, URLError)
import urllib.request, json
import subprocess
import telegram
import schedule
import time

cloud_url = 'WEBPAGE URL HERE'
my_token = 'YOUR TELEGRAM TOKEN HERE'
lumen_id = 'TELEGRAM USER1 ID HERE'
alice_id = 'TELEGRAM USER2 ID HERE'

def cloud_status():
	try:
		page = urlopen(cloud_url, timeout=3)
		return 'Up '
	except HTTPError:
		return 'Down'
	except URLError:
		return 'Down'

def send(msg, chat_id, token=my_token):
	bot = telegram.Bot(token=token)
	bot.sendMessage(chat_id=chat_id, text=msg)

def get_bitcoin_usd():
	with urllib.request.urlopen('https://blockchain.info/ticker') as url:
		data = json.loads(url.read().decode())
		return str(data['USD']['last'])

def get_bitcoin_eur():
	with urllib.request.urlopen('https://blockchain.info/ticker') as url:
		data = json.loads(url.read().decode())
		return str(data['EUR']['last'])

def send_morningstatus():
	btc_usd = get_bitcoin_usd()
	btc_eur = get_bitcoin_eur()
	cloud_status_str = cloud_status()
	nodestring = check_all_nodes()
	btc_usd_string = "Bitcoin: " + btc_usd + " USD"
	btc_eur_string = "Bitcoin: " + btc_eur + " EUR"
	cloud_string = "Cloud Status: " + cloud_status_str
	send(btc_usd_string, lumen_id)
	triple = btc_eur_string + "\n" + cloud_string + "\n" + nodestring
	send(triple, alice_id)

def get_node1_status():
	p1 = subprocess.Popen(['wget', 'https://securenodes2.eu.zensystem.io/nodes/14420/detail', '-q', '-O', '-'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', '-o', '-P', '.{0,0}State.{5,13}'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['cut', '-c', '17-'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	output,err = p3.communicate()
	output = output.decode('utf-8')
	output = output[0:2]
	if output == 'up':
		return True
	else:
		return False

def get_node2_status():
	p1 = subprocess.Popen(['wget', 'https://securenodes4.eu.zensystem.io/nodes/15500/detail', '-q', '-O', '-'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', '-o', '-P', '.{0,0}State.{5,13}'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['cut', '-c', '17-'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	output,err = p3.communicate()
	output = output.decode('utf-8')
	output = output[0:2]
	if output == 'up':
		return True
	else:
		return False

def get_node3_status():
	p1 = subprocess.Popen(['wget', 'https://securenodes2.eu.zensystem.io/nodes/15635/detail', '-q', '-O', '-'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', '-o', '-P', '.{0,0}State.{5,13}'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['cut', '-c', '17-'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	output,err = p3.communicate()
	output = output.decode('utf-8')
	output = output[0:2]
	if output == 'up':
		return True
	else:
		return False

def get_node7_status():
	p1 = subprocess.Popen(['wget', 'https://securenodes2.eu.zensystem.io/nodes/15656/detail', '-q', '-O', '-'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['grep', '-o', '-P', '.{0,0}State.{5,13}'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['cut', '-c', '17-'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	output,err = p3.communicate()
	output = output.decode('utf-8')
	output = output[0:2]
	if output == 'up':
		return True
	else:
		return False

def check_all_nodes():
	s1 = get_node1_status()
	s2 = get_node2_status()
	s3 = get_node3_status()
	s7 = get_node7_status()
	if s1 == True and s2 == True and s3 == True and s7 == True:
		return 'All Nodes Up'
	else:
		rstr = 'Node 1: ' + str(s1) + ' Node 2: ' + str(s2) + ' Node 3: ' + str(s3) + ' Node 7: ' + str(s7)
		return rstr

schedule.every().day.at("08:00").do(send_morningstatus)

while True:
	schedule.run_pending()
	time.sleep(60)
