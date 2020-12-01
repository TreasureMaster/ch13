#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Класс MailSender.
# Проблемы поддержки Юникода при работе с вложениями, заголовками и при сохранении файлов.
# Пример 13.23 (Лутц Т2 стр.254)
"""
# ---------------------------------------------------------------------------- #
отправляет сообщения, добавляет вложения (описание и текст приводятся
в модуле __init__)
# ---------------------------------------------------------------------------- #
"""

# клиентские настройки (переменная localserver определяет какой модуль будет загружен -
# с локальными или удаленными настройками конфигурации)
# localserver = False
# mailconfig = __import__('maillocal') if localserver else __import__('myconfig')
from resolvingConfig import mailconfig

import smtplib, os, mimetypes									# mime: имя в тип
import email.utils, email.encoders								# строка с датой, base64
from .mailTool import MailTool, SilentMailTool					# 4E: относительно пакета

from email.message          import Message						# объект сообщения, obj->text
from email.mime.multipart   import MIMEMultipart				# специализированные объекты
from email.mime.audio       import MIMEAudio					# вложений с поддержкой форматирования/кодирования
from email.mime.image       import MIMEImage
from email.mime.text        import MIMEText
from email.mime.base        import MIMEBase
from email.mime.application import MIMEApplication				# 4E: использовать новый класс приложения

def fix_encode_base64(msgobj):
	"""
	4E: реализация обходного решения для ошибки в пакете email в Python 3.1,
	препятствующей созданию полного текста сообщения с двоичными частями,
	преобразованными в формат base64 или другой формат электронной почты;
	функция email.encode, вызываемая конструктором, оставляет содержимое
	в виде строки bytes, даже при том, что оно находится в текстовом формате
	base64; это препятствует работе механизма создания полного текста
	сообщения, который предполагает получить текстовые данные и поэтому
	требует, чтобы они имели тип str; в результате этого с помощью пакета
	email в Py3.1 можно создавать только простейшие текстовые части
	сообщений - любая двоичная часть в формате MIME будет вызывать
	ошибку на этапе создания полного текста сообщения; есть сведения,
	что эта ошибка будет устранена в будущих версиях Python и пакета email,
	в этом случае данная функция не должна выполнять никаких действий;
	подробности смотрите в главе 13;
	"""
	linelen = 75									# согласно стандарту MIME
	from email.encoders import encode_base64

	encode_base64(msgobj)							# что обычно делает email: оставляет bytes
	text = msgobj.get_payload()						# bytes вызывает ошибку в email при создании текста
	if isinstance(text, bytes):						# содержимое - bytes в 3.1, str - в 3.2
		text = text.decode('ascii')					# декодировать в str, чтобы сгенерировать текст

	lines = []										# разбить на строки, иначе 1 большая строка
	text = text.replace('\n', '')					# в 3.1 нет \n, но что будет потом
	while text:
		line, text = text[:linelen], text[linelen:]
		lines.append(line)
	msgobj.set_payload('\n'.join(lines))

def fix_text_required(encodingname):
	"""
	4E: обходное решение для ошибки, вызываемой смешиванием str/bytes
	в пакете email; в Python 3.1 класс MIMEText требует передавать
	ему строки разных типов для текста в разных кодировках,
	что обусловлено преобразованием некоторых типов текста
	в разные форматы MIME; смотрите главу 13;
	единственная альтернатива - использовать обобщенный класс Message
	и повторить большую часть программного кода;
	"""
	from email.charset import Charset, BASE64, QP

	charset = Charset(encodingname)					# так email отправляет,

	bodyenc = charset.body_encoding					# что делать для кодировки utf8 и др., требует данные типа bytes
	return bodyenc in (None, QP)					# ascii, latin1 и др. требует данные типа str

