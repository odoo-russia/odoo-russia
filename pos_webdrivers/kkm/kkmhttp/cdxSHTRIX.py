#!/usr/bin/python
# -*- coding: utf8 -*-

from __future__ import with_statement

import sys, serial, os, time, traceback
from binascii import b2a_hex, a2b_hex
from struct import pack, unpack, calcsize

def _bin(v, size=16, reverse=False):
    if reverse:
        return ''.join('1' if (2**i & v) > 0 else '0' for i in xrange(size))
    else:
        return ''.join('1' if (2**i & v) > 0 else '0' for i in xrange(size-1, -1, -1))

def float2100int(f, digits=2):
        mask = "%."+str(digits)+'f'
        s    = mask % f
        return int(s.replace('.',''))

print 'Shtrih-M'
ENQ = '\x05'
STX = '\x02'
ACK = '\x06'
NAK = '\x15'
PORT = '/dev/ttyS4'  # '/dev/ttyUSB0'
BAUDRATE = 9600
PASSWORD = 30  # Пароль админа по умолчанию = 30, Пароль кассира по умолчанию = 1
LASTRESPONS = None
REGKASSIR = False

# Последняя запрошенная команда: имя, счетчик повторений, дата первого обращения, дата последнего обращения
LASTCMD = ['', 0, None, None, None]


resultKKM = {
'0000': u'OK',
'0001': u'Неисправен накопитель ФП 1, ФП 2 или часы',
'0002': u'Отсутствует ФП 1',
'0003': u'Отсутствует ФП 2',
'0004': u'Некорректные параметры в команде обращения к ФП',
'0005': u'Нет запрошенных данных',
'0006': u'ФП в режиме вывода данных',
'0007': u'Некорректные параметры в команде для данной реализации ФП',
'0008': u'Команда не поддерживается в данной реализации ФП',
'0009': u'Некорректная длина команды',
'000A': u'Формат данных не BCD',

'0033': u'Некорректные параметры в команде',

'0037': u'Команда не поддерживается в данной реализации ФР',

'0040': u'Переполнение диапазона скидок',

'0045': u'Cумма всех типов оплаты меньше итога чека',

'004a': u'Открыт чек – операция невозможна',
'004b': u'Буфер чека переполнен',

'004e': u'Смена превысила 24 часа',

'0050': u'Идет печать предыдущей команды',

'0058': u'Ожидание команды продолжения печати',

'005e': u'Некорректная операция',

'0056': u'Нет документа для повтора',

'006b': u'Нет чековой ленты',

'0072': u'Команда не поддерживается в данном подрежиме',
'0073': u'Команда не поддерживается в данном режиме',
}

def lrc2(data, lenData=None):
    """Подсчет CRC"""
    result = 0
    if lenData is None:
        lenData = len(data)
    result = result ^ lenData
    for c in data:
        result = result ^ ord(c)
    return chr(result)

def readA(ser):
    #global LASTRESPONS, LASTCMD
    data = None  # нет связи
    #~ fg = True
    #~ while fg:
        #~ print 'fg'
        #~ fg = False
    fg = True
    while fg:
        fg = False
        ser.write(ENQ)
        ch = ser.read(1)
        #print 'repr(ch):', repr(ch)
        if '\x06' == ch:
            #print 'ACK'  # Получаем ответ от ФР
            stx = ser.read(1)
            lenCmd = ser.read(1)
            data = ser.read(ord(lenCmd))
            crc = ser.read(1)
            if crc == lrc2(data):
                ser.write(ACK)
            else:
                ser.write(NAK)
            #~ err = '00%s' % b2a_hex(data[1])
            #~ if '0050' == err:
                #~ data[1] = '\x00'
                #~ fg = True
            #~ print 'read err:', err, fg
        elif '\x15' == ch:
            data = ''
            #print 'NAK'
        elif '' <> ch:  # Ожидаем конца передачи от ФР
            #LASTRESPONS = None
            #LASTCMD = ['', 0, None, None, None]
            fg = True
            ch = '.'
            while ch:
                ch = ser.read(1)
            #~ stx = ser.read(1)
            #~ lenCmd = ser.read(1)
            #~ data = ser.read(ord(lenCmd))
            #~ crc = ser.read(1)
            #~ if crc == lrc2(data):
                #~ ser.write(ACK)
            #~ else:
                #~ ser.write(NAK)
        #~ print 'data:', b2a_hex(data)
    print "DD", data
    filen = open("fffff", "w")
    filen.write(data)
    filen.close()
    return data

#~ def beep(ser=None, passwd=PASSWORD):
    #~ """Команда: Гудок
