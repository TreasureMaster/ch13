#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача каталогов с помощью ftplib.
# Реогранизация сценариев выгрузки и загрузки для многократного использования.
# Версия на основе функций.
# Пример 13.13 (Лутц Т2 стр.161)
"""
# ---------------------------------------------------------------------------- #
использует FTP для выгрузки всех файлов из локального каталога на удаленный
сайт/каталог; эта версия повторно использует функции из сценария загрузки,
чтобы избежать избыточности программного кода;
# ---------------------------------------------------------------------------- #
"""

import os
from downloadflat_modular import configTransfer, connectFtp, isTextKind

def cleanRemotes(cf, connection):
	"""
	пытается сначала удалить все файлы в каталоге на сервере,
	чтобы ликвидировать устаревшие копии
	"""
	if cf.cleanall:
		for remotename in connection.nlst():					# список файлов на сервере
			try:												# удаление файла на сервере
				print('deleting remote', remotename)			# проупстить '.' и '..'
				connection.delete(remotename)
			except:
				print('cannot delete remote', remotename)

def uploadAll(cf, connection):
	"""
	выгружает все файлы в каталог на сервере в соответствии с настройками cf
	listdir() отбрасывает пути к каталогм, любые ошибки завершают сценарий
	"""
	localfiles = os.listdir(cf.localdir)
	for localname in localfiles:
		localpath = os.path.join(cf.localdir, localname)
		print('uploading', localpath, 'to', localname, 'as', end=' ')
		if isTextKind(localname):
			# использовать текстовый режим передачи
			localfile = open(localpath, 'rb')
			connection.storlines('STOR ' + localname, localfile)
		else:
			# использовать двоичный режим передачи
			localfile = open(localpath, 'rb')
			connection.storbinary('STOR ' + localname, localfile)
		localfile.close()
	connection.quit()
	print('Done:', len(localfiles), 'files uploaded.')


if __name__ == '__main__':
	cf = configTransfer(site='GMP', rdir='test', user='combo')
	conn = connectFtp(cf)
	cleanRemotes(cf, conn)
	uploadAll(cf, conn)