# ANCHOR MailSender class
class MailSender(MailTool):
	"""
	отправляет сообщение: формирует сообщение, соединяется с SMTP-сервером;
	работает на любых компьютерах с Python+Интернет, не использует клиента
	командной строки; не выполняет аутентификацию: смотрите MailSenderAuth,
	если требуется аутентификация;
	4Е: tracesize - количество символов в трассировочном сообщении: 0 = нет,
		большое значение = все;
	4Е: поддерживает кодирование Юникода для основного текста и текстовых частей;
	4Е: поддерживает кодирование заголовков - и полных, и компонента имени в адресах;
	"""
	def __init__(self, smtpserver=None, tracesize=256):
		self.smtpServerName = smtpserver or mailconfig.smtpservername
		self.tracesize = tracesize
		# print('MailSender.mailconfig:', mailconfig.__file__)

	def sendMessage(self, From, To, Subj, extrahdrs, bodytext, attaches,
								saveMailSeparator = (('=' * 80) + 'PY\n'),
								bodytextEncoding = 'us-ascii',
								attachesEncodings = None):
		"""
		формирует и отправляет сообщение: блокирует вызывающую программу,
		в графических интерфейсах следует вызывать в отдельном потоке выполнения;
		IN: bodytext - основной текст,
		IN: attaches - список имен файлов,
		IN: extrahdrs - список кортежей (имя, значение) добавляемых заголовков;
		возбуждает исключение, если отправка не удалась по каким-либо причинам;
		в случае успеха сохраняет отправленное сообщение в локальный файл;
		предполагается, что значения для заголовков To, Cc, Bcc являются списками
		из 1 или более уже декодированных адресов (возможно, в полном формате
		имя + <адрес>); клиент должен сам выполнять анализ, чтобы разбить их
		по разделителям или использовать многострочный ввод;
		обратите внимание, что SMTP допускает использование полного формата
		имя+<адрес> в адресе получателя;
		4Е: адреса Bcc теперь используются для отправки, а заголовок отбрасывается;
		4Е: повторяющиеся адреса получателей отбрасываются, иначе они будут
			получить несколько копий письма;
		предупреждение: не поддерживаются сообщения multipart/alternative,
						только /mixed;
		"""
		# 4E: предполагается, что основной текст уже в требуемой кодировке;
		# клиенты могут декодировать, используя кодировку по выбору
		# пользователя, по умолчанию или utf8;
		# так или иначе, email требует передать либо str, либо bytes;
		if fix_text_required(bodytextEncoding):
			if not isinstance(bodytext, str):
				bodytext = bodytext.decode(bodytextEncoding)
		else:
			if not isinstance(bodytext, bytes):
				bodytext = bodytext.encode(bodytextEncoding)

		# создать корень сообщения
		if not attaches:
			msg = Message()
			msg.set_payload(bodytext, charset=bodytextEncoding)
		else:
			msg = MIMEMultipart()
			self.addAttachments(msg, bodytext, attaches, bodytextEncoding, attachesEncodings)

		# 4E: не-ASCII заголовки кодируются; кодировать только имена
		# в адресах, иначе smtp может отвергнуть сообщение;
		# кодирует все имена в аргументе То (но не адреса),
		# предполагается, что это допустимо для сервера;
		# msg.as_string() сохраняет все разрывы строк,
		# добавленные при кодировании заголовков;

		hdrenc = mailconfig.headersEncodeTo or 'utf-8'					# по умолчанию utf8
		Subj   = self.encodeHeader(Subj, hdrenc)						# полный заголовок
		From   = self.encodeAddrHeader(From, hdrenc)					# имена в адресах
		To     = [self.encodeAddrHeader(T, hdrenc) for T in To]			# каждый адрес
		Tos    = ', '.join(To)											# заголовок + аргумент

		# добавить заголовки в корень сообщения
		msg['From']    = From
		msg['To']      = Tos											# возможно несколько: список адресов
		msg['Subject'] = Subj											# серверы отвергают разделитель ';'
		msg['Date']    = email.utils.formatdate()						# дата+время, rfc2822 utc
		recip          = To
		for name, value in extrahdrs:									# Cc, Bcc, X-Mailer и др.
			if value:
				if name.lower() not in ['cc', 'bcc']:
					value = self.encodeHeader(value, hdrenc)
					msg[name] = value
				else:
					value = [self.encodeAddrHeader(V, hdrenc) for V in value]
					recip += value										# некоторые серверы отвергают ['']
					if name.lower() != 'bcc':							# 4E: bcc получает почту, без заголовка
						msg[name] = ', '.join(value)					# добавить запятые между сс

		recip = list(set(recip))										# 4E: удалить дубликаты
		fullText = msg.as_string()										# сформировать сообщение

		# вызов sendmail возбудит исключение, если все адреса Tos ошибочны,
		# или вернет словарь с ошибочными адресами Tos
		self.trace('Sending to...' + str(recip))
		# self.trace(fullText[:self.tracesize])							# вызов SMTP для соединения

		if 'sslServerMode' in mailconfig.__dict__ and mailconfig.sslServerMode:
			server = smtplib.SMTP_SSL(self.smtpServerName, timeout=15)			# также может дать ошибку
		else:
			server = smtplib.SMTP(self.smtpServerName, timeout=15)			# также может дать ошибку
		self.trace('После соединения...')
		self.getPassword()												# если сервер требует
		self.authenticateServer(server)									# регистрация в подклассе
		try:
			failed = server.sendmail(From, recip, fullText)				# исключение или словарь
		except:
			server.close()												# 4E: завершение может подвесить!
			raise														# повторно возбудить исключение
		else:
			server.quit()												# соединение+отправка, успех
		self.saveSentMessage(fullText, saveMailSeparator)				# 4E: в первую очередь

		if failed:
			class SomeAddrsFailed(Exception): pass
			raise SomeAddrsFailed('Failed addrs:%s\n' % failed)
		self.trace('Send exit')

	def addAttachments(self, mainmsg, bodytext, attaches, bodytextEncoding, attachesEncodings):
		"""
		формирует сообщение, состоящее из нескольких частей, добавляя
		вложения attachments; использует для текста указанную кодировку
		Юникода, если была передача;
		"""
		# добавить главную часть text/plain
		msg = MIMEText(bodytext, _charset=bodytextEncoding)
		mainmsg.attach(msg)

		# добавить части с вложениями
		# encodings = attachesEncodings or (['us-ascii'] * len(attaches))
		encodings = attachesEncodings or (['utf-8'] * len(attaches))
		self.trace('addAttachments:' + str(attaches) + str(encodings))
		for (filename, fileencode) in zip(attaches, encodings):

			# имя файла может содержать абсолютный или относительный путь
			if not os.path.isfile(filename):							# пропустить каталоги и пр.
				continue

			# определить тип содержимого по расширению имени файла, игнорировать кодировку
			contype, encoding = mimetypes.guess_type(filename)
			if contype is None or encoding is not None:					# не определно или сжат?
				contype = 'application/octet-stream'					# универсальный тип
			self.trace('Adding ' + contype)

			# сконструировать вложенный объект Message соответствующего типа
			maintype, subtype = contype.split('/', 1)					# REVIEW разбить строку по первому символу '/'
			if maintype == 'text':										# 4E: текст требует кодирования
				if fix_text_required(fileencode):						# требуется str или bytes
					data = open(filename, 'r', encoding=fileencode)
				else:
					data = open(filename, 'rb')
				msg = MIMEText(data.read(), _subtype=subtype, _charset=fileencode)
				data.close()

			elif maintype == 'image':
				data = open(filename, 'rb')								# 4E: обходной прием для двоичных
				msg = MIMEImage(data.read(), _subtype=subtype, _encoder=fix_encode_base64)
				data.close()

			elif maintype == 'audio':
				data = open(filename, 'rb')
				msg = MIMEAudio(data.read(), _subtype=subtype, _encoder=fix_encode_base64)
				data.close()

			elif maintype == 'application':
				data = open(filename, 'rb')
				msg = MIMEApplication(data.read(), _subtype=subtype, _encoder=fix_encode_base64)
				data.close()

			else:
				data = open(filename, 'rb')								# тип application/* мог бы обрабатываться здесь
				msg = MIMEBase(maintype, subtype)
				msg.set_payload(data.read())
				data.close()											# создание универсального типа
				fix_encode_base64(msg)									# также было нарушено!
				# email.encoders.encode_base64(msg)						# преобразовать в base64

			# установить имя файла и присоединить к контейнеру
			basename = os.path.basename(filename)
			msg.add_header('Content-Disposition', 'attachment', filename=basename)
			mainmsg.attach(msg)

		# текст за пределами структуры mime, виден клиентам,
		# которые не могут декодировать формат MIME
		mainmsg.preamble = 'A multi-part MIME format message.\n'
		mainmsg.epilogue = ''											# гарантировать завершение сообщения переводом строки

	def saveSentMessage(self, fullText, saveMailSeparator):
		"""
		добавляет отправленное сообщение в конец локального файла,
		если письмо было отправлено хотя бы одному адресату;
		клиент: определяет строку-разделитель, используемую приложением;
		предупреждение: пользователь может изменить файл во время работы
						сценария (маловероятно)
		"""
		try:
			sentfile = open(mailconfig.sentmailfile, 'a', encoding=mailconfig.fetchEncoding)
			if fullText[-1] != '\n': fullText += '\n'
			sentfile.write(saveMailSeparator)
			sentfile.write(fullText)
			sentfile.close()
		except:
			self.trace('Could not save sent message')					# не прекращает работу сценария

	def encodeHeader(self, headertext, unicodeencoding='utf-8'):
		"""
		4E: кодирует содержимое заголовков с символами не из даипазона ASCII
		в соответствии со стандартами электронной почты и Юникода, применяя
		кодировку пользователя или UTF-8; метод header.encode автоматически
		добавляет разрывы строк, если необходимо;
		"""
		try:
			headertext.encode('ascii')
		except:
			try:
				hdrobj = email.header.make_header([(headertext, unicodeencoding)])
				headertext = hdrobj.encode()
			except:
				pass													# автоматически разбивает на несколько строк
		return headertext												# smtplib может потерпеть неудачу, если не будет
																		# закодировано в ascii

	def encodeAddrHeader(self, headertext, unicodeencoding='utf-8'):
		"""
		4E: пытается закодировать имена в адресах электронной почты
		с символами не из диапазона ASCII в соответствии со стандартами
		электронной почты, MIME и Юникода; если терпит неудачу, компонент
		имени отбрасывается и используется только часть с фактическим адресом;
		если не может получить даже адрес, пытается декодировать целиком,
		иначе smtplib может столкнуться с ошибками, когда попытается
		закодировать все почтовое сообщение как ASCII; в большинстве случаев
		кодировки utf-8 вполне достаточно, так как она предусматривает
		довольно широкое разнообразие кодовых пунктов;

		вставляет символы перевода строки, если строка заголовка слишком
		длинная, иначе метод hdr.encode разобьет имена на несколько строк,
		но он может не замечать некоторые строки, длиннее максимального
		значения (улучшите меня); в данном случае метод Message.as_string
		форматирования не будет пытаться разбивать строки;
		смотрите также метод decodeAddrHeader в модуле mailParser,
		реализующий обратную операцию;
		"""
		try:
			pairs = email.utils.getaddresses([headertext])				# разбить на части
			encoded = []
			for name, addr in pairs:
				try:
					name.encode('ascii')								# использовать как есть, если ascii
				except UnicodeError:									# иначе закодировать компонент имени
					try:
						uni = name.encode(unicodeencoding)
						hdr = email.header.make_header([uni, unicodeencoding])
						name = hdr.encode()
					except:
						name = None										# отбросить имя, использовать только адрес
				joined = email.utils.formataddr((name, addr))			# заключить имя в кавычки, если необходимо
				encoded.append(joined)

			fullhdr = ', '.join(encoded)
			if len(fullhdr) > 72 or '\n' in fullhdr:					# не одна короткая строка?
				fullhdr = ',\n'.join(encoded)							# попробовать несколько строк
			
			return fullhdr
		except:
			return self.encodeHeader(headertext)

	def authenticateServer(self, server):
		pass															# этот класс/сервер не предусматривает аутентификацию

	def getPassword(self):
		self.trace('---mailSender.getPassword:')
		pass															# этот класс/сервер не предусматривает аутентификацию