#~ 13H. Длина сообщения: 5 байт.
#~ • Пароль оператора (4 байта)
#~ Ответ:
#~ 13H. Длина сообщения: 3 байта.
#~ • Код ошибки (1 байт)
#~ • Порядковый номер оператора (1 байт) 1...30
#~ """
    #~ cmd = pack('<bi', 0x13, passwd)
    #~ fmtA = '<B'
#~
    #~ #return execCmd(ser, cmd, fmtA)
#~
    #~ global LASTRESPONS
    #~ rr = None
    #~ try:
        #~ rr = sendCmd(cmd, fmtA, ser)
        #~ if 0 == rr[0]:
            #~ rr = getRespons()
            #~ #if '0000' == rr[0]:
            #~ #    r = LASTRESPONS[2]
    #~ except:
        #~ rr = None
    #~ return rr

def cmdSkip(fgCut=False, ser=None, passwd=PASSWORD):
    """Запрос «Управление прогоном/отрезом чековой ленты»"""

    cmd = pack('<biBB', 0x29, passwd, 2**1, 5)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #r = LASTRESPONS[2]
                if fgCut:
                    rr = sendCmd(pack('<biB', 0x25, passwd, 1), '<B', ser)
                    if 0 == rr[0]:
                        rr = getRespons()
    except:
        rr = None
    return rr

#~ def cut(ser, passwd=PASSWORD):
    #~ """Отрезка чека
       #~ Команда:     25H. Длина сообщения: 6 байт.
            #~ • Пароль оператора (4 байта)
            #~ • Тип отрезки (1 байт) «0» – полная, «1» – неполная
       #~ Ответ:       25H. Длина сообщения: 3 байта.
            #~ • Код ошибки (1 байт)
            #~ • Порядковый номер оператора (1 байт) 1...30
    #~ """
    #~ cmd = pack('<biB', 0x25, passwd, 1)
    #~ fmtA = '<B'
#~
    #~ return execCmd(ser, cmd, fmtA)

def sendMsg(ser, cmd):
    lenCmd = len(cmd)
    crc = lrc2(cmd, lenCmd)
    #print b2a_hex(STX+lenCmd+cmd+crc)
    ser.write(STX)
    ser.write(chr(lenCmd))
    ser.write(cmd)
    ser.write(crc)
    ser.flush()

def execCmd(ser, cmd, fmtA=''):
    fg = True
    while fg:
        fg = False
        sendMsg(ser, cmd)
        data = readA(ser)
        if data:
            cmdA = b2a_hex(data[0])
            err = '00%s' % b2a_hex(data[1])
            if '0000' == err:
                if fmtA:
                    return cmdA, err, list(unpack(fmtA, data[2:]))
                else:
                    return cmdA, err, None
            elif '0050' == err:  # Идет печать предыдущей команды
                fg = True
                time.sleep(0.25)
            else:
                return cmdA, err, None

def sendCmd(cmd, fmtA='', ser=None, port=None, passwd=PASSWORD):
    global LASTRESPONS, REGKASSIR, PORT, BAUDRATE
    if port is None:
        port = PORT
    r = []

    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE, timeout=1)
        #print 'Вычитываем ответ предыдущий команды:',
        data = readA(ser)
        #print repr(data)
        #~ if not REGKASSIR:
            #~ # Вычитываем ответ предыдущий команды
            #~ data = readA(ser)
            #~ REGKASSIR = True
        #~ print 2222, REGKASSIR, ser
        fg = data is not None
        while fg:
            fg = False
            #print 'Посылаем команду'
            sendMsg(ser, cmd)
            #print 'Вычитываем ответ'
            data = readA(ser)
            print 'ERX', repr(data)
            print 'hexxxx', b2a_hex(data[2:]), type(data[2:])

            if data:
                cmdA = b2a_hex(data[0])
                err = '00%s' % b2a_hex(data[1])
                if '0000' == err:
                    if fmtA:
                        if fmtA:
                            LASTRESPONS = cmdA, err, b2a_hex(data[2:])
                        else:
                            LASTRESPONS = cmdA, err, list(unpack(fmtA, data[2:]))
                    else:
                        LASTRESPONS = cmdA, err, None
                elif '0050' == err:  # Идет печать предыдущей команды
                    fg = True
                    LASTRESPONS = cmdA, err, None
                    time.sleep(0.25)
                elif '0058' == err:  # Ожидание команды продолжения печати
                    fg = True
                    LASTRESPONS = cmdA, err, None
                    time.sleep(0.25)
                    sendMsg(ser, pack('<Bi', 0xB0, passwd))
                    data = readA(ser)
                else:
                    LASTRESPONS = cmdA, err, None
        if data is None:
            r = (-1, u'нет связи')
        else:
            r = (0, 'OK')
    except Exception, e:
        #import traceback
        #print traceback.print_exc()
        LASTRESPONS = None
        r = (-1, str(e))
        #print 'Exception:', r
    finally:
        if fgClose and ser:
            ser.close()
    return r

