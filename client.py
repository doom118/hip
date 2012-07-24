#! /usr/bin/python2
# encoding: utf-8
# Copyright The multiuser HIP game © Assassin, 2011 - 2012
# This program published under Apache 2.0 license
# See LICENSE.txt for more details
# My EMail: assassin@sonikelf.ru
# My XMPP-conference: bottiks@conference.jabber.ru (closed)
# My Site: bottiks.ucoz.ru (closed)
# Multiuser game HIP - client


import os, sys

from socket import getaddrinfo, AF_INET, SOCK_DGRAM, socket, SOL_TCP

reload(sys).setdefaultencoding('utf8')


core = os.path.abspath(__file__)
coreDir = os.path.split(core)[0]
if coreDir: os.chdir(coreDir)

sys.path.insert(0, 'libs')
debug = True

if debug:
	def send(text):
		connect.sendto(text, adress)
		print '%s > %s' % (text, adress)
	def getResponse():
		response = connect.recv(1024)
		print 'server > %s' % response
		return response
else:
	send 		= lambda text: connect.sendto(text, adress) # отправление пакета
	getResponse	= lambda: connect.recv(1024)

getIP 				= lambda domain, port: getaddrinfo(domain, port, 0, 0, SOL_TCP)[0][4]
inp 				= lambda: raw_input().decode(sys.stdin.encoding)


field = list()
trump = None


colors_enabled = os.environ.has_key('TERM')

brown = '3m' # поля для ввода
red = '1m' # ошибки, выходы игроков и выключение сервера
green = '2m' # системные сообщения
blue = '4m' # процесс игры

def Print(text, color = None, nospace = False):
#	try:
	text = text.encode(sys.stdout.encoding)
	if color and colors_enabled:
		text = '%s[3%s%s%s[0m' % (chr(27), color, text, chr(27))
	if nospace:
		sys.stdout.write(text)
		sys.stdout.flush()
	else: print text
#	except: pass

def isNumber(text):
	try: int(text)
	except: return False
	else: return True

def numCards():
	text = unicode()
	for number, card in enumerate(myCards):
		text += u'%d) %s   ' % (number + 1, card)
	return text

def error(message):
	Print(u'Ошибка: сервер прислал неверный ответ (%s)' % message, red)
	os._exit(0)
	sys.exit(0)

def action():
	Print(u'Ваш ход', blue)
	Print(u'Ваши карты: ', blue, True)
	Print(numCards())
	Print(u'Козырь: %s' % trump, blue)
	Print(u'Введите номер карты или "hip" (для выхода из игры "exit"): ', brown, True)
	text = inp()
	if isNumber(text) and (0<int(text)<=len(myCards)):
		return myCards[int(text) - 1]
	elif text == 'hip' or text == 'exit': return text
	else:
		Print(u'Вы ввели какую-то хуйню', red)
		return action()

def formarField():
	formated = '|'.join(field)
	temp = '-' * len(formated)
	return '%s\n%s\n%s' % (temp, formated, temp)
		

def game():
	while True:
		response = getResponse()
		if response == 'action':
			send(action())
		elif response.startswith('trump'):
			trump = responce[6:]
			Print(u'Был выбран козырь - %s' % trump, green)
		elif response.startswith('action'):
			response = response.split()
			temp = len(response)
			if temp == 2:
				Print(u'Ходит игрок %s' % response[1], blue)
			else:
				Print(u'Игрок %s ходит картой %s' % (response[1], response[2]))
				field.append(response[2])
				Print(formarField())
		elif response == 'exit':
			Print(u'Игра окончена', red)
			os._exit(0)
			sys.exit(0)
		elif response == 'error':
			Print(u'Вы не можете ходить этой картой', red)
			send(action())
		else:
			cards = eval(response)
			Print('Ваши новые карты: %s' % cards, blue)
		################################################################
		###доделать реакцию на хип игрока и ход другого игрока картой###
		################################################################



Print(u'Введите IP или доменное имя сервера, к которому нужно подключится для игры: ', brown, True)
ip = inp()
Print(u'И порт: ', brown, True)
port = int(inp())

if ip == 'localhost':
	adress = (ip, port)
else:
	adress = getIP(ip, port)
del ip, port
print adress



connect = socket(AF_INET, SOCK_DGRAM)
send('join')
response = getResponse()
if responce == 'wait':
	Print(u'Идёт игра, ожидайте окончания', green)
	myCards = eval(getResponse())
elif response == 'ban':
	Print(u'Вам запрещено играть на этом сервере', red)
	os._exit(0)
	sys.exit(0)
else:
	myCards = eval(response)

Print(u'Ваши карты: ', blue, True)
Print('  '.join(myCards))

response = getResponse()
while response != 'started':
	if response.startswith('newGamer'):
		Print(u'Присоединился игрок %s, если в течении 15 секунд не присоединится другой игрок, игра начнётся' % response[9:], green)
	elif response == 'shutdown':
		Print(u'Сервер выключен, игра окончена', red)
		os._exit(0)
		sys.exit(0)
	elif response == 'wait':
		Print(u'Вы единственный на сервере, ожидание других игроков', green)
	else:
		error(response)		
	response = getResponse()

# сервер прислал started, начинается игра
Print(u'Игра начинается', green)
game()
