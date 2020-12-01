#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Почтовый клиент командной строки.
# Пример 13.20 (Лутц Т2 стр.239)
"""
# ---------------------------------------------------------------------------- #
pymail - простой консольный клиент электронной почты на языке Python;
использует модуль Python poplib для получения электронных писем,
smtplib для отправки новых писем и пакет email для извлечения
заголовков с содержимым и составления новых сообщений;
# ---------------------------------------------------------------------------- #
"""

import poplib, smtplib, email.utils
from email.parser import Parser
from email.message import Message

# WARNING заголовок с русским текстом отправляется, однако письмо с русским текстом выдает ошибку.

# NEWIT загрузка моей конфигурации для локальной сети
local = True
if local:
	import maillocal as mailconfig
else:
	import mailconfig

fetchEncoding = mailconfig.fetchEncoding

def decodeToUnicode(messageBytes, fetchEncoding=fetchEncoding):
	"""
	4E, Py3.1: декодирует извлекаемые строки bytes в строки str Юникода
	для отображения или анализа; использует глобальные настройки
	(или значения по умолчанию для платформы, исследует заголовки, делает
	обоснованные предположения); в Python 3.2/3.3 этот шаг может оказаться
	необязательным: в этом случае достаточно будет просто вернуть сообщение нетронутым;
	"""
	return [line.decode(fetchEncoding) for line in messageBytes]

def splitaddrs(field):
	"""
	4E: разбивает список адресов по запятым, учитывает возможность
	появления запятых в именах
	"""
	pairs = email.utils.getaddresses([field])					# [(name, addr)]
	return [email.utils.formataddr(pair) for pair in pairs]		# [name <addr>]

def inputmessage():
	import sys
	From = input('From? ').strip()
	To = input('To? ').strip()									# заголовк Date устанавливается автоматически
	To = splitaddrs(To)											# допускается множество name + <addr>
	Subj = input('Subj? ').strip()								# не разбивать вслепую по ',' или ';'
	print('Type message text, end with line="."')
	text = ''
	while True:
		line = sys.stdin.readline()
		if line == '.\n': break
		text += line
	return From, To, Subj, text

def sendmessage(passwd):
	From, To, Subj, text = inputmessage()
	msg = Message()
	msg['From'] = From
	msg['To'] = ', '.join(To)									# для заголовка, не для отправки
	msg['Subject'] = Subj
	msg['Date'] = email.utils.formatdate()						# текущие дата и время, rfc2822
	msg.set_payload(text)

	server = smtplib.SMTP(mailconfig.smtpservername)
	server.login(mailconfig.myaddress, passwd)
	try:
		failed = server.sendmail(From, To, str(msg))			# может также возбудить исключение
	except Exception as msg:
		# print(msg)
		print('Error - send failed')
	else:
		if failed: print('Failed:', failed)

def connect(servername, user, passwd):
	print('Connecting...')
	server = poplib.POP3(servername)
	server.user(user)										# соединиться, зарегистрироваться на сервере
	server.pass_(passwd)									# pass - зарезервированное слово
	print(server.getwelcome())								# print выведет возвращаемое приветствие
	return server

def loadmessages(servername, user, passwd, loadfrom=1):
	server = connect(servername, user, passwd)
	try:
		print(server.list())
		(msgCount, msgBytes) = server.stat()
		print('There are', msgCount, 'mail messages in', msgBytes, 'bytes')
		print('Retrieving...')
		msgList = []										# получить почту
		for i in range(loadfrom, msgCount+1):				# пусто, если low >= high
			(hdr, message, octets) = server.retr(i)			# сохранить текст в списке
			message = decodeToUnicode(message)				# 4E, Py3.1: bytes в str
			msgList.append('\n'.join(message))				# оставить письмо на сервере
	finally:
		server.quit()										# разблокировать почтовый ящик
	assert len(msgList) == (msgCount - loadfrom) + 1		# нумерация с 1
	# import pprint
	# pprint.pprint(msgList)
	return msgList

def deletemessages(servername, user, passwd, toDelete, verify=True):
	print('To be deleted:', toDelete)
	if verify and input('Delete?')[:1] not in ['y', 'Y']:
		print('Delete cancelled.')
	else:
		server = connect(servername, user, passwd)
		try:
			print('Deleting messages from server...')
			for msgnum in toDelete:							# повторно соединиться для удаления писем
				server.dele(msgnum)							# ящик будет заблокирован до вызова quit()
		finally:
			server.quit()