def getRespons(filename=None, data=None):
    global LASTRESPONS
    # Ответ для анализа
    if data:
        r = data
        LASTRESPONS = r
    elif filename:
        with open(filename, 'rb') as f:
            r = f.read()
        LASTRESPONS = r
    else:
        r = LASTRESPONS

    try:
        respons_cmd = r[1]
    except Exception, e:
        #import traceback
        #print traceback.print_exc()
        #print 'getRespons:', str(e)
        respons_cmd = None

    if respons_cmd:
        return respons_cmd, resultKKM.get(respons_cmd, respons_cmd)  # результат выполнения команды
    else:
        return -1, u'нет связи'

def cmdSumIN(nalichka, ser=None, passwd=PASSWORD):
    """Команда: Внесение
50H. Длина сообщения: 10 байт.
Пароль оператора (4 байта)
Сумма (5 байт)
Ответ:
50H. Длина сообщения: 5 байт.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
Сквозной номер документа (2 байта)
"""
    cmd = pack('<BilB', 0x50, passwd, float2100int(nalichka), 0)
    fmtA = '<BH'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser=ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def cmdSumOUT(nalichka, ser=None, passwd=PASSWORD):
    cmd = pack('<BilB', 0x51, passwd, float2100int(nalichka), 0)
    fmtA = '<BH'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser=ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def cmdX(ser=None, passwd=PASSWORD):
    """Команда: Суточный отчет без гашения
40H. Длина сообщения: 5 байт.
Пароль администратора или системного администратора (4 байта)
Ответ:
40H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 29, 30
"""
    cmdCancel(ser, passwd)

    cmd = pack('<Bi', 0x40, passwd)
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def cmdZ(ser=None, passwd=PASSWORD):
    """Команда: Суточный отчет с гашением
41H. Длина сообщения: 5 байт.
Пароль администратора или системного администратора (4 байта)
Ответ:
41H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 29, 30
"""
    cmd = pack('<Bi', 0x41, passwd)
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def cmdDrawer(ser=None, passwd=PASSWORD):
    """ Команда: Открыть денежный ящик
28H. Длина сообщения: 6 байт.
Пароль оператора (4 байта)
Номер денежного ящика (1 байт) 0, 1
Ответ:
28H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
"""
    cmd = pack('<BiB', 0x28, passwd, 0)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #r = LASTRESPONS[2]
                cmd = pack('<BiB', 0x28, passwd, 1)
                sendCmd(cmd, fmtA, ser)
    except:
        rr = None
    return rr

def cmdCopyDoc(ser=None, passwd=PASSWORD):
    """Команда: Повтор документа
8CH. Длина сообщения: 5 байт.
Пароль оператора (4 байта)
Ответ:
8CH. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
"""
    cmd = pack('<Bi', 0x8C, passwd)
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def cmdCancel(ser=None, passwd=PASSWORD):
    """Команда: Аннулирование чека
88H. Длина сообщения: 5 байт.
Пароль оператора (4 байта)
Ответ:
88H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
"""
    cmd = pack('<Bi', 0x88, passwd)
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def continuePrint(ser, passwd=PASSWORD):
    """Команда: Продолжение печати
B0H. Длина сообщения: 5 байт.
Пароль оператора, администратора или системного администратора (4 байта)
Ответ:
B0H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
"""
    cmd = pack('<Bi', 0xB0, passwd)
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                data = LASTRESPONS[2]
    except:
        rr = None
    return rr

#~ def kkmNo(ser, passwd=PASSWORD):
    #~ """
#~ Команда: Запрос состояния ФР
#~ 11H. Длина сообщения: 5 байт.
#~ Пароль оператора (4 байта)
#~ Ответ:
#~ 11H. Длина сообщения: 48 байт.
#~ Код ошибки (1 байт)
#~ Порядковый номер оператора (1 байт) 1...30
#~ Версия ПО ФР (2 байта)
#~ Сборка ПО ФР (2 байта)
#~ Дата ПО ФР (3 байта) ДД-ММ-ГГ
#~ Номер в зале (1 байт)
#~ Сквозной номер текущего документа (2 байта)
#~ Флаги ФР (2 байта)
#~ Режим ФР (1 байт)
#~ Подрежим ФР (1 байт)
#~ Порт ФР (1 байт)
#~ Версия ПО ФП (2 байта)
#~ Сборка ПО ФП (2 байта)
#~ Дата ПО ФП (3 байта) ДД-ММ-ГГ
#~ Дата (3 байта) ДД-ММ-ГГ
#~ Время (3 байта) ЧЧ-ММ-СС
#~ Флаги ФП (1 байт)
#~ Заводской номер (4 байта)
#~ Номер последней закрытой смены (2 байта)
#~ Количество свободных записей в ФП (2 байта)
#~ Количество перерегистраций (фискализаций) (1 байт)
#~ Количество оставшихся перерегистраций (фискализаций) (1 байт)
#~ ИНН (6 байт)
#~ """
    #~ cmd = pack('<Bi', 0x11, passwd)
    #~ fmtA = '<BHH3sBHHBBBHH3s3s3sBLHHBB6s'
