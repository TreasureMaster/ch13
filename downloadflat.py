#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача каталогов с помощью ftplib.
# Пример 13.10 (Лутц Т2 стр.146)
"""
# ---------------------------------------------------------------------------- #
использует протокол FTP для копирования (загрузки) всех файлов
из единственного каталога на удаленном сайте в каталог на локальном
компьютере; запускайте этот сценарий периодически для создания зеркала
плоского каталога FTP-сайта, находящегося на сервере вашего провайдера;
для анонимного доступа установите переменную remoteuser в значение
'anonymous'; чтобы пропускать ошибки загрузки файлов, можно было бы
использовать инструкцию try, но в этом случае таких ошибок FTP-соединение скорее
всего все равно будет закрыто автоматически; можно было бы перед передачей
каждого нового файла переустанавливать соединение, создавая новый экземпляр
класса FTP: сейчас устанавливается всего одно соединение; в случае неудачи
попробуйте записать в переменную nonpassive значение True, чтобы
использовать активный режим FTP, или отключите брандмауер; кроме того,
работоспособность этого сценария зависит от настроек сервера FTP
и возможных ограничений на загрузку.
# ---------------------------------------------------------------------------- #
"""

import os, sys, ftplib
from getpass import getpass
from mimetypes import guess_type

nonpassive = False									# в 2.1+ по умолчанию пассивный режим FTP
remotesite = 'GMP'									# загрузить с этого сайта
remotedir = './Test'								# и из этого каталога (например, public_html)
remoteuser = 'gold'
# remoteuser = 'combo'
remotepass = getpass('Password for %s on %s: ' % (remoteuser, remotesite))
localdir = (len(sys.argv) > 1 and sys.argv[1]) or './test'
cleanall = input('Clean local directory first? ')[:1] in ['Y', 'y']

print('connecting...')
connection = ftplib.FTP(remotesite)					# соединиться с FTP-сайтом
connection.login(remoteuser, remotepass)			# зарегистрироваться с именем/паролем
connection.cwd(remotedir)							# перейти в копируемый каталог
if nonpassive:										# принудительный перход в активный режим FTP
	connection.set_pasv(False)						# большинство серверов работают в пассивном режиме

if cleanall:										# сначала удалить все локальные файлы,
	for localname in os.listdir(localdir):			# чтобы избавиться от устаревших копий
		try:										# os.listdir пропускает . и ..
			print('deleting local', localname)
			os.remove(os.path.join(localdir, localname))
		except:
			print('cannot delete local', localname)

count = 0											# загрузить все файлы из удаленного каталога
remotefiles = connection.nlst()						# nlst() возвращает список файлов
													# dir() возвращает полный список
for remotename in remotefiles:
	if remotename in ('.', '..'): continue			# некоторые серверы включают . и ..

	mimetype, encoding = guess_type(remotename)		# например, ('text/plain', 'gzip')
	mimetype = mimetype or '?/?'					# допускается (None, None)
	maintype = mimetype.split('/')[0]				# .jpg - это ('image/jpeg', None)

	localpath = os.path.join(localdir, remotename)
	print('downloading', remotename, 'to', localpath, end=' ')
	print('as', maintype, encoding or '')

	if maintype == 'text' and encoding == None:
		# использовать текстовый файл и режим передачи ascii
		# использовать кодировку, совместимую с ftplib
		localfile = open(localpath, 'w', encoding=connection.encoding)
		callback = lambda line: localfile.write(line + '\n')
		connection.retrlines('RETR ' + remotename, callback)
	else:
		# использовать двоичный файл и двоичный режим передачи
		localfile = open(localpath, 'wb')
		connection.retrbinary('RETR ' + remotename, localfile.write)

	localfile.close()
	count += 1

connection.quit()
print('Done:', count, 'files downloaded.')