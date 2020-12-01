#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача деревьев каталогов с помощью ftplib.
# Удаление деревьев каталогов на сервере.
# Пример 13.16 (Лутц Т2 стр.172)
"""
# ---------------------------------------------------------------------------- #
расширяет класс FtpTools возможностью удаления файлов и подкаталогов
в дереве каталогов на сервере: поддерживает удаление вложенных подкаталогов;
зависит от формата вывода команды dir(), который может отличаться
на некоторых серверах! - смотрите подсказки в файле
Tools\Scripts\ftpmirror.py, в каталоге установки Python;
добавьте возможность загрузки дерева каталогов с сервера;
# ---------------------------------------------------------------------------- #
"""

from ftptools import FtpTools

class CleanAll(FtpTools):
	"""
	удаляет все дерево каталогов на сервере
	"""
	def __init__(self):
		self.fcount = self.dcount = 0

	def getlocaldir(self):
		return None											# не имеет смысла здесь

	def getcleanall(self):
		return True											# само собой разумеется здесь

	def cleanDir(self):
		"""
		для каждого элемента в текущем каталоге на сервере
		удаляет простые файлы, выполняет рекурсивный спуск и удаляет
		подкаталоги, метод dir() объекта FTP передает каждую строку
		указанной функции или методу
		"""
		lines = []											# на каждом уровне свой список строк
		self.connection.dir(lines.append)					# список текущего каталога на сервере

		for line in lines:
			parsed = line.split()							# разбить по пробельным символам
			permiss = parsed[0]								# предполагается формат для подкаталога:
			fname = parsed[-1]								# 'drwxr-xr-x 1 ftp ftp 			0 Oct 20 13:29 audio'
			if fname in ('.', '..'):							# некоторые серверы включают cwd и родительский каталог
				continue
			elif permiss[0] != 'd':							# простой файл: удалить
				print('file', fname)
				self.connection.delete(fname)
				self.fcount += 1
			else:											# каталог: удалит рекурсивно
				print('directory', fname)
				self.connection.cwd(fname)					# переход в каталог на сервере
				self.cleanDir()								# очистить подкаталог
				self.connection.cwd('..')					# возврат на уровень выше
				self.connection.rmd(fname)					# удалить пустой каталог на сервере
				self.dcount += 1
				print('directory exited')


if __name__ == '__main__':
	ftp = CleanAll()
	ftp.configTransfer(site='GMP', rdir='test1', user='combo')
	ftp.run(cleanTarget=ftp.cleanDir)
	print('Done:', ftp.fcount, 'files and', ftp.dcount, 'directories cleaned.')