#~
    #~ #data[13] = '%04d-%02d-%02d' % (2000+ord(data[13][2]), ord(data[13][0]), ord(data[13][1]) )
    #~ #data[14] = '%02d:%02d:%02d' % tuple(map(ord, data[14]))
    #~ cmdA, err, data = execCmd(ser, cmd, fmtA)
    #~ return cmdA, err, [data[0], data[16]]

def cmdGetKkmNo(ser=None, passwd=PASSWORD):
    """Запрос «Информация о версии ПО ККМ»"""

    cmd = pack('<Bi', 0x11, passwd)
    fmtA = '<BHH3sBHHBBBHH3s3s3sBLHHBB6s'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #print 'kkmno:', rr
            if '0000' == rr[0]:
                data = LASTRESPONS[2]
                kkmNo = str(data[16])
                kkmNM = ''
                zavod = ''
                verPO = ''
                rr = (kkmNo, kkmNM, zavod, verPO)
    except:
        rr = None
    #rr = ('1', '', '', '')
    return rr

#~ def getDT(ser, passwd=PASSWORD):
    #~ """
#~ Команда: Запрос состояния ФР
#~ 11H. Длина сообщения: 5 байт.
#~ Пароль оператора (4 байта)
#~ Ответ:
#~ 11H. Длина сообщения: 48 байт.
#~ Код ошибки (1 байт)
#~ Порядковый номер оператора (1 байт) 1...30
#~ Версия ПО ФР (2 байта)
#~ Сборка ПО ФР (2 байта)
#~ Дата ПО ФР (3 байта) ДД-ММ-ГГ
#~ Номер в зале (1 байт)
#~ Сквозной номер текущего документа (2 байта)
#~ Флаги ФР (2 байта)
#~ Режим ФР (1 байт)
#~ Подрежим ФР (1 байт)
#~ Порт ФР (1 байт)
#~ Версия ПО ФП (2 байта)
#~ Сборка ПО ФП (2 байта)
#~ Дата ПО ФП (3 байта) ДД-ММ-ГГ
#~ Дата (3 байта) ДД-ММ-ГГ
#~ Время (3 байта) ЧЧ-ММ-СС
#~ Флаги ФП (1 байт)
#~ Заводской номер (4 байта)
#~ Номер последней закрытой смены (2 байта)
#~ Количество свободных записей в ФП (2 байта)
#~ Количество перерегистраций (фискализаций) (1 байт)
#~ Количество оставшихся перерегистраций (фискализаций) (1 байт)
#~ ИНН (6 байт)
#~ """
    #~ cmd = pack('<Bi', 0x11, passwd)
    #~ fmtA = '<BHH3sBHHBBBHH3s3s3sBLHHBB6s'
#~
    #~ cmdA, err, data = execCmd(ser, cmd, fmtA)
    #~ return cmdA, err, (data[0], (2000+ord(data[13][2]), ord(data[13][0]), ord(data[13][1]), ord(data[14][0]), ord(data[14][1]), ord(data[14][2])))

def cmdGetDT(ser=None, passwd=PASSWORD):
    """Запрос «Считать текущее время и дату ККМ»"""

    cmd = pack('<Bi', 0x11, passwd)
    fmtA = '<BHH3sBHHBBBHH3s3s3sBLHHBB6s'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                data = LASTRESPONS[2]
                rr = (2000+ord(data[13][2]), ord(data[13][0]), ord(data[13][1]), ord(data[14][0]), ord(data[14][1]), ord(data[14][2]))
    except:
        rr = None
    return rr

