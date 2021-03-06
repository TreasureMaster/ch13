#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# POP: чтение электронной почты.
# Модуль настройки электронной почты.
# Пример 13.17 (Лутц Т2 стр.181)
"""
# ---------------------------------------------------------------------------- #
пользовательские параметры настройки для различных программ электронной почты
(версия pymail/mailtools); сценарии электронной почты получают имена серверов
и другие параметры настройки из этого модуля: измените его, чтобы он отражал
имена ваших серверов и ваши предпочтения;
# ---------------------------------------------------------------------------- #
"""
# ---------------------------------------------------------------------------- #
# (требуется для определения трассировки) От этой переменной зависит будет ли
# записываться лог в файл или консоль
# ---------------------------------------------------------------------------- #

selectLogging = True

# ---------------------------------------------------------------------------- #
# (обязательные параметры для соединения с сервером) - тип соединения SSL
# ---------------------------------------------------------------------------- #

sslServerMode = True

# ---------------------------------------------------------------------------- #
# (требуется для загрузки, удаления: для всех) имя сервера POP3,
# имя пользователя
# ---------------------------------------------------------------------------- #

popservername = 'pop.mail.ru'
popusername = 'am5x86p75@list.ru'

# ---------------------------------------------------------------------------- #
# (требуется для отправки: для всех) имя сервера SMTP
# смотрите модуль Python smtpd, где приводится класс сервера SMTP,
# выполняемого локально;
# ---------------------------------------------------------------------------- #

smtpservername = 'smtp.mail.ru'

# ---------------------------------------------------------------------------- #
# (необязательные параметры: для всех) персональная информация,
# используемая клиентами для заполнения полей в сообщениях,
# если эти параметры определены;
# подпись - может быть блоком в тройных кавычках, игнорируется,
# если пустая строка;
# адрес - используется в качестве начального значения поля "From",
# если непустая строка, больше не пытается определить начение
# поля From для ответов: это имело переменный успех;
# ---------------------------------------------------------------------------- #

myaddress = 'am5x86p75@list.ru'
mysignature = ('Thanks,\n -- Treasure Master (https://github.com/TreasureMaster)')

# ---------------------------------------------------------------------------- #
# (необязательные параметры: mailtools) могут потребоваться для отправки;
# имя пользователя/пароль SMTP, если требуется аутентификация;
# если аутентификация не требуется, установите переменную smtpuser
# в значение None или ''; в переменную smtppasswdfile запишите имя файла
# с паролем SMTP или пустую строку, чтобы вынудить программу
# запрашивать пароль (в консоли или в графическом инетрфейсе);
# ---------------------------------------------------------------------------- #

# smtpuser = None									# зависит от провайдера
smtpuser = 'am5x86p75@list.ru'
smtppasswdfile = ''								# установите значение в '', чтобы обеспечить запрос

# ---------------------------------------------------------------------------- #
# (обязательный параметр: mailtools) локальный файл, где некоторые клиенты
# сохраняют отправленные сообщения;
# ---------------------------------------------------------------------------- #

sentmailfile = r'.\sentmail.txt'				# '.' означает текущий рабочий каталог

# ---------------------------------------------------------------------------- #
# (обязательный параметр: pymail, pymail2) локальный файл, где pymail
# сохраняет почту по запросу;
# ---------------------------------------------------------------------------- #

savemailfile = r'c:\temp\savemail.txt'			# не используется в PyMailGUI: диалог

# ---------------------------------------------------------------------------- #
# (обязательные параметры: pymail, mailtools) fetchEncoding -
# это имя кодировки, используемой для декодирования байтов сообщения,
# а также для кодирования/декодирования текста сообщения, если они
# сохраняются в текстовых файлах; подробности смотрите в главе 13:
# это временное решение, пока не появится новый пакет email,
# с более дружественным отношением к строкам bytes;
# headersEncodeTo - для отправки заголовков: смотрите главу 13;
# ---------------------------------------------------------------------------- #

fetchEncoding = 'utf8'					# 4E: как декодировать и хранить текст сообщений (или latin1 ?)
headersEncodeTo = None					# 4E: как кодировать не-ASCII заголовки при отправке (None = utf8)

# ---------------------------------------------------------------------------- #
# (необязательный параметр: mailtools) максимальное количество заголовков
# или сообщений, загружаемых за один запрос; если указать значение N,
# mailtools будет извлекать не более N самых последних электронных писем;
# более старые сообщения, не попавшие в это число, не будут извлекаться
# с сервера, но будут возвращаться как пустые письма;
# если этой переменной присвоить значение None (или 0), будут загружаться
# все сообщения; используйте этот параметр, если вам может поступать
# очень большое количество писем, а ваше подключене к Интернету
# или сервер слишком медленные, чтобы можно было выполнить загрузку
# сразу всех сообщений; кроме того, некоторые клиенты загружают
# только самые свежие письма, но этот параметр никак не связан
# с данной особенностью;
# ---------------------------------------------------------------------------- #

fetchlimit = 25							# 4E: максимальное число загружаемых заголовков/сообщений
