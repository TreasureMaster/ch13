#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача каталогов с помощью ftplib.
# Выгрузка каталогов сайтов.
# Пример 13.11 (Лутц Т2 стр.153)
"""
# ---------------------------------------------------------------------------- #
использует FTP для выгрузки всех файлов из локального каталога на удаленный
сайт/каталог; например, сценарий можно использовать для копирования
файлов веб/FTP сайта с вашего ПК на сервер провайдера; выполняет выгрузку
плоского каталога: вложенные каталоги можно копировать с помощью
сценария uploadall.py, дополнительные примечания смотрите в комментариях
в downloadflat.py: этот сценарий является его зеркальным отражением.
# ---------------------------------------------------------------------------- #
"""

import os, sys, ftplib
from getpass import getpass
from mimetypes import guess_type

nonpassive = False									# пассивный режим FTP по умолчанию
remotesite = 'GMP'									# выгрузить на этот сайт
remotedir = 'books'									# с компьютера где выполняется сценарий
remoteuser = 'combo'
remotepass = getpass('Password for %s on %s: ' % (remoteuser, remotesite))
localdir = (len(sys.argv) > 1 and sys.argv[1]) or '.'
cleanall = input('Clean remote directory first? ')[:1] in ['Y', 'y']

print('connecting...')
connection = ftplib.FTP(remotesite)					# соединиться с FTP-сайтом
connection.login(remoteuser, remotepass)			# зарегистрироваться с именем/паролем
connection.cwd(remotedir)							# перейти в каталог копирования

if nonpassive:										# принудительный переход в активный режим FTP
	connection.set_pasv(False)						# большинство серверов работают в пассивном режиме

if cleanall:
	for remotename in connection.nlst():			# уничтожить все удаленные файлы,
		try:										# чтобы избавиться от устаревших копий
			print('deleting remote', remotename)	# проупстить . и ..
			connection.delete(remotename)
		except:
			print('cannot delete remote', remotename)

count = 0											# выгрузить все локальные файлы
localfiles = os.listdir(localdir)					# listdir() отбрасывает путь к каталогу, любая ошибка завершит сценарий

for localname in localfiles:
	mimetype, encoding = guess_type(localname)		# например, ('text/plain', 'gzip')
	mimetype = mimetype or '?/?'					# допускается (None, None)
	maintype = mimetype.split('/')[0]				# .jpg ('image/jpeg', None)

	localpath = os.path.join(localdir, localname)
	print('uploading', localpath, 'to', localname, end=' ')
	print('as', maintype, encoding or '')

	if maintype == 'text' and encoding == None:
		# использовать двоичный файл и режим передачи ascii
		# для поддержки логики обработки символов конца строки
		# требуется использовать режим 'rb'
		localfile = open(localpath, 'rb')
		connection.storlines('STOR ' + localname, localfile)
	else:
		# использовать двоичный файл и двоичный режим передачи
		localfile = open(localpath, 'rb')
		connection.storbinary('STOR ' + localname, localfile)

	localfile.close()
	count += 1

connection.quit()
print('Done:', count, 'files uploaded.')