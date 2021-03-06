import urllib.request, json
import RPi.GPIO as GPIO
import subprocess
import threading
import logging
import os
import sys
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)
from urllib.request import (urlopen, HTTPError, URLError)
from RPLCD.gpio import CharLCD
from datetime import datetime
from RPLCD import cursor
from queue import Queue
from time import sleep

GPIO.setwarnings(False)
lcd = CharLCD(pin_rs=22, pin_rw=None, pin_e=17, pins_data=[25, 24, 23, 18], numbering_mode=GPIO.BCM)
BITCOIN_API_URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin/'
token = 'YOUR TELEGRAM TOKEN HERE'
cloud_url = 'YOUR WEBPAGE TO MONITOR HERE'
q = Queue()
logger = logging.getLogger('msglog')
logger2 = logging.getLogger('newuserlog')
logger.setLevel(logging.INFO)
logger2.setLevel(logging.INFO)
handler = logging.FileHandler('/home/pi/telegram_message_bot.log')
handler.setLevel(logging.INFO)
handler2 = logging.FileHandler('/home/pi/telegram_message_bot.userlog')
handler2.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)
handler2.setFormatter(formatter)
logger.addHandler(handler)
logger2.addHandler(handler2)

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
		return 'up'
	else:
		return 'do'

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
		return 'up'
	else:
		return 'do'

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
		return 'up'
	else:
		return 'do'

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
		return 'up'
	else:
		return 'do'

def get_latest_bitcoin_price():
	with urllib.request.urlopen('https://blockchain.info/ticker') as url:
		data = json.loads(url.read().decode())
		return str(data['EUR']['last'])

def get_last_message():
	p1 = subprocess.Popen(['grep', '-a', 'message from', '/home/pi/telegram_message_bot.log'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['tail', '-n1'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['sed', 's/^.\{39\}//'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	output,err = p3.communicate()
	return output.decode('utf-8')

def get_secondlast_message():
	p1 = subprocess.Popen(['grep', '-a', 'message from', '/home/pi/telegram_message_bot.log'], stdout=subprocess.PIPE)
	p2 = subprocess.Popen(['tail', '-n2'], stdin=p1.stdout, stdout=subprocess.PIPE)
	p1.stdout.close()
	p3 = subprocess.Popen(['head', '-n1'], stdin=p2.stdout, stdout=subprocess.PIPE)
	p2.stdout.close()
	p4 = subprocess.Popen(['sed', 's/^.\{39\}//'], stdin=p3.stdout, stdout=subprocess.PIPE)
	p3.stdout.close()
	output,err = p4.communicate()
	return output.decode('utf-8')

def cloud_status():
	try:
		page = urlopen(cloud_url, timeout=3)
		return 'up'
	except HTTPError:
		return 'do'
	except URLError:
		return 'do'

def start(bot, update):
	update.message.reply_text('send a message (20-40 chars max)')
	user = update.message.from_user
	logger2.info(user)
	logger2.info('above user came online')

def remove_non_ascii(text):
	return ''.join(i for i in text if ord(i)<128)

def msgh(bot, update):
	string = update.message.text
	string = remove_non_ascii(string)
	user = update.message.from_user
	if string == 'temp':
		logger2.info(user)
		logger2.info('message from ' + user.first_name + ': '  + string)
		try:
			cputemp = mesaure_temp()
			update.message.reply_text('Temperature: ' + cputemp + " C")
		except:
			logger2.info('requesting temp failed')
	elif string == 'btc':
		logger2.info(user)
		logger2.info('message from ' + user.first_name + ': '  + string)
		try:
			btc_price = get_latest_bitcoin_price()
			update.message.reply_text('BTC: ' + btc_price + ' EUR')
		except:
			logger2.info('requesting btc failed')
	else:
		queuestring = user.first_name + ': ' + string
		logger.info(user)
		logger.info('message from ' + user.first_name + ': '  + string)
		q.put(queuestring)
		try:
			update.message.reply_text('Got your message')
		except:
			logger2.info('whoops, getting message from telegram user failed..')

def mesaure_temp():
	temp = os.popen('vcgencmd measure_temp').readline()
	temp = temp.replace('temp=','')
	return temp[0:4]

def worker(lcd, q):
	tele_string = get_last_message()
	tele_string2 = get_secondlast_message()
	while True:
		try:
			if q.empty() == False:
				tele_string2 = tele_string
				tele_string = q.get()
			lcd.clear()
			lcd.write_string(tele_string)
			with cursor(lcd, 2, 0):
				lcd.write_string(tele_string2)
			sleep(1)
			for x in range(0, 7):
				if q.empty() == False:
					tele_string2 = tele_string
					tele_string = q.get()
					lcd.clear()
					lcd.write_string(tele_string)
					with cursor(lcd, 2, 0):
						lcd.write_string(tele_string2)
				sleep(1)
			btc_price = get_latest_bitcoin_price()
			cputemp = mesaure_temp()
			ns1 = get_node1_status()
			ns2 = get_node2_status()
			ns3 = get_node3_status()
			ns7 = get_node7_status()
			cloudstatus = cloud_status()
			statusstring = 'N1' + ns1 + ' N2' + ns2 + ' N3' + ns3 + ' N7' + ns7
			print(statusstring)
			for x in range(0, 13):
				lcd.clear()
				lcd.write_string(datetime.now().strftime('%b %d  %H:%M:%S'))
				with cursor(lcd, 1, 0):
					lcd.write_string('BTC ' + btc_price + ' EUR')
				with cursor(lcd, 2, 0):
					lcd.write_string('CPU ' + cputemp + ' C ' + 'Cloud ' + cloudstatus)
				with cursor(lcd, 3, 0):
					lcd.write_string(statusstring)
				sleep(1)
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()

logger2.info('Starting up..')
t = threading.Thread(target=worker, args=[lcd, q])
t.daemon = True
t.start()

updater = Updater(token)
dispatcher = updater.dispatcher

start_handler = CommandHandler('Start', start)
msg_handler = MessageHandler(Filters.text, msgh)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(msg_handler)

updater.start_polling()
updater.idle()

GPIO.cleanup()
sys.exit()