def cmdSetDT(curDT=None, ser=None, passwd=PASSWORD):
    """Программирование времени и даты
    Установка даты
    Команда:     22H. Длина сообщения: 8 байт.
         • Пароль системного администратора (4 байта)
         • Дата (3 байта) ДД-ММ-ГГ
    Ответ:       22H. Длина сообщения: 2 байта.
         • Код ошибки (1 байт)
    Установка даты
    Команда:     23H. Длина сообщения: 8 байт.
         • Пароль системного администратора (4 байта)
         • Дата (3 байта) ДД-ММ-ГГ
    Ответ:       23H. Длина сообщения: 2 байта.
         • Код ошибки (1 байт)
    Установка времени
    Команда:    21H. Длина сообщения: 8 байт.
                 • Пароль системного администратора (4 байта)
                 • Время (3 байта) ЧЧ-ММ-СС
            Ответ:      21H. Длина сообщения: 2 байта.
                 • Код ошибки (1 байт)
    """
    global LASTRESPONS

    rr = cmdGetDT(ser)
    if rr and len(rr) > 2:
        kkmDT = rr
        if curDT is None:
            curDT = time.localtime()[:6]
        #print 'curDT:', curDT
        if kkmDT <> curDT:
            fg = False
            cmd = pack('<BiBBB', 0x22, passwd, curDT[2], curDT[1], curDT[0]-2000,)
            try:
                rr = sendCmd(cmd, '', ser)
                if 0 == rr[0]:
                    rr = getRespons()
                    fg = '0000' == rr[0]
            except:
                pass
            if fg:
                cmd = pack('<BiBBB', 0x23, passwd, curDT[2], curDT[1], curDT[0]-2000,)
                try:
                    rr = sendCmd(cmd, '', ser)
                    if 0 == rr[0]:
                        rr = getRespons()
                        fg = '0000' == rr[0]
                except:
                    pass
            if fg:
                cmd = pack('<BiBBB', 0x21, passwd, curDT[3], curDT[4], curDT[5],)
                try:
                    rr = sendCmd(cmd, '', ser)
                    if 0 == rr[0]:
                        rr = getRespons()
                        fg = '0000' == rr[0]
                except:
                    pass
        else:
            rr = ('0000', 'OK')
    return rr

def cmdPrint(text, ser=None, passwd=PASSWORD):
    """Команда: Печать строки
17H. Длина сообщения: 46 байт.
Пароль оператора (4 байта)
Флаги (1 байт) Бит 0 – контрольная лента, Бит 1 – чековая лента.
Печатаемые символы (40 байт)
Ответ:
17H. Длина сообщения: 3 байта.
Код ошибки (1 байт)
Порядковый номер оператора (1 байт) 1...30
"""
    cmd = pack('<BiB40s', 0x17, passwd, 2, text[:40].encode('cp1251').ljust(40, '\x00'))
    fmtA = '<B'

    #return execCmd(ser, cmd, fmtA)

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr

def openCheck(ser, fg_return=False, passwd=PASSWORD):
    """Команда:     8DH. Длина сообщения: 6 байт.
             • Пароль оператора (4 байта)
             • Тип документа (1 байт): 0 – продажа;
                                       1 – покупка;
                                       2 – возврат продажи;
                                       3 – возврат покупки
        Ответ:       8DH. Длина сообщения: 3 байта.
             • Код ошибки (1 байт)
             • Порядковый номер оператора (1 байт) 1...30
    """
    if fg_return:
        ctype=2
    else:
        ctype=0
    cmd = pack('<BiB', 0x8D, passwd, ctype)
    fmtA = '<B'

    return execCmd(ser, cmd, fmtA)

def sale(ser, amount, price, text=u"", department=0, taxes=[0,0,0,0][:], fg_return=False, passwd=PASSWORD):
    """Продажа
        Команда:     80H. Длина сообщения: 60 байт.
             • Пароль оператора (4 байта)
             • Количество (5 байт) 0000000000...9999999999
             • Цена (5 байт) 0000000000...9999999999
             • Номер отдела (1 байт) 0...16
             • Налог 1 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 2 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 3 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 4 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Текст (40 байт)
        Ответ:       80H. Длина сообщения: 3 байта.
             • Код ошибки (1 байт)
             • Порядковый номер оператора (1 байт) 1...30
    """
    if fg_return:
        cmdNo = 0x82  # Возврат продажи
    else:
        cmdNo = 0x80  # Продажа
    cmd = pack('<BilclcBBBBB40s', cmdNo, passwd, \
        float2100int(amount)*10, '\x00', \
        float2100int(price), '\x00', \
        department, taxes[0], taxes[1], taxes[2], taxes[3], \
        text[:40].encode('cp1251').ljust(40, '\x00')
    )
    fmtA = '<B'

    return execCmd(ser, cmd, fmtA)

