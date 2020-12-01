#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# SMTP: отправка электронной почты.
# Сценарий отправки электронной почты по SMTP (Simple Mail Transfer Protocol).
# Пример 13.19 (Лутц Т2 стр.192)
"""
# ---------------------------------------------------------------------------- #
использует модуль Python почтового интерфейса SMTP для отправки сообщений;
это простой сценарий одноразовой отправки - смотрите pymail, PyMailGUI
и PyMailCGI, реализующие клиентов с более широкими возможностями
взаимодействия с пользователями; смотрите также popmail.py - сценарий
получения почты, и пакет mailtools, позволяющий добавлять вложения
и форматировать сообщения с помощью стандартного пакета email;
# ---------------------------------------------------------------------------- #
"""

import smtplib, sys, email.utils, mailconfig

mailserver = mailconfig.smtpservername						# например: smtp.rmi.net
# mailserver = '192.168.0.14'
mailserver = 'GMP'

From = input('From?').strip()								# или импортировать из mailconfig
# From = 'am5x86p75@list.ru'
# To = input('To?').strip()									# например: python-list@python.org
To = 'test@test.loc'
Tos = To.split(';')											# допускается список получателей
Subj = input('Subj?').strip()
Date = email.utils.formatdate()								# текущее дата и время в стандарте RFC2822

# стандартные заголовки, за которыми следует пустая строка и текст
text = ('From: %s\nTo: %s\nDate: %s\nSubject: %s\n\n' % (From, To, Date, Subj))
# NEWIT тестирование с подменой поля To
# text = ('From: %s\nDate: %s\nSubject: %s\n\n' % (From, Date, Subj))

print('Type message text, end with line=[Ctrl+d (Unix), Ctrl+z (Windows)]')

while True:
	line = sys.stdin.readline()
	if not line:
		break												# выход по ctrl-d/z
	# if line[:4] == 'From':
		# line = '>' + line									# серверы могут экранировать
	text += line

print('Connecting...')
# WARNING требуется безопасное шифрование SSL
server = smtplib.SMTP(mailserver)							# соединиться без регистрации
# WARNING mail.ru требуется регистрация
import maillocal
server.login(maillocal.myaddress, 'test')
# server.login(mailconfig.myaddress, 'TrBVX1*jy5ka')
failed = server.sendmail(From, Tos, text)
server.quit()
if failed:													# smtplib может возбуждать исключения
	print('Failed recipients:', failed)						# но здесь они не обрабатываются
else:
	print('No errors.')
print('Bye.')