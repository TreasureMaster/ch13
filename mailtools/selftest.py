#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Сценарий самотестирования.
# Пример 13.26 (Лутц Т2 стр.283)
"""
# ---------------------------------------------------------------------------- #
когда этот файл запускается как самостоятельный сценарий,
выполняет тестирование пакета
# ---------------------------------------------------------------------------- #
"""

# обычно используется модуль mailconfig, находящийся в каталоге клиента или в пути sys.path;
# для нужд тестирования берется модуль из каталога Email уровнем выше

# import sys, os
# sys.path.insert(0, os.path.abspath('..'))
# print(sys.path)
# print(os.getcwd())
# import os
# sys.path.append(os.path.abspath(os.getcwd()))
# print()
# клиентские настройки (переменная localserver определяет какой модуль будет загружен -
# с локальными или удаленными настройками конфигурации)
# localserver = True
# mailconfig = __import__('maillocal') if localserver else __import__('mailconfig')
from resolvingConfig import mailconfig
print('config:', mailconfig.__file__)

# получить из __init__
from mailtools import (MailFetcherConsole,
					   MailSender, MailSenderAuthConsole,
					   MailParser)

if not mailconfig.smtpuser:
	sender = MailSender(tracesize=5000)
else:
	sender = MailSenderAuthConsole(tracesize=5000)

sender.sendMessage(
	From      = mailconfig.myaddress,
	To        = [mailconfig.myaddress],
	Subj      = 'testing mailtools package: new resolvingConfig',
	extrahdrs = [('X-Mailer', 'mailtools')],
	bodytext  = 'Here is my source code\n',
	attaches  = ['getone.py'],
)
	# bodytextEncoding = 'utf-8',						# дополнительные тесты
	# attachesEncoding = ['latin-1'],					# проверка текста заголовков
	# attaches = ['monkeys.jpg'],						# проверка Base64
	# to = 'i18n addr list...',							# тест заголовков mime/unicode

# измените параметр fetchlimit в модуле mailconfig,
# чтобы проверить ограничение на количество получаемых сообщений
fetcher = MailFetcherConsole()
def status(*args): print(args)

hdrs, sizes, loadedall = fetcher.downloadAllHeaders(status)
for num, hdr in enumerate(hdrs[:5]):
	print(hdr)
	if input('load mail?') in ['Y', 'y']:
		print(fetcher.downloadMessage(num+1).rstrip(), '\n', '-'*70)

last5 = len(hdrs) - 4
msgs, sizes, loadedall = fetcher.downloadAllMessages(status, loadfrom=last5)
for msg in msgs:
	print(msg[:200], '\n', '-'*70)

parser = MailParser()
for i in [1]:											# попробуйте [0, len(msgs)]
	fulltext = msgs[i]
	fd = open('selftest.log', 'w')
	# import time
	# time.sleep(.1)
	message = parser.parseMessage(fulltext)

	ctype, maintext = parser.findMainText(message)
	fd.write(ctype)
	fd.write('#'*40)
	fd.write(maintext)
	fd.close()
	print('Parsed:', message['Subject'])
	print(maintext)
input('Press Enter to exit')							# пауза на случай запуска щелчком мыши в Windows