def closeCheck(ser, nalichka, skidka=0, text=u"", summa2=0,summa3=0,summa4=0, taxes=[0,0,0,0][:], passwd=PASSWORD):
    """
        Команда:     85H. Длина сообщения: 71 байт.
             • Пароль оператора (4 байта)
             • Сумма наличных (5 байт) 0000000000...9999999999
             • Сумма типа оплаты 2 (5 байт) 0000000000...9999999999
             • Сумма типа оплаты 3 (5 байт) 0000000000...9999999999
             • Сумма типа оплаты 4 (5 байт) 0000000000...9999999999
             • Скидка/Надбавка(в случае отрицательного значения) в % на чек от 0 до 99,99
               % (2 байта со знаком) -9999...9999
             • Налог 1 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 2 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 3 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Налог 4 (1 байт) «0» – нет, «1»...«4» – налоговая группа
             • Текст (40 байт)
        Ответ:       85H. Длина сообщения: 8 байт.
             • Код ошибки (1 байт)
             • Порядковый номер оператора (1 байт) 1...30
             • Сдача (5 байт) 0000000000...9999999999
    """
    cmd = pack('<BilclclclchBBBB40s', 0x85, passwd, \
        float2100int(nalichka), '\x00', \
        float2100int(summa2), '\x00', \
        float2100int(summa3), '\x00', \
        float2100int(summa4), '\x00', \
        float2100int(skidka), \
        taxes[0], taxes[1], taxes[2], taxes[3], \
        text[:40].encode('cp1251').ljust(40, '\x00')
    )
    fmtA = '<Blx'
    cmdA, err, data = execCmd(ser, cmd, fmtA)
    if data:
        data[1] = data[1] / 100.0
    return cmdA, err, data

def setBaudrate(ser, passwd=PASSWORD):
    """Команда: Установка параметров обмена
14H. Длина сообщения: 8 байт.
• Пароль системного администратора (4 байта)
• Номер порта (1 байт) 0...255
• Код скорости обмена (1 байт) 0...6
• Тайм аут приема байта (1 байт) 0...255
Ответ:
14H. Длина сообщения: 2 байта.
• Код ошибки (1 байт)
Примечание: ФР поддерживает обмен со скоростями 2400, 4800, 9600, 19200, 38400,
57600, 115200 для порта 0, чему соответствуют коды от 0 до 6. Для
остальных портов диапазон скоростей может быть сужен, и в этом
случае, если порт не поддерживает выбранную скорость, будет выдано
сообщение об ошибке. Тайм-аут приема байта нелинейный. Диапазон
допустимых значений [0...255] распадается на три диапазона:
1. В диапазоне [0...150] каждая единица соответствует 1 мс, т.е. данным
диапазоном задаются значения тайм-аута от 0 до 150 мс;
2. В диапазоне [151...249] каждая единица соответствует 150 мс, т.е.
данным диапазоном задаются значения тайм-аута от 300 мс до 15 сек;
3. В диапазоне [250...255] каждая единица соответствует 15 сек, т.е.
данным диапазоном задаются значения тайм-аута от 30 сек до 105 сек.
По умолчанию все порты настроены на параметры: скорость 4800 бод с
тайм-аутом 100 мс. Если устанавливается порт, по которому ведется
обмен, то подтверждение на прием команды и ответное сообщение
выдаются ФР со старой скоростью обмена.
"""
    cmd = pack('<BiBBB', 0x14, passwd, 0, 2, 156)
    return execCmd(ser, cmd)


def isPort(iPort, iSpeed):
    ser = None
    if 'posix' == os.name:
        #fPort = '/dev/ttyUSB%s' % iPort
        fPort = '/dev/ttyS%s' % iPort
    else:
        fPort = 'COM%s' % (iPort + 1)
    try:
        ser = serial.Serial(fPort, iSpeed,\
                            parity=serial.PARITY_NONE,\
                            stopbits=serial.STOPBITS_ONE,\
                            timeout=0.1,\
                            writeTimeout=0.1)
    except Exception, e:
        #print str(e)
        if ser:
            ser.close()
        ser = None
    return ser

def scanKkm():
    for iPort in xrange(256):
        ser = None
        print '\r...',
        sys.stdout.flush()
        for iSpeed in [9600, 9600, 4800, 4800, 115200, 115200, 2400, 2400, 19200, 19200, 38400, 38400, 57600, 57600]:
            if ser:
                ser.close()
                ser = None
            ser = isPort(iPort, iSpeed)
            if ser:
                print '\r', ser.port, ser.getBaudrate(),
                sys.stdout.flush()
                try:
                    data = readA(ser)
                except:
                    data = None
                if data is not None:
                    print '*'
                    if 9600 <> iSpeed:
                        data = setBaudrate(ser)
                        if data:
                            if '0000' == data[1]:
                                print 'new baudrate 9600'
                    sys.stdout.flush()
                    p, b = ser.port, ser.getBaudrate()
                    ser.close()
                    ser = None
                    return p, b
                    #break
            else:
                break
        if ser:
            print '\r...',
            sys.stdout.flush()

