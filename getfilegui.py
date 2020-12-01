#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Передача файлов с помощью ftplib.
# Добавляем пользовательский интерфейс.
# Пример 13.7 (Лутц Т2 стр.137)
"""
# ---------------------------------------------------------------------------- #
вызывает функцию FTP getfile из многократно используемого класса формы
графического интерфейса; использует os.chdir для перехода в целевой
локальный каталог (getfile в настоящее время предполагает, что в имени файла
отсутствует префикс пути к локальному каталогу); вызывает getfile.getfile
в отдельном потоке выполнения, что позволяет выполнять несколько запросов
одновременно и избежать блокировки графического интерфейса на время загрузки;
отличается от основанного на сокетах getfilegui, но повторно использует
класс Form построителя графического интерфейса; в данном виде поддерживает
как анонимный доступ к FTP, так и с указанием имени пользователя;

предостережение: содержимое поля ввода пароля здесь не скрывается
за звездочками, ошибки выводятся в консоль, а не в графический интерфейс
(потоки выполнения не могут обращаться к графическому интерфейсу в Windows),
поддержка многопоточной модели выполнения реализована не на все 100%
(существует небольшая задержка между os.chdir и открытием локального
выходного файла в getfile) и можно было бы выводить диалог "сохранить как",
для выбора локального каталога, и диалог с содержимым удаленного каталога,
для выбора загружаемого файла; читателям предлагается самостоятельно
добавить эти улучшения;
# ---------------------------------------------------------------------------- #
"""

from tkinter import Tk, mainloop
from tkinter.messagebox import showinfo
import getfile, os, sys, _thread								# здесь FTP-версия getfile
from Tom2.ch12.form import Form									# использовать инструмент форм

class FtpForm(Form):
	def __init__(self):
		root = Tk()
		root.title(self.title)
		labels = ['Server Name', 'Remote Dir', 'File Name',
				  'Local Dir', 'User Name?', 'Password?']
		Form.__init__(self, labels, root)
		self.mutex = _thread.allocate_lock()
		self.threads = 0

	def transfer(self, filename, servername, remotedir, userinfo):
		try:
			self.do_transfer(filename, servername, remotedir, userinfo)
			print('%s of "%s" successful' % (self.mode, filename))
		except:
			print('%s of "%s" has failed:' % (self.mode, filename), end=' ')
			print(sys.exc_info()[0], sys.exc_info()[1])
		self.mutex.acquire()
		self.threads -= 1
		self.mutex.release()

	def onSubmit(self):
		Form.onSubmit(self)
		localdir = self.content['Local Dir'].get()
		remotedir = self.content['Remote Dir'].get()
		servername = self.content['Server Name'].get()
		filename = self.content['File Name'].get()
		username = self.content['User Name?'].get()
		password = self.content['Password?'].get()
		userinfo = ()
		if username and password:
			userinfo = (username, password)
		if localdir:
			os.chdir(localdir)
		self.mutex.acquire()
		self.threads += 1
		self.mutex.release()
		ftpargs = (filename, servername, remotedir, userinfo)
		_thread.start_new_thread(self.transfer, ftpargs)
		showinfo(self.title, '%s of "%s" started' % (self.mode, filename))

	def onCancel(self):
		if self.threads == 0:
			Tk().quit()
		else:
			showinfo(self.title, 'Cannot eixt: %d threads running' % self.threads)

class FtpGetfileForm(FtpForm):
	title = 'FtpGetfileGui'
	mode = 'Download'
	def do_transfer(self, filename, servername, remotedir, userinfo):
		getfile.getfile(filename, servername, remotedir,
						userinfo, verbose=False, refetch=True)


if __name__ == '__main__':
	FtpGetfileForm()
	mainloop()