# ---------------------------------------------------------------------------- #
#                         специализированные подклассы                         #
# ---------------------------------------------------------------------------- #

# ANCHOR MailSenderAuth class
class MailSenderAuth(MailSender):
	"""
	используется для работы с серверами, требующими аутентификацию;
	клиент: выбирает суперкласс MailSender или MailSenderAuth, опираясь
	на параметр mailconfig.smtpuser (None?)
	"""
	smtpPassword = None													# 4E: в классе, не в self, совместно используется
																		# всеми экземплярами
	def __init__(self, smtpserver=None, smtpuser=None, tracesize=256):
		MailSender.__init__(self, smtpserver, tracesize)
		self.smtpUser = smtpuser or mailconfig.smtpuser
		# self.smtpPassword = None										# 4E: заставит PyMailGUI запрашивать
																		# пароль при каждой операции отправки!
	def authenticateServer(self, server):
		server.login(self.smtpUser, self.smtpPassword)

	def getPassword(self):
		"""
		get получает пароль для аутентификации на сервере SMTP, если он еще
		не известен; может вызываться суперклассом автоматически или
		клиентом вручную: не требуется до момента отправки, но не следует
		вызывать из потока выполнения графического интерфейса; пароль
		извлекается из файла на стороне клиента или методом подкласса
		"""
		if not self.smtpPassword:
			try:
				localfile = open(mailconfig.smtppasswdfile)
				MailSenderAuth.smtpPassword = localfile.readline()[:-1]
				self.trace('local file password' + repr(self.smtpPassword))
			except:
				MailSenderAuth.smtpPassword = self.askSmtpPassword()

	def askSmtpPassword(self):
		assert False, 'Subclass must be define method'

# ANCHOR MailSenderAuthConsole class
class MailSenderAuthConsole(MailSenderAuth):
	def askSmtpPassword(self):
		import getpass
		prompt = 'Password for %s on %s?' % (self.smtpUser, self.smtpServerName)
		return getpass.getpass(prompt)

# ANCHOR SilentMailSender class
class SilentMailSender(SilentMailTool, MailSender):
	pass																# отключает трассировку
