#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# POP: чтение электронной почты.
# Сценарий чтения почты с сервера POP (Post Office Protocol).
# Пример 13.18 (Лутц Т2 стр.184)
"""
# ---------------------------------------------------------------------------- #
использует модуль POP3 почтового интерфейса Python для просмотра сообщений
почтовой учетной записи pop; это простой листинг - смотрите реализацию
клиента с большим количеством функций взаимодействий с пользователем
в pymail.py и сценарий отправки почту в smtpmail.py; протокол POP
используется для получения почты и на сервере выполняется на сокете
с портом номер 110, но модуль Python poplib скрывает все детали протокола;
для отправки почты используйте модуль smtplib (или os.popen('mail...')).
Смотрите также модуль imaplib, реализующий альтернативный протокол IMAP,
и программы PyMailGUI/PyMailCGI, реализующий дополнительный особенности;
# ---------------------------------------------------------------------------- #
"""

import poplib, getpass, sys, mailconfig

mailserver = mailconfig.popservername							# например: 'pop.rmi.net'
mailuser = mailconfig.popusername								# например: 'lutz'
mailpasswd = getpass.getpass('Password for %s?' % mailserver)

print('Connecting...')
# WARNING только SSL (порт 110 теперь не используется)
server = poplib.POP3_SSL(mailserver)
server.user(mailuser)											# соеднение, регистрация на сервере
server.pass_(mailpasswd)										# pass - зарезервированное слово

try:
	print(server.getwelcome())									# вывод приветствия
	msgCount, msgBytes = server.stat()
	print('There are', msgCount, 'mail messages in', msgBytes, 'bytes')
	print(server.list())
	print('-' * 80)
	input('[Press Enter key]')

	for i in range(msgCount):
		hdr, message, octets = server.retr(i + 1)				# octets - счетчик байтов
		for line in message: print(line.decode())				# читает, выводит все письма
		print('-' * 80)											# в 3.х сообщения - bytes
		if i < msgCount - 1:									# почтовый ящик блокируется
			input('[Press Enter key]')							# до вызова quit
finally:														# снять блокировку с ящика
	server.quit()												# иначе будет разблокирован по таймауту
print('Bye.')