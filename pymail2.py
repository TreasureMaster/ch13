#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Обновление клиента командной строки pymail.
# Пример 13.27 (Лутц Т2 стр.287)
"""
# ---------------------------------------------------------------------------- #
pymail2 - простой консольный клиент электронной почты на языке Python;
эта версия использует пакет mailtools, который в свою очередь использует модули
poplib, smtplib и пакет email для анализа и составления электронных писем;
отображает только первую текстовую часть электронных писем, а не весь полный
текст; изначально загружает только заголовки сообщений, используя команду TOP;
полный текст загружается только для писем, выбранных для отображения;
кэширует уже загруженные письма; предупреждение: не предусматривает
возможность обновления оглавления; напрямую использует объекты из пакета
mailtools, однако они точно так же могут использоваться как суперклассы;
# ---------------------------------------------------------------------------- #
"""

# NEWIT загрузка моей конфигурации для локальной сети
localserver = True
mailconfig = __import__('maillocal') if localserver else __import__('mailconfig')

import mailtools
from pymail import inputmessage

mailcache = {}

def fetchmessage(i):
	try:
		fulltext = mailcache[i]
	except KeyError:
		fulltext = fetcher.downloadMessage(i)
		mailcache[i] = fulltext
	return fulltext

def sendmessage():
	From, To, Subj, text = inputmessage()
	sender.sendMessage(From, To, Subj, [], text, attaches=None)

def deletemessages(toDelete, verify=True):
	print('To be deleted:', toDelete)
	if verify and input('Delete?')[:1] not in ['Y', 'y']:
		print('Delete cancelled.')
	else:
		print('Deleting messages from server...')
		fetcher.deleteMessages(toDelete)

def showindex(msgList, msgSizes, chunk=5):
	count = 0
	for (msg, size) in zip(msgList, msgSizes):					# email.message.Message, int
		count += 1												# в 3.х - итератор
		print('%d:\t%d bytes' % (count, size))
		for hdr in ('From', 'To', 'Date', 'Subject'):
			print('\t%-8s=> %s' % (hdr, msg.get(hdr, '(unknown)')))
		if count % chunk == 0:
			input('[Press Enter key]')							# пауза после каждой группы сообщений

def showmessage(i, msgList):
	if 1 <= i <= len(msgList):
		fulltext = fetchmessage(i)
		message = parser.parseMessage(fulltext)
		ctype, maintext = parser.findMainText(message)
		print('-'*79)
		print(maintext.rstrip() + '\n')							# главная текстовая часть, не все письмо
		print('-'*79)											# и никаких вложений после
	else:
		print('Bad message number')

def savemessage(i, mailfile, msgList):
	if 1 <= i <= len(msgList):
		fulltext = fetchmessage(i)
		savefile =open(mailfile, 'a', encoding=mailconfig.fetchEncoding)
		savefile.write('\n' + fulltext + '-'*80 + '\n')
	else:
		print('Bad message number')

def msgnum(command):
	try:
		return int(command.split()[1])
	except:
		return -1												# предполагается, что это ошибка

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

def interact(msgList, msgSizes, mailfile):
	showindex(msgList, msgSizes)
	toDelete = []
	while True:
		try:
			command = input('[Pymail] Action? (i, l, d, s, m, q, ?) ')
		except EOFError:
			command = 'q'

		if not command: command = '*'

		if command == 'q':
			break

		elif command[0] == 'i':
			showindex(msgList, msgSizes)

		elif command[0] == 'l':
			if len(command) == 1:
				for i in range(1, len(msgList) + 1):
					showmessage(i, msgList)
			else:
				showmessage(msgnum(command), msgList)

		elif command[0] == 's':
			if len(command) == 1:
				for i in range(1, len(msgList) + 1):
					savemessage(i, mailfile, msgList)
			else:
				savemessage(msgnum(command), mailfile, msgList)

		elif command[0] == 'd':
			if len(command) == 1:
				toDelete = list(range(1, len(msgList) + 1))
			else:
				delnum = msgnum(command)
				if (1 <= delnum <= len(msgList)) and (delnum not in toDelete):
					toDelete.append(delnum)
				else:
					print('Bad message number')

		elif command[0] == 'm':
			try:
				sendmessage()
			except Exception as msg:
				print(msg)
				print('Error - mail not sent')

		elif command[0] == '?':
			print(helptext)
		else:
			print('What? -- type "?" for commands help')
	return toDelete

def main():
	global parser, sender, fetcher
	mailserver = mailconfig.popservername
	mailuser = mailconfig.popusername
	mailfile = mailconfig.savemailfile

	parser = mailtools.MailParser()
	sender = mailtools.MailSenderAuthConsole()
	fetcher = mailtools.MailFetcherConsole(mailserver, mailuser)

	def progress(i, max):
		print(i, 'of', max)

	hdrsList, msgSizes, ignore = fetcher.downloadAllHeaders(progress)
	msgList = [parser.parseHeaders(hdrtext) for hdrtext in hdrsList]

	print('[Pymail email client]')
	toDelete = interact(msgList, msgSizes, mailfile)

	if toDelete: deletemessages(toDelete)


if __name__ == '__main__':
	main()