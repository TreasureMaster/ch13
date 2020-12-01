#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Добавляем пользовательский интерфейс.
# Пример 13.8 (Лутц Т2 стр.142)
"""
# ---------------------------------------------------------------------------- #
запускает функцию FTP putfile из многократно используемого класса формы
графического интерфейса; см. примечания в getfilegui: справедливыми
остаются большинство тех же предупреждений; формы для получения
и отправки выделены в единый класс, чтобы производить изменения
лишь в одном месте;
# ---------------------------------------------------------------------------- #
"""

from tkinter import mainloop
import putfile, getfilegui

class FtpPutfileForm(getfilegui.FtpForm):
	title = 'FtpPutfileGui'
	mode = 'Upload'
	def do_transfer(self, filename, servername, remotedir, userinfo):
		putfile.putfile(filename, servername, remotedir,
						userinfo, verbose=False)


if __name__ == '__main__':
	FtpPutfileForm()
	mainloop()