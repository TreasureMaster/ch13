#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Утилиты FTP get и put.
# Утилита выгрузки.
# Пример 13.5 (Лутц Т2 стр.133)
"""
# ---------------------------------------------------------------------------- #
Выгружает произвольный файл по FTP в двоичном режиме.
Использует анонимный доступ к FTP, если функции не был передан
кортеж user=(имя, пароль) аргументов.
# ---------------------------------------------------------------------------- #
"""

import ftplib

def putfile(file, site, dir, user=(), *, verbose=True):
	"""
	выгружает произвольный файл по FTP на сайт/каталог, используя анонимный
	доступ или действительную учетную запись, двоичный режим передачи
	"""
	if verbose: print('Uploading', file)
	local = open(file, 'rb')								# локальный файл с тем же именем
	remote = ftplib.FTP(site)								# соединиться с FTP-сайтом
	remote.login(*user)										# анонимная или действительная учетная запись
	remote.cwd(dir)
	remote.storbinary('STOR ' + file, local, 1024)
	remote.quit()
	local.close()
	if verbose: print('Upload done.')


if __name__ == '__main__':
	site = 'GMP'
	dir = '.'
	import sys, getpass
	pswd = getpass.getpass(site + ' pswd?')
	putfile(sys.argv[1], site, dir, user=('combo', pswd))	# имя файла в командной строке
															# действительная учетная запись