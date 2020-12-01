#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Класс MailTool.
# Пример 13.22 (Лутц Т2 стр.252)
"""
# ---------------------------------------------------------------------------- #
общие суперклассы: используются для включения и отключения вывода
трассировочных сообщений
# ---------------------------------------------------------------------------- #
"""
from resolvingConfig import mailconfig


class MailTool:								# суперкласс всех инструментов электронной почты

	def trace(self, message):				# переопределите, чтобы запретить выводить в файл журнала
		print(message)


class LoggedMailTool:								# суперкласс всех инструментов электронной почты
	import os, time
	loggedpath = os.path.join(os.getcwd(), 'TraceLog')
	if not os.path.exists(loggedpath): os.mkdir(loggedpath)
	loggedfile = os.path.join(loggedpath, 'trace.log')
	tracelog = open(loggedfile, 'a', encoding='utf-8')
	print(file=tracelog)
	print('#'*60, file=tracelog)
	print(time.ctime(time.time()), file=tracelog)

	def trace(self, message):				# переопределите, чтобы запретить выводить в файл журнала
		print(message, file=self.tracelog, flush=True)

if 'selectLogging' in mailconfig.__dict__ and mailconfig.selectLogging:
	MailTool = LoggedMailTool

class SilentMailTool:						# для подмешивания, а не наследования

	def trace(self, message):
		pass