def cmdChek(aNalichnye, tovary, skidka=0, ser=None, port=None, passwd=PASSWORD):
    """Запрос «Фискальный документ»: Продажа
    Пример использования
    cmdChek(100, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
"""
    global LASTRESPONS, PORT, BAUDRATE

    nalichnye = 0.0
    summa2 = 0.0
    summa3 = 0.0
    summa4 = 0.0
    try:
        nal, vidopl = aNalichnye
        if 1==vidopl:
            summa2 = nal
        elif 2==vidopl:
            summa3 = nal
        elif 3==vidopl:
            summa4 = nal
        else:
            nalichnye = nal
    except:
        nalichnye = aNalichnye
        vidopl = 0

    if port is None:
        port = PORT

    chekSum = 0.0
    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE, timeout=1)

        fgReturn = False
        data = openCheck(ser, fg_return=fgReturn)
        r = (data[1], resultKKM.get(data[1], data[1]))
        #print '  openCheck1:', r
        if '0000' <> r[0]:
            r = cmdCancel(ser, passwd)
            #print '  1:', r
            data = openCheck(ser, fg_return=fgReturn)
            r = (data[1], resultKKM.get(data[1], data[1]))
            #print '  openCheck2:', r
            #r = continuePrint(ser)
            #print '  continuePrint', r

        if '0000' == r[0]:
            fgNoErr = True
            for tovar, kolvo, cena in tovary:
                chekSum+=kolvo*cena
                data = sale(ser, kolvo, cena, text=tovar, fg_return=fgReturn)
                r = (data[1], resultKKM.get(data[1], data[1]))
                #print 'saleCheck:', r
                if '0000' <> r[0]:
                    fgNoErr = False
                    break
            if fgNoErr:
                if skidka:
                    skidkaSum = round(chekSum * skidka / 100.0, 2)
                    chekSum-=skidkaSum
                if 0==vidopl:
                    if not nalichnye:
                        nalichnye = chekSum
                    if nalichnye < chekSum:
                        nalichnye = chekSum

                data = closeCheck(ser, nalichnye, skidka, u'', summa2, summa3, summa4)
                r = (data[1], resultKKM.get(data[1], data[1]))
                #print '  closeCheck:', r
    except Exception, e:
        LASTRESPONS = None
        r = (-1, str(e))
        #print 'exceptionCheck:', r
        #print 'Exception:', r
    finally:
        if fgClose and ser:
            ser.close()
    #print 'check return:', r
    return r

def cmdChekReturn(tovary, skidka=0, ser=None, port=None, passwd=PASSWORD):
    """Запрос «Фискальный документ»: Возврат
    Пример использования
    cmdChek([100, (u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
"""
    global LASTRESPONS, PORT, BAUDRATE
    if port is None:
        port = PORT

    chekSum = 0.0
    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE, timeout=1)

        #r = continuePrint(ser)

        fgReturn = True
        data = openCheck(ser, fg_return=fgReturn)
        r = (data[1], resultKKM.get(data[1], data[1]))
        if '0000' <> r[0]:
            r = cmdCancel(ser, passwd)
            data = openCheck(ser, fg_return=fgReturn)
            r = (data[1], resultKKM.get(data[1], data[1]))

        if '0000' == r[0]:
            fgNoErr = True
            for tovar, kolvo, cena in tovary:
                chekSum+=kolvo*cena
                data = sale(ser, kolvo, cena, text=tovar, fg_return=fgReturn)
                r = (data[1], resultKKM.get(data[1], data[1]))
                if '0000' <> r[0]:
                    fgNoErr = False
                    break
            if fgNoErr:
                nalichnye = 0
                if skidka:
                    skidkaSum = round(chekSum * skidka / 100.0, 2)
                    chekSum-=skidkaSum
                if not nalichnye:
                    nalichnye = chekSum
                if nalichnye < chekSum:
                    nalichnye = chekSum

                data = closeCheck(ser, nalichnye, skidka)
                r = (data[1], resultKKM.get(data[1], data[1]))
    except Exception, e:
        LASTRESPONS = None
        r = (-1, str(e))
        #print 'Exception:', r
    finally:
        if fgClose and ser:
            ser.close()
    return r

def cmdCachReg(ser=None, passwd = PASSWORD, regNumber = None):
    """Команда: Запрос денежного регистра
1AH. Длина сообщения: 6 байт.
    • Пароль оператора (4 байта)
    • Номер регистра (1 байт) 0... 255

Ответ:
1AH. Длина сообщения: 9 байт.
    • Код ошибки (1 байт)
    • Порядковый номер оператора (1 байт) 1...30
    • Содержимое регистра (6 байт)
"""
    cmd = pack('<BiB', 0x1A, passwd, regNumber)
    fmtA = 'hex'#'<BBBBBBB'#'<bhf'
    #'<BBBBBBB' '<Hfb'
    #~ print 'size', calcsize(fmtA)
    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
    except:
        rr = None
    return rr