def showindex(msgList):
	count = 0												# вывести некоторые заголовки
	for msgtext in msgList:
		msghdrs = Parser().parsestr(msgtext, headersonly=True)	# ожидается тип str в 3.1
		count += 1
		print('%d:\t%d bytes' % (count, len(msgtext)))
		for hdr in ('From', 'To', 'Date', 'Subject'):
			try:
				print('\t%-8s=> %s' % (hdr, msghdrs[hdr]))
			except KeyError:
				print('\t%-8c=> (unknown)' % hdr)
		if count % 5 == 0:
			input('[Press Enter key]')						# приостановка через каждые 5 писем

def showmessage(i, msgList):
	if 1 <= i <= len(msgList):
		# print(msgList[i-1])								# устарело: выветси целиком заголовки + текст
		print('-' * 79)
		msg = Parser().parsestr(msgList[i-1])				# ожидается тип str в 3.1
		content = msg.get_payload()							# содержимое: строка или [Messages]
		if isinstance(content, str):						# сохранить только самый последний символ конца строки
			content = content.rstrip() + '\n'
		print(content)
		print('-'*79)										# получить только текст, см email.parsers
	else:
		print('Bad message number')

def savemessage(i, mailfile, msgList):
	if 1 <= i <= len(msgList):
		savefile = open(mailfile, 'a', encoding=mailconfig.fetchEncoding)
		savefile.write('\n' + msgList[i-1] + '\n' + '-'*80)
	else:
		print('Bad message number')

def msgnum(command):
	try:
		return int(command.split()[1])
	except:
		return -1											# предполагается, что это ошибка

helptext="""
Available commands:
i    - index display
l n? - list all messages (or just message n)
d n? - mark all messages for deletion (or just message n)
s n? - save all messages to a file (or just message n)
m    - compose and send a new mail message
q    - quit pymail
?    - display this help text
"""

def interact(msgList, mailfile, mailpasswd):
	showindex(msgList)
	toDelete = []
	while True:
		try:
			command = input('[Pymail] Action? (i, l, d, s, m, q, ?) ')
		except EOFError:
			command = 'q'
		if not command: command = '*'

		# завершение
		if command == 'q':
			break

		# оглавление
		elif command[0] == 'i':
			showindex(msgList)

		# содержимое письма
		elif command[0] == 'l':
			if len(command) == 1:
				for i in range(1, len(msgList)+1):
					showmessage(i, msgList)
			else:
				showmessage(msgnum(command), msgList)

		# сохранение
		elif command[0] == 's':
			if len(command) == 1:
				for i in range(1, len(msgList)+1):
					savemessage(i, mailfile, msgList)
			else:
				savemessage(msgnum(command), mailfile, msgList)

		# удаление
		elif command[0] == 'd':
			if len(command) == 1:							# удалить все позднее
				toDelete = list(range(1, len(msgList)+1))	# в 3.х требуется вызвать list()
			else:
				delnum = msgnum(command)
				if (1 <= delnum <= len(msgList)) and (delnum not in toDelete):
					toDelete.append(delnum)
				else:
					print('Bad message number')

		# составление нового письма
		elif command[0] == 'm':								# отправить новое сообщение через SMTP
			sendmessage(mailpasswd)
			# execfile('smtpmail.py', {})					# альтернатива: запустить в собственном пространстве имен
		elif command[0] == '?':
			print(helptext)
		else:
			print('What? -- type "?" for commands help')
	return toDelete


if __name__ == '__main__':
	import getpass
	mailserver = mailconfig.popservername
	mailuser = mailconfig.popusername
	mailfile = mailconfig.savemailfile
	mailpasswd = getpass.getpass('Password for %s?' % mailserver)
	print('[Pymail email client]')
	msgList = loadmessages(mailserver, mailuser, mailpasswd)			# загрузить dct
	toDelete = interact(msgList, mailfile, mailpasswd)
	if toDelete:
		deletemessages(mailserver, mailuser, mailpasswd, toDelete)
	print('Bye.')
