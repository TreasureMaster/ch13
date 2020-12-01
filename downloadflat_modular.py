#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача каталогов с помощью ftplib.
# Реогранизация сценариев выгрузки и загрузки для многократного использования.
# Версия на основе функций.
# Пример 13.12 (Лутц Т2 стр.159)
"""
# ---------------------------------------------------------------------------- #
использует протокол FTP для копирования (загрузки) всех файлов из каталога
на удаленном сайте в каталог на локальном компьютере; эта версия действует
точно так же, но была реогранизована с целью завернуть фрагменты
программного кода в функции, чтобы их можно было повторно использовать
в сценарии выгрузки каталога и, возможно, в других программах в будущем -
в противном случае избыточность программного кода может с течением времени
привести к появлению различий в изначально одинаковых фрагментах
и усложнит сопровождение.
# ---------------------------------------------------------------------------- #
"""

import os, sys, ftplib
from getpass import getpass
from mimetypes import guess_type, add_type

defaultSite = 'GMP'
defaultRdir = 'test'
deafultUser = 'combo'

def configTransfer(site=defaultSite, rdir=defaultRdir, user=deafultUser):
	"""
	принимает параметры выгрузки или загрузки
	из-за большого количества параметров использует класс
	"""
	class cf: pass
	cf.nonpassive = False								# пассивный режим FTP, по умолчанию в 2.1+
	cf.remotesite = site								# удаленный сайт куда/откуда выполняется передача
	cf.remotedir = rdir									# и каталог ('.' означает корень учетной записи)
	cf.remoteuser = user
	cf.localdir = (len(sys.argv) > 1 and sys.argv[1]) or '.'
	cf.cleanall = input('Clean target directory first? ')[:1] in ['Y', 'y']
	cf.remotepass = getpass('Password for %s on %s: ' % (cf.remoteuser, cf.remotesite))
	return cf

def isTextKind(remotename, trace=True):
	"""
	использует mimetype для определения принадлежности файла
	к текстовому или двоичному типу
	'f.html' определяется как ('text/html', None): текст
	'f.jpeg' определяется как ('image/jpeg', None): двоичный
	'f.txt.gz' определяется как ('text/plain', 'gzip'): двоичный
	файлы с неизвестными расширениями определяются как (None, None): двоичные
	модуль mimetype способен также строить предположение об именах
	исходя из типа: смотрите пример PyMailGUI
	"""
	add_type('text/x-python-win', '.pyw')						# отсутствует в таблицах
	mimetype, encoding = guess_type(remotename, strict=False)	# разрешить расширенную интерпретацию
	mimetype = mimetype or '?/?'								# тип неизвестен?
	maintype = mimetype.split('/')[0]							# получить первый элемент
	if trace: print(maintype, encoding or '')
	return maintype == 'text' and encoding == None				# не сжатый текст

def connectFtp(cf):
	print('connecting...')
	connection = ftplib.FTP(cf.remotesite)						# соединиться с FTP-сайтом
	connection.login(cf.remoteuser, cf.remotepass)				# зарегистрироваться
	connection.cwd(cf.remotedir)								# перейти в каталог
	if cf.nonpassive:											# переход в активный режим FTP при необходимости
		connection.set_pasv(False)								# большинство работают в пассивном режиме
	return connection

def cleanLocals(cf):
	"""
	пытается удалить все локальные файлы, чтобы убрать устаревшие копии
	"""
	if cf.cleanall:
		for localname in os.listdir(cf.localdir):				# список локальных файлов
			try:												# удаление локального файла
				print('deleting local', localname)
				os.remove(os.path.join(cf.localdir, localname))
			except:
				print('cannot delete local', localname)

def downloadAll(cf, connection):
	"""
	загружает все файлы из удаленного каталог в соответствии с настройками в cf;
	метод nlst() возвращает список файлов, dir() - полный список
	с дополнительными подробностями
	"""
	remotefiles = connection.nlst()
	for remotename in remotefiles:
		if remotename in ('.', '..'): continue
		localpath = os.path.join(cf.localdir, remotename)
		print('downloading', remotename, 'to', localpath, 'as', end=' ')
		if isTextKind(remotename):
			# использовать текстовый режим передачи
			localfile = open(localpath, 'w', encoding=connection.encoding)
			def callback(line): localfile.write(line + '\n')
			connection.retrlines('RETR ' + remotename, callback)
		else:
			# использовать двоичный режим передачи
			localfile = open(localpath, 'wb')
			connection.retrbinary('RETR ' + remotename, localfile.write)
		localfile.close()
	connection.quit()
	print('Done:', len(remotefiles), 'files downloaded.')


if __name__ == '__main__':
	cf = configTransfer()
	conn = connectFtp(cf)
	cleanLocals(cf)											# не удалять файлы, если соединение не было установлено
	downloadAll(cf, conn)