def cmdOperReg(ser=None, passwd=PASSWORD, regNumber = None):
    """Команда: Запрос операционного регистра
1BH. Длина сообщения: 6 байт.
    • Пароль оператора (4 байта)
    • Номер регистра (1 байт) 0... 255
Ответ:
1BH. Длина сообщения: 5 байт.
    • Код ошибки (1 байт)
    • Порядковый номер оператора (1 байт) 1...30
    • Содержимое регистра (2 байта)
"""
    cmd = pack('<BiB', 0x1B, passwd, regNumber)
    fmtA = 'hex'#<Bh'
    #~ print calcsize(fmtA)
    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS[2]
    except:
        rr = None
    return rr


def getOperReg():
    number_cheks = []
    for num in range(148, 152):
        res = cmdOperReg(regNumber = num)
        print 'registr', num, ':', LASTRESPONS
        s = LASTRESPONS[2][::-1]
        tt = ''
        for key, ch in enumerate(s):
            if key % 2 != 0:
                tt = str(tt) + str(s[key]) + str(s[key-1])
        s = bin(int(tt[:-2], 16))[2:]
        summa = int (str(s),2)
        number_cheks.append(summa)
        #~ number_cheks.append(LASTRESPONS[2][1])
    return number_cheks

def getCachReg():
    """Получаем выручку"""
    import decimal
    #номера денежного регистра
    list_number = ([193,194,195,196],[197,198,199,200],[201,202,203,204],[205,206,207,208])
    stryc = []
    #~ for num in range(0,64):
    #~ res = cmdCachReg(regNumber = 193)# запрос к денежому регистру (num - номером денежного регистра)
    #~ print 'registr 193', LASTRESPONS[2]
    #~ s = LASTRESPONS[2][::-1]
    #~ print 's', s
    #~ tt = ''
    #~ for key, ch in enumerate(s):
        #~ if key % 2 != 0:
            #~ tt = str(tt) + str(s[key]) + str(s[key-1])
    #~ print 'tt', tt[:-2]
    #~ s = bin(int(tt[:-2], 16))[2:]
    #~ print int (str(s),2)
    #1e 24 b8 00 00 00 00
    #00 00 00 00 8b 42 e1
#~
    for number in list_number:
        dic = []
        for num in number:
            res = cmdCachReg(regNumber = num)# запрос к денежому регистру (num - номером денежного регистра)
            print 'registr', num,':', LASTRESPONS[2]
            s = LASTRESPONS[2][::-1]
            tt = ''
            for key, ch in enumerate(s):
                if key % 2 != 0:
                    tt = str(tt) + str(s[key]) + str(s[key-1])
            s = bin(int(tt[:-2], 16))[2:]
            summa = int (str(s),2)
#~
            if summa == 0:
                summa = '0.00'
            else:
                dl = len(str(summa))
                summa = '%s.%s' % (str(summa)[:-2], str(summa)[(dl-2):])
            dic.append(decimal.Decimal(summa,2))
        stryc.append(dic)
    opl = []
    for summ in stryc:
        opl.append(summ[0] - summ[1] - summ[2] + summ[3])
    result = opl[0] + opl[1] + opl[2] + opl[3]
    return result


if __name__=="__main__":

    #PORT, BAUDRATE = scanKkm()
    #print PORT, BAUDRATE
    #sys.exit()

    #~ ser = serial.Serial(PORT, BAUDRATE,\
                        #~ parity=serial.PARITY_NONE,\
                        #~ stopbits=serial.STOPBITS_ONE,\
                        #~ timeout=1,\
                        #~ writeTimeout=1)
#~
    #~ # Вычитываем ответ предыдущей команды
    #~ data = readA(ser)
    #~ if data:
        #~ print repr(data)

    #print cmdBeep()
    #print cmdSkip(True)
    #print cmdSumIN(123.45)
    #print cmdSumOUT(123.45)
    #print cmdX()
    #print cmdZ()

    #print cmdDrawer()
    #print cmdCopyDoc()
    #print cmdCancel()
    #print continuePrint(ser)

    #print cmdGetKkmNo()
    #print cmdGetDT()

    #err, note = cmdSetDT()
    #print err, note

    #print cmdPrint(u'Привет4')

    #if data:
    #    print data, resultKKM.get(data[1], data[1])

    #err, note = cmdChek(100, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
    #print err, note

    #err, note = cmdChekReturn([(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
    #print err, note
    pass
