#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Класс MailParser.
# Декодирование Юникода для текстового содержимого частей и заголовков.
# Пример 13.25 (Лутц Т2 стр.275)
"""
# ---------------------------------------------------------------------------- #
разбор и извлечение, анализ, сохранение вложения (описание и тест
приводятся в модуле __init__)
# ---------------------------------------------------------------------------- #
"""

import os, mimetypes, sys									# mime: отображение типа в имя
import email.parser											# анализ текста в объекте Message
import email.header											# 4E: кодирование/декодирование заголовков
import email.utils											# 4E: кодирование/декодирование заголовков с адресами

from email.message import Message							# обход объектов Message
from .mailTool import MailTool								# 4E: относительно пакета

class MailParser(MailTool):
	"""
	методы анализа текста сообщения, вложений

	важное замечание: содержимое объекта Message может быть простой строкой
	в простых несоставных сообщениях или списком объектов Message
	в сообщениях, состоящих из нескольких частей (возможно, вложенных);
	мы не будем различать эти два случая, потому что генератор walk
	объекта Message всегда первым возвращает сам объект и прекрасно
	обрабатывает простые, несоставные объекты
	(выполняется обход единственного объекта);

	в случае простых сообщений тело сообщения всегда рассматривается здесь
	как единственная часть сообщения; в случае составных сообщений список
	частей включает основной текст сообщения, а также все вложения;
	это позволяет обрабатывать в графических интерфейсах простые нетекстовые
	сообщения как вложения (например, сохранять, открывать);
	иногда, в редких случаях, содержимым частей объекта Message
	может быть None;

	4E примечание: в Py 3.1 содержимое текстовых частей возвращается в виде
	строки bytes, когда передается аргумент decode=1, в других случаях может
	возвращаться строка str; в модуле mailtools текст хранится в виде строки
	bytes, чтобы упростить сохранение в файлах, но основное текстовое
	содержимое декодируется в строку str в соответствии с информацией
	в заголовках или с применением кодировки по умолчанию + предполагаемой;
	при необходимости клиенты должны сами декодировать остальные части:
	для декодирования частей, сохраненных в двоичных файлах, PyMailGUI
	использует информацию в заголовках;

	4Е: добавлена поддержка автоматического декодирования заголовков
	сообщения в соответствии с их содержимым - как полных заголовков,
	таких как Subject, так и компонентов имен в заголовках с адресами,
	таких как From и To;
	клиент должен запрашивать эту операцию после анализа полного текста
	сообщения, перед отображением: механизм анализа не выполняет декодирование;
	"""

	def walkNamedParts(self, message):
		"""
		функция-генератор, позволяющая избежать повторения логики выбора
		именованных частей; пропускает заголовки multipart, извлекает
		имена файлов частей; message - это уже созданный из сообщения
		объект email.message.Message; не пропускает части необычного типа:
		содержимым может быть None, при сохранении следует обрабатывать
		такую возможность; некоторые части некоторых других типов также
		может потребоваться пропустить;
		"""
		for (ix, part) in enumerate(message.walk()):					# walk включает сообщение
			fulltype = part.get_content_type()							# ix включает пропущенные части
			maintype = part.get_content_maintype()
			if maintype == 'multipart':									# multipart/* контейнер
				continue
			elif fulltype == 'message/rfc822':							# 4E: пропустить message/rfc822
				continue												# пропустить все message/* ?
			else:
				filename, contype = self.partName(part, ix)
				yield (filename, contype, part)

	def partName(self, part, ix):
		"""
		извлекает имя файла и тип содержимого из части сообщения;
		имя файла: сначала пытается определить из параметра
		filename заголовка Content-Disposition, затем из параметра name
		заголовка Content-Type и под конец генерирует имя файла из типа,
		определяемого с помощью модуля mimetypes;
		"""
		filename = part.get_filename()									# имя файла в заголовке
		contype = part.get_content_type()								# тип/подтип, в нижнем регистре
		if not filename:
			filename = part.get_param('name')							# проверить параметр name
		if not filename:												# заголовка content-type
			if contype == 'text/plain':									# расширение текстового файла
				ext = '.txt'											# иначе будет предложено .ksh
			else:
				ext = mimetypes.guess_extension(contype)
				if not ext: ext = '.bin'								# универсальное по умолчанию
			filename = 'part-%03d%s' % (ix, ext)
		return (filename, contype)

	def saveParts(self, savedir, message):
		"""
		сохраняет все части сообщения в файлах в локальном каталоге;
		возвращает список [('тип/подтип', 'имя файла')] для использования
		в вызывающей программе, но не открывает какие-либо части или
		вложения; метод get_payload декодирует содержимое с применением
		кодировок base64, quoted-printable, uuencoded: механизм анализа
		почтовых сообщений может вернуть содержимое None для некоторых
		необычных типов частей, которые, вероятно, следует пропустить:
		здесь преобразовать в str для безопасности;
		"""
		if not os.path.exists(savedir):
			os.mkdir(savedir)
		partfiles = []
		for (filename, contype, part) in self.walkNamedParts(message):
			fullname = os.path.join(savedir, filename)
			fileobj = open(fullname, 'wb')								# двоичный режим
			content = part.get_payload(decode=1)						# декодирует base64, qp, uu
			if not isinstance(content, bytes):							# 4E: bytes для rb
				content = b'(no content)'								# decode=1 возвращает bytes, но для некоторых типов None
			fileobj.write(content)										# 4E: не str(content)
			fileobj.close()
			partfiles.append((contype, fullname))						# для открытия в вызывающей программе
		return partfiles

	def saveOnePart(self, savedir, partname, message):
		"""
		то же самое, но отыскивает по имени только одну часть
		и сохраняет ее
		"""
		if not os.path.exists(savedir):
			os.mkdir(savedir)
		fullname = os.path.join(savedir, partname)
		(contype, content) = self.findOnePart(partname, message)
		if not isinstance(content, bytes):
			content = b'(no content)'
		open(fullname, 'wb').write(content)
		return (contype, fullname)

	def partsList(self, message):
		"""
		возвращает список имен файлов для всех частей уже
		проанализированного сообщения, используется та же логика определения
		имени файла, что и в saveParts, но не сохраняет части в файлы
		"""
		validParts = self.walkNamedParts(message)
		return [filename for (filename, contype, part) in validParts]

	def findOnePart(self, partname, message):
		"""
		отыскивает и возвращает содержимое части по его имени;
		предназначен для совместного использования с методом partsList;
		можно было бы также использовать mimetypes.guess_type(partname);
		необходимости поиска можно было бы избежать, сохраняя данные в словаре;
		4Е: содержимое может иметь тип str или bytes - преобразовать при необходимости;
		"""
		for (filename, contype, part) in self.walkNamedParts(message):
			if filename == partname:
				content = part.get_payload(decode=1)					# декодирует base64, qp, uu
				return (contype, content)								# может быть текст в двоичном виде

	def decodedPayload(self, part, asStr=True):
		"""
		4Е: декодирует текстовую часть, представленную в виде
		строки bytes, в строку str Юникода для отображения,
		разбиения на строки и так далее;
		IN: part - аргумент, объект Message; (decode=1) декодирует
		из формата MIME (base64, uuencode, qp), bytes.decode() выполняет
		дополнительное декодирование в текстовые строки Юникода;
		прежде чем вернуть строку с ошибкой, сначала пытается применить
		кодировку, указанную в заголовках сообщения (если имеется
		и соответствует), затем пытается применить кодировку по умолчанию
		для текущей платформы и несколько предполагаемых кодировок;
		"""
		payload = part.get_payload(decode=1)							# может быть строка bytes
		if asStr and isinstance(payload, bytes):						# decode=1 возвращает bytes
			tries = []
			enchdr = part.get_content_charset()							# сначала проверить заголовки сообщения
			if enchdr:
				tries += [enchdr]
			tries += [sys.getdefaultencoding()]							# то же, что и bytes.decode()
			tries += ['latin1', 'utf8']									# попробовать 8-битные, включая ascii
			for trie in tries:											# попробовать utf8 (по умолчанию в Windows)
				try:
					payload = payload.decode(trie)						# подошла?
					break
				except (UnicodeError, LookupError):						# Lookup: недопустимое имя
					pass
			else:
				payload = '--Sorry: cannot decode Unicode text--'
		return payload

	def findMainText(self, message, asStr=True):
		"""
		для текстовых клиентов возвращает первую текстовую часть в виде str;
		в содержимом простого сообщения или во всех частях составного
		сообщения отыскивает часть типа text/plain, затем text/html, затем
		text/*, после чего принимается решение об отсутствии текстовой
		части, пригодной для отображения; это эвристическое решение,
		но оно охватывает простые, а также multipart/alternative
		и multipart/mixed сообщения;
		если это не простое сообщение, текстовая часть по умолчанию имеет
		заголовок content-type со значением text/plain;

		обрабатывает вложенные сообщения, выполняя обход, начиная с верхнего
		уровня, вместо сканирования списка; если это не составное сообщение,
		но имеет тип text/html, возвращает разметку HTML как текст типа HTML:
		вызывающая программа может открыть его в браузере, извлечь простой
		текст и так далее; если это простое сообщение и текстовая часть
		не найдена, следовательно, нет текста для отображения: предусмотрите
		сохранение/открытие содержимого в графическом интерфейсе;
		предупреждение: не пытайтесь объединить несколько встроенных
		частей типа text/plain, если они имеются;
		4Е: текстовое содержимое может иметь тип bytes - декодирует в str здесь;
		4Е: передайте asStr=False, чтобы получить разметку HTML в двоичном
			представлении для сохранения в файл;
		"""
		# отыскать простой текст
		for part in message.walk():								# walk выполнит обход всех частей
			ctype = part.get_content_type()						# если не составное
			if ctype == 'text/plain':							# может иметь формат base64, qp, uu
				return ctype, self.decodedPayload(part, asStr)	# bytes в str?

		# отыскать часть с разметкой HTML
		for part in message.walk():
			ctype = part.get_content_type()						# HTML отображается вызывающей функцией
			if ctype == 'text/html':
				return ctype, self.decodedPayload(part, asStr)

		# отыскать части любого другого текстового типа, включая XML
		for part in message.walk():
			if part.get_content_maintype() == 'text':
				return part.get_content_type, self.decodedPayload(part, asStr)

		# не найдено: можно было бы использовать первую часть,
		# но она не помечена как текстовая
		failtext = '[No text to display]' if asStr else b'[No text to display]'
		return 'text/plain', failtext

	def decodeHeader(self, rawheader):
		"""
		4E: декодирует текст заголовка i18n в соответствии со стандартами
		электронной почты и Юникода и их содержимым; в случае ошибки
		при декодировании возвращает в первоначальном виде; клиент должен
		вызывать этот метод для подготовки заголовка к отображению: объект
		Message не декодируется;
		пример: '=?UTF-8?Q?Introducing=20Top=20Values=20..Savers?=';
		пример: 'Man where did you get that =?UTF-8?Q?assistant=3F?=';

		метод decode_header автоматически обрабатывает любые разрывы строк
		в заголовке, может возвращать несколько частей, если в заголовке
		имеется несколько подстрок, закодированных по-разному, и возвращает
		все части в виде списка строк bytes, если кодировки были найдены
		(недекодированные части возвращаются как закодированные
		в raw-unicode-escape, со значением enc=None), но возвращает
		единственную часть с enc=None, которая является строкой str,
		а не bytes в Py3.1, если весь заголовок оказался недекодированным
		(должен обрабатывать смешанные типы);
		дополнительные подробности/примеры смотрите в главе 13;

		следующей реализации было бы достаточно, если бы не возможность
		появления подстрок, кодированных по-разному, или если бы
		в переменной enc не возвращалось значение None (возбуждает исключение,
		в результате которого аргумент rawheader возвращается в исходном виде):

		hdr, enc = email.header.decode_header(rawheader)[0]
		return hdr.decode(enc)
		# ошибка, если enc=None: нет имени кодировки или кодированных подстрок
		"""
		try:
			parts = email.header.decode_header(rawheader)
			# self.trace('---> mailParser.decodeHeader:')
			# self.trace(str(parts))
			decoded = []
			for (part, enc) in parts:								# для всех подстрок
				if enc == None:										# недекодированная часть?
					if not isinstance(part, bytes):					# str: недекодированный заголовок
						decoded += [part]							# иначе декодированный в Юникод
					else:
						decoded += [part.decode('raw-unicode-escape')]
				else:
					decoded += [part.decode(enc)]
			# self.trace('\t---> decoded Header:')
			# self.trace('\t' + ' '.join(decoded))
			return ' '.join(decoded)
		except:
			return rawheader										# вернуть как есть

	def decodeAddrHeader(self, rawheader):
		"""
		4E: декодирует заголовок i18n с адресами в соответствии
		со стандартами электронной почты и Юникод и их содержимым;
		должен анализировать первую часть адреса, чтобы получить
		интернационализированную часть:
		'"=?UTF-8?Q?Walmart?=" <newsletters@walmart.com>';
		заголовок From скорее всего будет содержать единственный адрес,
		но заголовки To, Cc, Bcc могут содержать несколько адресов;

		метод decodeHeader обрабатывает вложенные подстроки в разных
		кодировках внутри заголовка, но мы не можем напрямую вызвать
		его здесь для обработки всего заголовка, потому что он будет
		завершаться с ошибкой, если закодированная строка
		с именем будет заканчиваться кавычкой ", а не пробелом
		или концом строки; смотрите также метод encodeAddrHeader
		в модуле mailSender, реализующий обратную операцию;

		ниже приводится первая реализация, которая терпела неудачу
		при обработке некодированных подстрок в имени и возбуждала
		исключение при встрече некодированных частей типа bytes,
		если в адресе имеется хоть одна закодированная подстрока;

		namebytes, nameenc = email.header.decode_header(name)[0] (email+MIME)
		if nameenc: enc = namebytes.decode(nameenc)				 (Юникод?)
		"""
		try:
			pairs = email.utils.getaddresses([rawheader])		# разбить на части
			decoded = []										# учитывает запятые в именах
			for (name, addr) in pairs:
				try:
					name = self.decodeHeader(name)				# email + MIME + Юникод
				except:
					name = None									# использовать кодированное имя при возбуждении исключения в decodeHeader
				joined = email.utils.formataddr((name, addr))	# объединить
				decoded.append(joined)
			return ', '.join(decoded)							# более 1 адреса
		except:
			return self.decodeHeader(rawheader)					# попробовать декодироваь всю строку

	def splitAddresses(self, field):
		"""
		4E: используйте в графическом интерфейсе запятую как
		символ-разделитель адресов и функцию getadresses
		для корректного разбиения, которая позволяет использовать
		запятые в компонентах имен адресов;
		используется программой PyMailGUI для разбиения содержимого
		заголовков To, Cc, Bcc, обработки ввода пользователя и копий
		заголовков; возвращает пустой список, если аргумент field пуст
		или возникло какое-либо исключение;
		"""
		try:
			pairs = email.utils.getaddresses([field])					# [(имя, адрес)]
			# NOTE Используется коррекция адресов с ошибками (без угловых скобок или с одной скобкой)
			def checkaddr(pair):
				if pair[1].find(' ') != -1:
					ext, addr = pair[1].strip().rsplit(' ', 1)
					return (pair[0] + ext, addr)
				else:
					return pair
			pairs = map(checkaddr, pairs)
			# return [email.utils.formataddr(pair) for pair in pairs]		# [имя <адрес>]
			# NOTE если в базовой части адреса ничего нет, то это пустышка
			return [email.utils.formataddr(pair) for pair in pairs if pair[1]]		# [имя <адрес>]
		except:
			return ''						# синтаксическая ошибка в поле, введенном пользователем? и т.д.

	# возвращаются, когда анализ завершается неудачей
	errorMessage = Message()
	errorMessage.set_payload('[Unable to parse message - format error]')

	def parseHeaders(self, mailtext):
		"""
		анализирует только заголовки, возвращает корневой объект
		email.message.Message; останавливается сразу после анализа
		заголовков, даже если за ними ничего не следует (команда top);
		объект email.message.Message является отображением заголовков
		сообщения; в качестве содержимого объекта сообщения устанавливается
		значение None, а не необработанный текст тела
		"""
		try:
			return email.parser.Parser().parsestr(mailtext, headersonly=True)
		except:
			return self.errorMessage

	def parseMessage(self, fulltext):
		"""
		анализирует все сообщение, возвращает корневой объект
		email.message.Message; содержимым объекта сообщения является строка,
		если is_multipart() возвращает False; при наличии нескольких частей
		содержимым объекта сообщения является множество объектов Message;
		метод, используемый здесь, действует также, как функция
		email.message_from_string()
		"""
		try:												# может потерпеть неудачу
			return email.parser.Parser().parsestr(fulltext)
		except:
			return self.errorMessage						# в вызывающей программе? можно проверить возвращаемое значение

	def parseMessageRaw(self, fulltext):
		"""
		анализирует только заголовки, возвращает корневой объект
		email.message.Message; останавливается сразу после анализа
		заголовков для эффективности (здесь не используется);
		содержимым объекта сообщения является необработанный текст
		письма, следующий за заголовками
		"""
		try:
			return email.parser.HeaderParser().parsestr(fulltext)
		except:
			return self.errorMessage
