#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача каталогов с помощью ftplib.
# Реогранизация сценариев выгрузки и загрузки для многократного использования.
# Версия на основе классов.
# Пример 13.14 (Лутц Т2 стр.163)
"""
# ---------------------------------------------------------------------------- #
использует протокол FTP для загрузки из удаленного каталога или выгрузки
в удаленный каталог всех файлов сайта; для организации пространства имен
и обеспечения более естественной структуры программного кода в этой версии
используются классы и приемы ООП; мы могли бы также организовать сценарий
как суперкласс, выполняющий загрузку, и подкласс, выполняющий выгрузку,
который переопределяет методы очистки каталога и передачи файла, но это
усложнило бы в других клиентах возможность выполнения обеих оперций,
загрузки и выгрузки; для сценария uploadall и, возможно, для других также
предусмотрены методы, выполняющие выгрузку/загрузку единственного файла,
которые используются в цикле в оригинальных методах;
# ---------------------------------------------------------------------------- #
"""

import os, sys, ftplib
from getpass import getpass
from mimetypes import guess_type, add_type

# значение по умолчанию для всех клиентов
dfltSite = 'GMP'
dfltRdir = 'test'
dfltUser = 'combo'

class FtpTools:
	# следующие три метода допускается переопределять
	def getlocaldir(self):
		return (len(sys.argv) > 1 and sys.argv[1]) or 'test'

	def getcleanall(self):
		return input('Clean target dir first? ')[:1] in ['Y', 'y']

	def getpassword(self):
		return getpass('Password for %s on %s:' % (self.remoteuser, self.remotesite))

	def configTransfer(self, site=dfltSite, rdir=dfltRdir, user=dfltUser):
		"""
		принимает параметры операции выгрузки или загрузки
		из значений по умолчанию в модуле, из аргументов,
		из кмоандной строки, из ввода пользователя
		анонимный доступ к FTP: user='anonymous' pass=emailaddr
		"""
		self.nonpassive = False									# пассивный режим FTP по умолчанию в 2.1+
		self.remotesite = site									# удаленный сайт куда/откуда выполняется передача
		self.remotedir = rdir									# и каталог ('.' - корень учетной записи)
		self.remoteuser = user
		self.localdir = self.getlocaldir()
		self.cleanall = self.getcleanall()
		self.remotepass = self.getpassword()

	def isTextKind(self, remotename, trace=True):
		"""
		использует mimetype для определения принадлежности файла
		к текстовому или довичному типу
		'f.html' определяется как ('text/html', None): текст
		'f.jpeg' определяется как ('image/jpeg', None): двоичный
		'f.txt.gz' определяется как ('text/plain', 'gzip'): двоичный
		неизвестные расширения определяются как (None, None): двоичные
		модуль mimetype способен также строить предполоежния об именах
		исходя из типа: смотрите пример PyMailGUI
		"""
		add_type('text/x-python-win', '.pyw')						# отсутствует в таблицах
		mimetype, encoding = guess_type(remotename, strict=False)	# разрешить расширенную интерпретацию
		mimetype = mimetype or '?/?'								# тип неизвестен?
		maintype = mimetype.split('/')[0]							# получить первый элемент
		if trace: print(maintype, encoding or '')
		return maintype == 'text' and encoding == None				# не сжатый текст

	def connectFtp(self):
		print('connecting...')
		connection = ftplib.FTP(self.remotesite)					# соединиться с FTP-сайтом
		connection.login(self.remoteuser, self.remotepass)			# зарегистрироваться
		connection.cwd(self.remotedir)								# перейти в каталог
		if self.nonpassive:											# переход в активный режим FTP при необходимости
			connection.set_pasv(False)								# большинство - в пассивном режиме
		self.connection = connection

	def cleanLocals(self):
		"""
		пытается удалить все локальные файлы, чтобы убрать устарвешие копии
		"""
		if self.cleanall:
			for localname in os.listdir(self.localdir):				# локальные файлы
				try:												# удаление файла
					print('deleting local', localname)
					os.remove(os.path.join(self.localdir, localname))
				except:
					print('cannot delete local', localname)

	def cleanRemote(self):
		"""
		пытается сначала удалить все файлы в каталоге на сервере,
		чтобы ликвидировать устарвешние копии
		"""
		if self.cleanall:
			for remotename in self.connection.nlst():				# список файлов
				try:												# удаление файла
					print('deleting remote', remotename)
					self.connection.delete(remotename)
				except:
					print('cannot delete remote', remotename)

	def downloadOne(self, remotename, localpath):
		"""
		загружает один файл по FTP в текстовом или двоичном режиме
		имя локального файла не обязательно должно соответствовать
		имени удаленного файла
		"""
		if self.isTextKind(remotename):
			localfile = open(localpath, 'w', encoding=self.connection.encoding)
			def callback(line): localfile.write(line + '\n')
			self.connection.retrlines('RETR ' + remotename, callback)
		else:
			localfile = open(localpath, 'wb')
			self.connection.retrbinary('RETR ' + remotename, localfile.write)
		localfile.close()

	def uploadOne(self, localname, localpath, remotename):
		"""
		выгружает один файл по FTP в текстовом или двоичном режиме
		имя удаленного файла не обязательно должно соответствовать
		имени локального файла
		"""
		if self.isTextKind(localname):
			localfile = open(localpath, 'rb')
			self.connection.storlines('STOR ' + remotename, localfile)
		else:
			localfile = open(localpath, 'rb')
			self.connection.storbinary('STOR ' + remotename, localfile)
		localfile.close()

	def downloadDir(self):
		"""
		загружает все файлы из удаленного каталога в соответствии
		с настройками; метод nlst() возвращает список файлов, dir() -
		полный список с дополнительными подробностями
		"""
		remotefiles = self.connection.nlst()

		for remotename in remotefiles:
			if remotename in ('.', '..'): continue
			localpath = os.path.join(self.localdir, remotename)
			print('downloading', remotename, 'to', localpath, 'as', end=' ')
			self.downloadOne(remotename, localpath)
		print('Done:', len(remotefiles), 'files downloaded.')

	def uploadDir(self):
		"""
		выгружает все файлы в каталог на сервере в соответствии
		с настройками; listdir() отбрасывает пути к каталогам,
		любые ошибки завершают сценарий
		"""
		localfiles = os.listdir(self.localdir)

		for localname in localfiles:
			localpath = os.path.join(self.localdir, localname)
			print('uploading', localpath, 'to', localname, 'as', end=' ')
			self.uploadOne(localname, localpath, localname)
		print('Done:', len(localfiles), 'files uploaded.')

	def run(self, cleanTarget=lambda: None, transferAct=lambda: None):
		"""
		выполняет весь сеанс FTP
		по умолчанию очистка каталога и передача не выполняются
		не удаляет файлы, если соединение с сервером установить не удалось
		"""
		self.connectFtp()
		cleanTarget()
		transferAct()
		self.connection.quit()


if __name__ == '__main__':
	ftp = FtpTools()
	xfermode = 'download'
	if len(sys.argv) > 1:
		xfermode = sys.argv.pop(1)							# получить и удалить второй аргумент
	if xfermode == 'download':
		ftp.configTransfer()
		ftp.run(cleanTarget=ftp.cleanLocals, transferAct=ftp.downloadDir)
	elif xfermode == 'upload':
		ftp.configTransfer(site='GMP', rdir='test', user='combo')
		ftp.run(cleanTarget=ftp.cleanRemote, transferAct=ftp.uploadDir)
	else:
		print('Usage: ftptools.py ["download" | "upload"] [localdir]')