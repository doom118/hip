#! /usr/bin/python2
# encoding: utf-8
# Copyright The multiuser HIP game © Assassin, 2011 - 2012
# This program published under Apache 2.0 license
# See LICENSE.txt for more details
# My EMail: assassin@sonikelf.ru
# My XMPP-conference: bottiks@conference.jabber.ru (closed)
# My Site: bottiks.ucoz.ru (closed)
# Multiuser game HIP - server

# Карточная игра Хип
# Правила идентичны всеми известному "Дураку", но есть несколько поправок:
# Игроку выдаются 4 карты в начале игры, вместо 6
# Цель игры - собрать 4 карты одинаковых мастей (прочих карт в руках не должно быть)
# После того, как кончается колода, она перемешивается и снова используется


# config
IP 	= ('87.98.168.93', 405846)
#IP = ('your ip address', 9248)# for game on Internet
debug = True # можете использовать для мухлежа \
# (если честно то для этого дебаг и был сделан :-D)
# end of config

# ToDo: немного переписать для игры более 2х человек


import sys, os
if debug:
	def send(adress, connect, text):
		connect.sendto(text, adress)
		print '%s > %s' % (text, adress)
else:
	send	= lambda adress, connect, text: connect.sendto(text, adress) # отправление пакета
field		= list() # поле для карт (хз как ещё назвать переменную :-) )

sys.path.insert(0, 'libs')
from SocketServer import TCPServer, BaseRequestHandler
from random import choice as RChoice
from threading import Timer

reload(sys).setdefaultencoding('utf8')


core = os.path.abspath(__file__)
coreDir = os.path.split(core)[0]
if coreDir: os.chdir(coreDir)

cards	= list()
numbers = [unicode(x) for x in range(6, 11)].__add__([u'В', u'Д', u'К', u'Т'])
masts = tuple([unichr(x) for x in (9829, 9830, 9824, 9827)])
polices = \
	{u'6': u'шелбан',
	u'7': u'фофан',
	u'8': u'крысиный кайф',
	u'9': u'удар в плечо',
	u'10': u'пощёчина',				# наказания
	u'В': u'погладь по головке',
	u'Д': u'бритва',
	u'К': u'лось',
	u'Т': u'королевский лось'
	}
notability = \
	{
	u'В': 11,
	u'Д': 12,
	u'К': 13,
	u'Т': 14
	}
def isNumber(text):
	try: int(text)
	except: return False
	else: return True

ban = list()

timer = None

trump = None # козырь

for mast in masts[0:2]:
	for number in numbers:
		cards.append(u'%s[31m%s%s[0m' % (chr(27), u'%s%s' % (number, mast), chr(27)))

for mast in masts[2:4]:
	for number in numbers:
		cards.append(u'%s%s' % (number, mast))
del numbers

notUsedCards = list(cards) # делаем копию всех существующих карт

users = dict()

def sendToAll(connect, text): # отправление пакета всем участникам
	if debug: print text
	for adress in users:
		send(adress, connect, text)

def minus(a, b):
	for x in b:
		if x in a: a.remove(x)
	return a

def HIP(ip):
	########################################################
	############доделать реакцию на хип игрока##############
	########################################################
	pass
def game(connect):
	sendToAll(connect, 'started')
	trump = RChoice(masts)
	sendToAll(conncet, 'trump %s' % trump)
	action(RChoice(users), connect)
	
def action(user, connect):
	user.status = 'action'
	if debug: print u'ходит игрок %s' % user.address
	sendToAll(connect, 'action %s' % user.address)
	send(user.address, connect, 'action')
isInt = lambda numb: int(numb) == float(numb) # проверка, целое ли число (велосипед, я знаю) \
# присылайте варианты лучше

getBody = lambda card: (card[5:-3] if len(card) > 2 else card) # возвращает саму карту, \
# т.е. без обозначения цвета

def getNotability(card):
	if isNumber(card[0]):
		notability = int(card[0])
	else:
		notability = notability[card[0]]
	if card[1] == trump:
		notability += 14
	return notability

'''def getBody(card):
	if len(card) > 2:
		card = card[5:-3]
	return card'''
	

class user:
	def __init__(self, address):
		self.address = address
		self.status = 'wait' # что сейчас делает игрок:
		# wait - ждёт пока другие игроки ходят, или же самих других игроков
		# action - ходит
		self.cards = list()
	def refreshCards(self):
		while len(self.cards) < 4:
			card = RChoice(cards)
			self.cards.append(card)
			notUsedCards.remove(card)
		if debug: print u'у юзера %s %s' % (self.client_address, ' '.join(self.cards))
		return self.cards
	haveHip = lambda self: ((len(self.cards) == 4) and \
	(self.cards[0] == self.cards[1] == self.cards[2] == self.cards[3]))
	def haveHip(self):
		for x in range(3):
			if not self.cards[x] == self.cards[x+1]:
				return False
		return True
'''	def haveHip(self): # есть ли у игрока хип (все ли масти одинаковые)
		for mast in masts:
			if self.cards[0].count(mast):
				haveMast = mast
		for card in self.cards:
			if not card.count(haveMast): return False
		return haveMast'''

class Server(BaseRequestHandler):
	def handle(self):
		command = self.request[0].strip()
		if debug:
			print '%s > %s' % (self.client_address, command)
		if self.client_address[0] in ban: # юзер забанен
			send(self.client_address, self.request[1], 'ban')
		else:
			if command:
				if users.has_key(self.client_address):
					if command == 'exit':
						if debug: print u'юзер %s вышел из игры' % self.client_address
						sendToAll(self.request[1], 'exit')
					elif command == 'hip':
						if debug: print u'юзер %s объявил хип' % self.client_address
						if users[self.client_address].haveHip():
							HIP(self.client_address)
						else: sendToAll(self.request[1], 'exit')
					elif command in cards:
						if debug: print u'юзер %s ходит картой %s' % (self.client_address, command)
						if (not users[self.client_address].status == 'action') and \
							(command in users[self.client_address].cards):
							if (not isInt(len(field) / 2)) or \
								((getNotability(getBody(field[-1])) - getNotability(getBody(command))) > 0):
								field.append(command) # добавляем карту на поле
								users[self.client_address].status = 'wait'
								users[self.client_address].refreshCards()
								send(self.client_address, self.request[1], unicode(cards))
								sendToAll(self.request[1], 'action %s %s' % (self.client_address, command))
							else:
								#ошибка
								send(self.client_address, self.request[1], 'error')
								# если количество карт на поле не чётное, т.е. игрок \
								# отбивается, а не ходит новой картой, иначе никакие \
								# проверки не нужны
								# проверить, может ли игрок отбиться этой картой или нет
								
						########################################################
						#########доделать реакцию на ход игрока картой##########
						########################################################
					else:
						if debug: print u'юзер %s прислал какую-то хуйню' % self.client_address
				elif (command == 'join'):
					if debug: print u'юзер %s вошёл в игру' % self.client_address
					if timer:
						timer.cancel()
						timer = None
					users[self.client_address] = user(self.client_address)
					send(self.client_address, self.request[1], unicode(users[self.client_address].refreshCards()))
					if len(users) > 1:
						send(self.client_address, self.request[1], 'newGamer %s' % self.client_address)
						timer = Timer(15, game, (self.request[1],))
					else: send(self.client_address, self.request[1], 'wait')
				else: 
					if debug: print u'юзер %s прислал какую-то хуйню' % self.client_address
			else:
				if debug: print u'юзер %s прислал какую-то хуйню' % self.client_address


server = TCPServer(IP, Server)
server.serve_forever()
