#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Класс MailFetcher.
# Инструменты синхронизации почтового ящика.
# Пример 13.24 (Лутц Т2 стр.266)
"""
# ---------------------------------------------------------------------------- #
получает, удаляет, сопоставляет почту с POP-сервера (описание и тест
приводятся в модуле __init__)
# ---------------------------------------------------------------------------- #
"""

# клиентские настройки (переменная localserver определяет какой модуль будет загружен -
# с локальными или удаленными настройками конфигурации)
# localserver = False
# mailconfig = __import__('maillocal') if localserver else __import__('myconfig')
# import mailconfig
from resolvingConfig import mailconfig

import poplib, sys										# клиентский mailconfig в sys.path, в катлоге сценария, в PYTHONPATH

print('user:', mailconfig.popusername)

from .mailParser import MailParser						# сопоставление заголовков
from .mailTool import MailTool, SilentMailTool			# суперкласс, управляющий трассировкой

# рассинхронизация номеров сообщений
class DeleteSynchError(Exception): pass					# обнаружена рассинхронизация при удалении
class TopNotSupported(Exception): pass					# невозможно выполнить проверку синхронизации
class MessageSynchError(Exception): pass				# обнаружена рассинхронизация оглавления

# ANCHOR class MailFetcher
class MailFetcher(MailTool):
	"""
	получение почты: соединяется, извлекает заголовки+содержимое, удаляет
	работает на любых компьютерах с Python+Интернет; создайте подкласс,
	чтобы реализовать кэширование средствами протокола POP;
	для поддержки протокола IMAP требуется создать новый класс;
	4Е: предусматривает декодирование полного текста сообщений
	для последующей передачи его механизму анализа;
	"""
	def __init__(self, popserver=None, popuser=None, poppswd=None, hastop=True):
		self.popServer = popserver or mailconfig.popservername
		self.popUser = popuser or mailconfig.popusername
		self.srvHasTop = hastop
		self.popPassword = poppswd							# если имеет значение None, пароль будет запрошен позднее
		# print('MailFetcher.mailconfig:', mailconfig.__file__)

	def connect(self):
		self.trace('Connecting...')
		self.getPassword()									# файл, GUI или консоль
		if 'sslServerMode' in mailconfig.__dict__ and mailconfig.sslServerMode:
			server = poplib.POP3_SSL(self.popServer, timeout=15)
		else:
			server = poplib.POP3(self.popServer, timeout=15)
		server.user(self.popUser)							# соединиться, зарегистрироваться
		server.pass_(self.popPassword)						# pass  - зарезервированное слово
		self.trace(server.getwelcome())						# print выведет приветствие
		return server

	# использовать настройки из клиентского mailconfig, находящегося в пути
	# поиска; при необходимости можно изменить в классе или в экземплярах;
	fetchEncoding = mailconfig.fetchEncoding

	def decodeFullText(self, messageBytes):
		"""
		4E, Py3.1: декодирует полный текст сообщения, представленный в виде
		строки bytes, в строку Юникода str; выполняется на этапе получения
		для последующего отображения или анализа (после этого полный текст
		почтового сообщения всегда будет обрабатываться как строка Юникода);
		декодирование выполняется в соответствии с настройками в классе или
		в экземпляре или применяются наиболее распространенные кодировки;
		можно было бы также попробовать определить кодировку из заголовков
		или угадать ее, проанализировав структуру байтов; в Python 3.2/3.3
		этот этап может оказаться излишним: в этом случае измените метод
		так, чтобы он возвращал исходный список строк сообщения нетронутым;
		дополнительные подробности смотрите в главе 13;

		для большинства сообщений достаточно будет простой 8-битовой
		кодировки, такой как latin-1, потому что стандартной считается
		кодировка ASCII; этот метод применяется ко всему тексту сообщения -
		это лишь один из этапов на пути декодирования сообщений: содержимое
		и заголовки сообщений могут также находиться в формате MIME и быть
		закодированы в соответствии со стандартами электронной почты
		и Юникода; смотрите подробности в главе 13, а также реализацию
		модулей mailParser и mailSender;
		"""
		text = None
		kinds = [self.fetchEncoding]						# сначала настройки пользователя
		kinds += ['ascii', 'latin1', 'utf8']				# затем наиболее распространенные кодировки
		kinds += [sys.getdefaultencoding()]					# и по умолчанию (может отличаться)
		for kind in kinds:									# может вызывать ошибку при сохранении
			try:
				text = [line.decode(kind) for line in messageBytes]
				break
			except (UnicodeError, LookupError):				# LookupError - неверное имя
				pass
		# self.trace(kind)
		# self.trace('text encoded in mailFetcher.decodeFullText' if text else 'None')
		# self.trace(text)
		if text == None:
			# пытается вернуть заголовки + сообщение об ошибке, иначе
			# исключение может вызвать аварийное завершение клиента;
			# пытается декодировать заголовки как ascii,
			# с применением других кодировок или с помощью
			# кодировки по умолчанию для платформы;
			blankline = messageBytes.index(b'')
			hdrsonly = messageBytes[:blankline]
			commons = ['ascii', 'latin1', 'utf8']
			for common in commons:
				try:
					text = [line.decode(common) for line in hdrsonly]
					break
				except UnicodeError:
					pass
			else:														# не подошла ни одна кодировка
				try:
					text = [line.decode() for line in hdrsonly]		# по умолчанию?
				except UnicodeError:
					text = ['From: (sender of unknown Unicode format headers)']
			text += ['',
					 '--Sorry: mailtools cannot decode this mail content!--']
		return text

	def downloadMessage(self, msgnum):
		"""
		загружает полный текст одного сообщения по указанному относительному
		номеру POP msgnum; анализ содержимого выполняет вызывающая программа
		"""
		self.trace('load ' + str(msgnum))
		server = self.connect()
		try:
			resp, msglines, respsz = server.retr(msgnum)
		finally:
			server.quit()
		msglines = self.decodeFullText(msglines)						# декодировать bytes в str
		return '\n'.join(msglines)										# объединить строки

	def downloadAllHeaders(self, progress=None, loadfrom=1):
		"""
		получает только размеры и заголовки для всех или только
		для сообщений с номерами от loadfrom и выше;
		используйте loadfrom для загрузки только новых сообщений;
		для последующей загрузки полного текста сообщений
		используйте downloadMessage; progress - это функция,
		которая вызывается с параметрами (счетчик, всего);
		возвращает: [текст заголовков], [размеры сообщений],
		флаг "сообщения загружены полностью"

		4Е: добавлена проверка параметра mailconfig.fetchlimit для поддержки
		почтовых ящиков с большим количеством входящих сообщений: если он
		не равен None, извлекается только указанное число заголовков,
		вместо остальных возвращаются пустые заголовки; иначе пользователи,
		получающие большое количество сообщений, как я (4К сообщений),
		будут испытывать неудобства;
		4Е: передает loadfrom методу downloadMessages (чтобы хоть
			немного облегчить положение);
		"""
		self.trace(loadfrom)
		if not self.srvHasTop:											# не все серверы поддерживают команду TOP
			# загрузить полные сообщения
			return self.downloadAllMsgs(progress, loadfrom)
		else:
			self.trace('loading headers')
			fetchlimit = mailconfig.fetchlimit
			server = self.connect()										# ящик теперь заблокирован до вызова метода quit
			try:
				resp, msginfos, respsz = server.list()					# список строк 'номер размер'
				msgCount = len(msginfos)								# альтернатива методу srvr.stat()
				msginfos = msginfos[loadfrom-1:]						# отбросить уже загруженные
				allsizes = [int(x.split()[1]) for x in msginfos]
				allhdrs = []
				for msgnum in range(loadfrom, msgCount+1):				# возможно пустой
					if progress: progress(msgnum, msgCount)				# вызвать progress
					if fetchlimit and (msgnum <= msgCount - fetchlimit):
						# пропустить, добавить пустой заголовок
						hdrtext = 'Subject: --mail skipped--\n\n'
						allhdrs.append(hdrtext)
					else:
						# получить, только заголовки
						resp, hdrlines, respsz = server.top(msgnum, 0)
						hdrlines = self.decodeFullText(hdrlines)
						allhdrs.append('\n'.join(hdrlines))
			finally:
				server.quit()											# разблокировать почтовый ящик
			self.trace(str(len(allsizes)) + ', ' + str(len(allhdrs)))
			assert len(allhdrs) == len(allsizes)
			self.trace('load headers exit')
			return allhdrs, allsizes, False

	def downloadAllMessages(self, progress=None, loadfrom=1):
		"""
		загрузить все сообщения целиком с номерами loadfrom..N,
		независимо от кэширования, которое может выполняться вызывающей
		программой; намного медленнее, чем downloadAllHeaders,
		если требуется загрузить только заголовки;

		4Е: поддержка mailconfig.fetchlimit: смотрите downloadAllHeaders;
		можно было бы использовать server.list() для получения размеров
		пропущенных сообщений, но клиентам скорее всего этого не требуется;
		"""
		self.trace('loading full messages')
		fetchlimit = mailconfig.fetchlimit
		server = self.connect()
		try:
			(msgCount, msgBytes) = server.stat()						# ящик на сервере
			allmsgs = []
			allsizes = []
			for i in range(loadfrom, msgCount+1):						# пусто, если low >= high
				if progress: progress(i, msgCount)
				if fetchlimit and (i <= msgCount - fetchlimit):
					# пропустить, добавить пустое сообщение
					mailtext = 'Subject: --mail skipped--\n\nMail skipped.\n'
					allmsgs.append(mailtext)
					allsizes.append(len(mailtext))
				else:
					# получить полные сообщения
					(resp, message, respsz) = server.retr(i)			# сохранить в списке
					message = self.decodeFullText(message)
					allmsgs.append('\n'.join(message))					# оставить на сервере
					allsizes.append(respsz)								# отличается от len(msg)
		finally:
			server.quit()												# разблокировать ящик
		assert len(allmsgs) == (msgCount - loadfrom) + 1
		# assert sum(allsizes) == msgBytes								# если не loadfrom > 1
		return allmsgs, allsizes, True

	def deleteMessages(self, msgnums, progress=None):
		"""
		удаляет несколько сообщений на сервере: предполагается, что номера
		сообщений в ящике не изменялись с момента последней
		синхронизации/загрузки; используется, если заголовки сообщения
		недоступны; выполняется быстро, но может быть опасен:
		смотрите deleteMessagesSafely
		"""
		self.trace('deleting mails')
		server = self.connect()
		try:															# не устанавливать
			for (ix, msgnum) in enumerate(msgnums):						# соединение для каждого
				if progress: progress(ix+1, len(msgnums))
				server.dele(msgnum)
		finally:														# номера изменились, перезагрузить
			server.quit()

	def deleteMessagesSafely(self, msgnums, synchHeaders, progress=None):
		"""
		удаляет несколько сообщений на сервере, но перед удалением выполняет
		проверку заголовка с помощью команды TOP; предполагает, что почтовый
		сервер поддерживает команду TOP протокола POP, иначе возбуждает
		исключение TopNotSupported - клиент может вызвать deleteMessages;

		используется, если почтовый ящик на сервере мог измениться с момента
		последней операции получения оглавления и соответственно могли
		имзениться номера POP-сообщений; это может произойти при удалении
		почты с помощью другого клиента; кроме того, некоторые провайдеры
		могут перемещать почту из ящика входящих сообщений в ящик
		недоставленных сообщений в случае ошибки во время загрузки;

		аргумент synchHeaders должен быть списком уже загруженных
		заголовков, соответствующих выбранным сообщениям
		(обязательная информация);
		возбуждает исключение, если обнаруживается рассинхронизация
		с почтовым сервером; доступ к входящей почте блокируется
		до вызова метода quit, поэтому номер не могут измениться
		между командой TOP и фактическим удалением: проверка синхронизации
		должна выполняться здесь, а не в вызывающей программе; может оказаться
		недостаточным вызвать checkSynchError + deleteMessages, но здесь
		проверяется каждое сообщение, на случай удаления или вставки
		сообщений в середину почтового ящика;
		"""
		if not self.srvHasTop:
			raise TopNotSupported('Safe delete cancelled')

		self.trace('deleting mails safely')
		errmsg = 'Message %s out of synch with server.\n'
		errmsg += 'Delete terminated at this message.\n'
		errmsg += 'Mail client may require restart or reload.'

		server = self.connect()								# блокирует ящик до quit
		try:												# не устанавливает соединение для каждого
			(msgCount, msgBytes) = server.stat()			# объем входящей почты
			for (ix, msgnum) in enumerate(msgnums):
				if msgnum > msgCount:						# сообщения были удалены
					raise DeleteSynchError(errmsg % msgnum)
				resp, hdrlines, respsz = server.top(msgnum, 0)		# только заголовки
				hdrlines = self.decodeFullText(hdrlines)
				msghdrs = '\n'.join(hdrlines)
				if not self.headersMatch(msghdrs, synchHeaders[msgnum-1]):
					raise DeleteSynchError(errmsg % msgnum)
				else:
					server.dele(msgnum)						# безопасно удалить это сообщение
		finally:											# номера изменились: перезагрузить
			server.quit()									# разблокировать при выходе

	def checkSynchError(self, synchHeaders):
		"""
		сопоставляет уже загруженные заголовки в списке synchHeaders с теми,
		что находятся на сервере, с использованием команды TOP
		протокола POP, извлекающей текст заголовков;
		используется, если содержимое почтового ящика могло измениться,
		например в результате удаления сообщений с помощью другого клиента
		или в результате автоматических действий, выполняемых
		почтовым сервером; возбуждает исключение в случае обнаружения
		рассинхронизации или ошибки во время взаимодействия с сервером;

		для повышения скорости проверяется только последний в последнем:
		это позволяет обнаружить факт удаления из ящика, но предполагает,
		что сервер не мог вставить новые сообщения перед последним (верно
		для входящих сообщений); сначала проверяется объем входящей почты:
		если меньше - были только удаления; иначе, если сообщения удалялись
		и в конец добавлялись новые, результат top будет отличаться;
		результат этого метода можно считать действительным только на момент
		его работы: содержимое ящика входящих сообщений может
		измениться после возврата;
		"""
		self.trace('synch check')
		errormsg = 'Message index out of synch with mail server.\n'
		errormsg += 'Mail client may require restart or reload.'
		server = self.connect()
		try:
			lastmsgnum = len(synchHeaders)						# 1..N
			(msgCount, msgBytes) = server.stat()				# объем входящей почты
			if lastmsgnum > msgCount:							# теперь меньше
				raise MessageSynchError(errormsg)				# нечего сравнивать
			if self.srvHasTop:
				resp, hdrlines, respsz = server.top(lastmsgnum, 0)		# только заголовки
				hdrlines = self.decodeFullText(hdrlines)
				lastmsghdrs = '\n'.join(hdrlines)
				if not self.headersMatch(lastmsghdrs, synchHeaders[-1]):
					raise MessageSynchError(errormsg)
		finally:
			server.quit()

	def headersMatch(self, hdrtext1, hdrtext2):
		"""
		для сопоставления недостаточно простого сравнения строк: некоторые
		серверы добавляют заголовок "Status:", который изменяется с течением
		времени; у одного провайдера он устанавливался изначально
		как "Status: U" (unread - непрочитанное) и заменялся на "Status: RO"
		(read, old - прочитано, старое) после загрузки сообщения -
		это сбивает с толку механизм проверки синхронизации,
		если после загрузки нового оглавления, но непосредственно
		перед удалением или проверкой последнего сообщения клиентом
		было загружено новое сообщение;
		теоретически значение заголовка "Message-id:" является уникальным
		для сообщения, но сам заголовк является необязательным и может
		быть подделан; сначала делается попытка выполнить типичное
		сопоставление; анализ - дорогостоящая операция, поэтому
		выполняется последним
		"""
		# попробовать сравнить строки
		if hdrtext1 == hdrtext2:
			self.trace('Same headers text')
			return True

		# попробовать сопоставить без заголовков Status
		split1 = hdrtext1.splitlines()								# s.split('\n), но без последнего
		split2 = hdrtext2.splitlines()								# элемента пустой строки ('')
		strip1 = [line for line in split1 if not line.startswith('Status:')]
		strip2 = [line for line in split2 if not line.startswith('Status:')]
		if strip1 == strip2:
			self.trace('Same without Status')
			return True

		# попробовать найти несовпадения заголовков Message-id, если они имеются
		msgid1 = [line for line in split1 if line[:11].lower() == 'message-id']
		msgid2 = [line for line in split2 if line[:11].lower() == 'message-id']
		if (msgid1 or msgid2) and (msgid1 != msgid2):
			self.trace('Different Message-Id')
			return False

		# выполнить полный анализ заголовков и сравнить наиболее типичные из них,
		# если заголовки message-id отсутствуют или в них были найдены различия
		tryheaders = ('From', 'To', 'Subject', 'Date')
		tryheaders += ('Cc', 'Return-Path', 'Received')
		msg1 = MailParser().parseHeaders(hdrtext1)
		msg2 = MailParser().parseHeaders(hdrtext2)
		for hdr in tryheaders:										# возможно несколько адресов в Received
			if msg1.get_all(hdr) != msg2.get_all(hdr):				# без учета регистра,
				self.trace('Diff common headers')					# по умолчанию None
				return False

		# все обычные заголовки совпадают и нет отличающихся message-id
		self.trace('Same common headers')
		return True

	def getPassword(self):
		"""
		получает пароль POP, если он еще не известен
		не требуется до обращения к серверу из файла
		на стороне клиента или вызовом метода подкласса
		"""
		if not self.popPassword:
			try:
				localfile = open(mailconfig.poppasswdfile)
				self.popPassword = localfile.readline()[:-1]
				self.trace('local file password' + repr(self.popPassword))
			except:
				self.popPassword = self.askPopPassword()

	def askPopPassword(self):
		assert False, 'Subclass must define method'

# ---------------------------------------------------------------------------- #
#                         специализированные подклассы                         #
# ---------------------------------------------------------------------------- #

# ANCHOR class MailFetcherConsole
class MailFetcherConsole(MailFetcher):
	def askPopPassword(self):
		import getpass
		prompt = 'Password for %s on %s?' % (self.popUser, self.popServer)
		return getpass.getpass(prompt)

# ANCHOR SilentMailFetcher
class SilentMailFetcher(SilentMailTool, MailFetcher):
	pass														# отключает трассировку
