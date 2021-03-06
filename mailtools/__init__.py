#!/usr/local/bin/python3
#-*- coding: utf-8 -*-
# Глава 13. Сценарии на стороне клиента.
# Вспомогательный пакет mailtools.
# Файл инициализации.
# Пример 13.21 (Лутц Т2 стр.251)
"""
# ---------------------------------------------------------------------------- #
пакет mailtools: интерфейс к почтовому серверу, используется клиентами
pymail2, PyMailGUI и PyMailCGI; реализует загрузку, отправку, анализ,
составление, удаление, возможность добавления вложений, кодирование
(оба вида - MIME и Юникода) и так далее; классы, реализующие анализ,
получение и отправку, могут подмешиваться в подклассы,
использующий их методы, или использоваться как встраиваемые
или самостоятельные объекты;

этот пакет также включает удобные подклассы для работы в немом режиме
и многое другое; загружает все почтовые сообщения, если сервер POP
не устанавливает верхнюю границу; не содержит специальной поддержки
многопоточной модели выполнения или графического интерфейса
и позволяет подклассам предоставлять свою реализацию запроса пароля;
функция обратного вызова progress получает признак состояния; в случае
ошибки все методы возбуждают исключения - они должны обрабатываться
клиентом с графическим/другим интерфейсом; этот набор инструментов был
преобразован из простого модуля в пакет: вложенные модули импортируются
здесь для обратной совместимости;

4E: необходимо использовать синтаксис импортирования относительно
пакета, потому что в Py 3.x каталог пакета больше не включается
в путь поиска модулей при импортировании пакета, если пакет
импортируется из призвольного каталога (из другого каталога,
который использует этот пакет); кроме того, выполняется декодирование
Юникода в тексте письма при его получении (смотрите mailFetcher),
а также в некоторых частях с текстовым содержимым, которые, возможно,
были закодированы в формат MIME (смотрите mailParser);

TBD: в saveparts, возможно, следовало бы открывать файл в текстовом режиме,
когда основной тип определяется, как text?
TBD: в walkNamedParts, возможно, следовало бы перешагивать через нетипичные
типы, такие как message/delivery-status?
TBD: поддержка Юникода не подверглась всеобъемлющему тестированию:
обращайтесь к главе 13 за дополнительными сведениями о пакете email в Py3.1,
его ограничениях и о приемах, используемых здесь;
# ---------------------------------------------------------------------------- #
"""
# NEWIT если импортируется как пакет, то берем пространство имен mailconfig отсюда
from .resolvingConfig import mailconfig
# собрать содержимое всех модулей здесь, если импортируется каталог пакета
from .mailFetcher import *
from .mailSender import *							# 4E: импортирование относительно пакета
from .mailParser import *

# NEWIT однако не используем его, когда импортируем все, позволяя добавить mailconfig самостоятельно
# экспортировать вложенные модули для инструкций from mailtools import *
__all__ = 'mailFetcher', 'mailSender', 'mailParser'

# программный код самотестирования находиться в файле selftest.py, чтобы
# позволить установить путь к модулю mailconfig перед тем, как будут
# выполнены инструкции импортирования вложенных модулей выше
