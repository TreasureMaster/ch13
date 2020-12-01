#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# NNTP: доступ к телеконференциям.
# Пример 13.28 (Лутц Т2 стр.294)
"""
# ---------------------------------------------------------------------------- #
получает и выводит сообщения из телеконференции comp.lang.python с помощью
модуля nntplib, который в действительности действует поверх сокетов;
nntplib поддеживает также отправку новых сообщений и так далее;
примечание: после прочтения сообщения не удаляются;
# ---------------------------------------------------------------------------- #
"""

listonly = False
showhdrs = ['From', 'Subject', 'Date', 'Newsgroups', 'Lines']

try:
	import sys
	servername, groupname, showcount = sys.argv[1:]
	showcount = int(showcount)
except:
	servername = 'news.usenet.net'								# присвойте этому параметру имя сервера
	groupname = 'comp.software'							# аргумент командной строки или значение по умолчанию
	showcount = 10											# показать последние showcount сообщений

# соединиться с сервером NNTP
print('Connecting to', servername, 'for', groupname)

from nntplib import NNTP

connection = NNTP(servername)
(reply, count, first, last, name) = connection.group(groupname)
print('%s has %s articles: %s-%s' % (name, count, first, last))

# запросить только заголовки
fetchfrom = str(int(last) - (showcount-1))
(reply, subjects) = connection.xhdr('subject', (fetchfrom + '-' + last))

# вывести заголовки, получить заголовки + тело
for (id, subj) in subjects:									# [-showcount:] для загрузки всех заголовков
	print('Article %s [%s]' % (id, subj))
	if not listonly and input('=> Display?') in ['Y', 'y']:
		reply, num, tid, listing = connection.head(id)
		for line in listing:
			for prefix in showhdrs:
				if line[:len(prefix)] == prefix:
					print(line[:80])
					break
		if input('=> Show body?') in ['Y', 'y']:
			reply, num, tid, listing = connection.body(id)
			for line in listing:
				print(line[:80])
	print()
print(connection.quit())