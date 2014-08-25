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

def num2str(n):
    s = '%.2f' % n
    return a2b_hex(''.join((s[:-3], s[-2:]))[:10].rjust(10, '0'))

def num3str(n):
    s = '%.3f' % n
    return a2b_hex(''.join((s[:-4], s[-3:]))[:10].rjust(10, '0'))

print 'ATOL'
ENQ = '\x05'
ACK = '\x06'
STX = '\x02'
ETX = '\x03'
EOT = '\x04'
NAK = '\x15'
DLE = '\x10'
DLEDLE = '%s%s' % (DLE, DLE)
DLEETX = '%s%s' % (DLE, ETX)
#PORT = '/dev/ttyS4'  # '/dev/ttyUSB0'
#BAUDRATE = 9600
PORT = '/dev/ttyUSB0'
BAUDRATE = 4800
LASTRESPONS = None
PASSWORD = 0  # Пароль админа по умолчанию = 0
REGKASSIR = False

# Последняя запрошенная команда: имя, счетчик повторений, дата первого обращения, дата последнего обращения
LASTCMD = ['', 0, None, None, None]

def crc(data):
    r = 0
    for ch in data:
        r ^= ord(ch)
    r ^= ord(ETX)
    return chr(r)

resultKKM = {
'0000': u'OK',
'0001': u'Контрольная лента обработана без ошибок',

'0008': u'Неверная цена (сумма',

'000a': u'Неверное количество',
'000b': u'Переполнение счетчика наличности',
'000c': u'Невозможно сторно последней операции',
'000d': u'Сторно по коду невозможно (в чеке зарегистрировано меньшее количество товаров с указанным кодом)',
'000e': u'Невозможен повтор последней операции',

'0014': u'Неверная длина',

'001e': u'Вход в режим заблокирован',
'001f': u'Проверьте дату и время',
'0020': u'Дата и время в ККМ меньше чем в ЭКЛЗ/ФП',

'0066': u'Команда не реализуется в данном режиме ККМ',

'007a': u'Данная модель ККМ не может выполнить команду',

'008c': u'Неверный пароль',

'008f': u'Обнуленная касса (повторное гашение невозможно)',

'009a': u'Чек закрыт – операция невозможна',
'009b': u'Чек открыт – операция невозможна',
'009c': u'Смена открыта, операция невозможна',

#'00': u'',
#'00': u'',
}

def cmdSkip(fgCut=False, ser=None, passwd=PASSWORD):
    """Запрос «Управление прогоном/отрезом чековой ленты»"""
    #rr = (-2, u'команда не реализована')
    rr = (-2, u'кнопка "прогона" находится на ккм')
    return rr

def sendMsg(ser, cmd):
    _cmd = cmd.replace(DLE, DLEDLE).replace(ETX, DLEETX)
    _crc = crc(_cmd)
    #print repr(STX), list(_cmd), repr(ETX), _crc
    ser.write(STX)
    ser.write(_cmd)
    ser.write(ETX)
    ser.write(_crc)
    ser.flush()

def sendCmd(cmd, fmtA='', ser=None, port=None, passwd=PASSWORD):
    global BAUDRATE, LASTRESPONS, REGKASSIR, PORT
    if port is None:
        port = PORT
    r = []
    err = None

    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE,\
                                parity=serial.PARITY_NONE,\
                                stopbits=serial.STOPBITS_ONE,\
                                timeout=0.5,\
                                writeTimeout=0.5)

        # Начало отправки команды
        ch = ''
        fg5 = 5  # Отправляем ENQ не более 5 раз
        while fg5:
            fg5-=1
            ser.write(ENQ)
            ch = ser.read(1)
            if ch == ACK:
                break
            elif ch in [ENQ, NAK, EOT]:
                fg5 = 5  # если получили NAK, то приемник занят
            else:
                ch = ''
        #print repr(ch)

        if ACK == ch:
            fg10 = 10  # пытаемся отправить команду не более 10 раз
            while fg10:
                fg10-=1
                sendMsg(ser, cmd)
                ch = ser.read(1)
                if ACK == ch:
                    fg10 = 0
                    #print 'A: ACK'
                    ser.write(EOT)
                    ch = ser.read(1)
                    if ENQ == ch:  # Получаем ответ
                        ser.write(ACK)
                        #r = []
                        fg4 = 4  # Ждем STX в течении 2 сек.
                        while fg4:
                            fg4-=1
                            ch = ser.read(1)
                            if ch == STX:
                                r.append(ch)
                                break
                        # Если r будет пустой, то это значит ответ не получен
                        ch = ser.read(1)
                        while ch:
                            r.append(ch)
                            if '\x10' == ch:
                                ch = ser.read(1)
                                r.append(ch)
                            elif '\x03' == ch:
                                break
                            ch = ser.read(1)
                        ch = ser.read(1)
                        r.append(ch)
                        if ch == crc(''.join(r[1:-2])):
                            ser.write(ACK)
                        else:
                            ser.write(NAK)
                        ch = ser.read(1)  # Читаем EOT
                        r.append(ch)

                        data = ''.join(r[1:-3]).replace(DLEDLE, DLE).replace(DLEETX, ETX)
                        #~ print 'data:', data, '|', len(data[2:])

                        cmdA = data[0]
                        err = '00%s' % b2a_hex(data[1])
                        if fmtA:
                            #~ print 333333, b2a_hex(data[2:])
                            if fmtA == 'hex':
                                #~ print 444444444444
                                LASTRESPONS = cmdA, err, b2a_hex(data[2:])
                            else:
                                #~ print 55555555555555
                                LASTRESPONS = cmdA, err, list(unpack(fmtA, data[2:]))
                        else:
                            LASTRESPONS = cmdA, err, None
                    elif '' == ch:
                        err = ''
                    else:
                        print 'A:', repr(ch)
                elif NAK == ch:
                    #print 'A: NAK'
                    pass
                else:
                    print 'sendMsg A:', repr(ch)
                    fg10 = 0
        if err is None:
            r = (-1, u'ответ ккм не прочитан')
        else:
            r = (0, 'OK')
    except Exception, e:
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
        print 'getRespons:', str(e)
        respons_cmd = None

    if respons_cmd:
        return respons_cmd, resultKKM.get(respons_cmd, respons_cmd)  # результат выполнения команды
    else:
        return -1, u'нет связи'

def cmdSumIN(nalichka, ser=None, passwd=PASSWORD):
    """Внесение"""

    resetMode()
    setMode(1)

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'I' + '\x00' + num2str(nalichka)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    resetMode()
    return rr

def cmdSumOUT(nalichka, ser=None, passwd=PASSWORD):
    resetMode()
    setMode(1)

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'O' + '\x00' + num2str(nalichka)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    resetMode()
    return rr

def cmdX(ser=None, passwd=PASSWORD):
    """Суточный отчет без гашения """

    resetMode()
    #mode = getMode()
    #print mode[0]
    #return

    setMode(2)

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'g' + a2b_hex('%02d' % 1)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    resetMode()
    return rr

def cmdZ(ser=None, passwd=PASSWORD):
    """Суточный отчет с гашением"""
    resetMode()
    #mode = getMode()
    #print mode[0]
    #return

    setMode(3)

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'Z'
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    resetMode()
    return rr

def cmdCachReg(ser=None, passwd = PASSWORD, regNumber = None):
    """Считать регистр
Команда:
"С"<Регистр (1)> <Параметр1 (1)> <Параметр2 (1)>.
Ответ:
"U"<Код ошибки (1)><Значение (Х)>.
Код команды ("С", 91h, 145).
"""
    cmd = a2b_hex(str(PASSWORD).rjust(4, '0')) + '\x91' + '\x0B' + '0' + '0'
    fmtA = 'hex'
    #~ print 'size: ', calcsize(fmtA)
    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #rr = tuple(dt)
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def getCachReg():
    """Получить выручку"""
    res = cmdCachReg()
    summa = int(LASTRESPONS[2])
    dl = len(str(summa))
    result = '%s.%s' % (str(summa)[:-2], str(summa)[(dl-2):])
    return result#'OTVET', res[0], res[1], '"LASTRESPONS:"', LASTRESPONS#, int(ee)

def cmdDrawer(ser=None, passwd=PASSWORD):
    """Открыть денежный ящик"""
    res = getCachReg()
    print res

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + '\x80'
    print 'cmd', cmd
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #rr = tuple(dt)
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    print 'rr', rr
    return rr

def cmdCopyDoc(ser=None, passwd=PASSWORD):
    """Повтор документа"""
    #rr = (-2, u'команда не реализована')
    rr = ('007a', u'Данная модель ККМ не может выполнить команду')
    return rr

def cmdCancel(ser=None, passwd=PASSWORD):
    """Аннулирование чека"""

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'Y'
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
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

def _cmdGetKkmNo(ser=None, passwd=PASSWORD):
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
                #data = LASTRESPONS[2]
                kkmNo = ''  # str(data[16])
                kkmNM = ''
                zavod = ''
                verPO = ''
                rr = (kkmNo, kkmNM, zavod, verPO)
    except:
        rr = None
    return rr

def cmdGetKkmNo(ser=None, passwd=PASSWORD):
    """Запрос «Информация о версии ПО ККМ»"""

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + '?'
    fmtA = '<B3s3sB4sB2sc2s2sB5sBB'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            #rr = getRespons()
            #if '0000' == rr[0]:
            if True:
                data = LASTRESPONS[2]
                #print data[3] & 2**1 # Смена открыта, 0 - нет
                #print b2a_hex(chr(data[7]))  # Режим работы,  Младшая тетрада – режим, старшая подрежим (формат «Подрежим.Режим»)
                #print b2a_hex(data[8])  # Номер чека
                #rr = b2a_hex(data[9])  # Номер смены
                #print data[-1]
                kkmNo =  b2a_hex(data[4]).lstrip('0')
                kkmNM = ''
                zavod = ''
                verPO = ''
                rr = (kkmNo, kkmNM, zavod, verPO)
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr


def getMode(ser=None, passwd=PASSWORD):
    """Запрос «Информация о версии ПО ККМ»"""

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + '?'
    fmtA = '<B3s3sB4sB2sc2s2sB5sBB'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            #rr = getRespons()
            #if '0000' == rr[0]:
            if True:
                data = LASTRESPONS[2]
                # Режим работы,  Младшая тетрада – режим, старшая подрежим (формат «Подрежим.Режим»)
                ch = b2a_hex(data[7])
                #print int(ch[1], 16), int(ch[0], 16)  # Режим, подрежим
                rr = str(int(ch[1], 16)) + str(int(ch[0], 16))
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def setMode(mode, ser=None, passwd=PASSWORD):
    """Вход в режим
    1 - Режим регистрации
    2 - Режим отчетов без гашения
    3 - Режим отчетов с гашением
    4 - Режим программирования
    5 - Режим доступа к ФП
    6 - Режим доступа к ЭКЛЗ
"""

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'V' + a2b_hex('%02d' % mode) + a2b_hex('%08d' % 30)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def resetMode(ser=None, passwd=PASSWORD):
    """Выход из текущего режима"""

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'H'
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
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

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + '?'
    fmtA = '<B3s3sB4sB2sB2s2sB5sBB'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            #rr = getRespons()
            #if '0000' == rr[0]:
            if True:
                data = LASTRESPONS[2]
                dt = list(data[1])
                dt.extend(data[2])
                dt = map(int, map(b2a_hex, dt))
                dt[0]+=2000
                rr = tuple(dt)
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def cmdBeep(ser=None, passwd=PASSWORD):
    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'G'
    fmtA = ''

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            #rr = getRespons()
            #if '0000' == rr[0]:
                #data = LASTRESPONS[2]
            pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def cmdSetDT(curDT=None, ser=None, passwd=PASSWORD):
    """Программирование времени и даты"""

    global LASTRESPONS
    resetMode()
    setMode(4)

    rr = cmdGetDT(ser)
    if rr and len(rr) > 2:
        kkmDT = rr
        if curDT is None:
            curDT = time.localtime()[:6]
        if kkmDT <> curDT:
            fg = kkmDT[:3] == curDT[:3]
            if not fg:
                cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'd' + \
                    a2b_hex('%02d' % curDT[2]) + \
                    a2b_hex('%02d' % curDT[1]) + \
                    a2b_hex('%02d' % (curDT[0]-2000))
                fmtA = '<B'
                try:
                    rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
                    if 0 == rr[0]:
                        rr = getRespons()
                        fg = '0000' == rr[0]
                except:
                    pass
                if fg:
                    try:
                        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
                        if 0 == rr[0]:
                            rr = getRespons()
                            fg = '0000' == rr[0]
                    except:
                        pass
                time.sleep(2)
            if fg:
                print 'curDT:', curDT
                cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'K' + \
                    a2b_hex('%02d' % curDT[3]) + \
                    a2b_hex('%02d' % curDT[4]) + \
                    a2b_hex('%02d' % curDT[5])
                fmtA = '<B'
                try:
                    rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
                    if 0 == rr[0]:
                        rr = getRespons()
                        fg = '0000' == rr[0]
                except:
                    pass
        else:
            rr = ('0000', 'OK')
    resetMode()
    return rr

def cmdPrint(text, ser=None, passwd=PASSWORD):

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'L' + text[:38].encode('866')
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def openCheck(ser, fg_return=False, passwd=PASSWORD):
    if fg_return:
        ctype=2
    else:
        ctype=1

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + '\x92' + a2b_hex('%02d' % 0) + a2b_hex('%02d' % ctype)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def sale(ser, amount, price, text=u"", department=0, taxes=[0,0,0,0][:], fg_return=False, passwd=PASSWORD):
    """Продажа"""

    if text:
        cmdPrint(text, ser, passwd)

    if fg_return:
        cmdNo = 'W'  # Возврат продажи
        cmd = a2b_hex(str(passwd).rjust(4, '0')) + cmdNo + a2b_hex('%02d' % 0) +num2str(price) + num3str(amount)
    else:
        cmdNo = 'R'  # Продажа
        cmd = a2b_hex(str(passwd).rjust(4, '0')) + cmdNo + a2b_hex('%02d' % 0) +num2str(price) + num3str(amount) + a2b_hex('%02d' % department)

    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser, passwd=passwd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None
    return rr

def discount(ser, skidka, passwd=PASSWORD):
    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'C\x00\x00\x00\x00' + num2str(skidka)[2:]
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    return rr

def closeCheck(ser, nalichka, skidka=0, text=u"", summa2=0,summa3=0,summa4=0, taxes=[0,0,0,0][:], passwd=PASSWORD):
    if skidka:
        r = discount(ser, skidka, passwd)
        if r and '0000' <> r[0]:
            return r
    # TODO: Надо реализовать разные типы оплаты
    tipOplaty = 1  # Наличка
    if summa2 > 0:
        tipOplaty = 2
        nalichka = summa2
    elif summa3 > 0:
        tipOplaty = 3
        nalichka = summa3
    elif summa4 > 0:
        tipOplaty = 4
        nalichka = summa4

    cmd = a2b_hex(str(passwd).rjust(4, '0')) + 'J' + a2b_hex('%02d' % 0) + a2b_hex('%02d' % tipOplaty) + num2str(nalichka)
    fmtA = '<B'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd, fmtA, ser)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                #data = LASTRESPONS[2]
                #print LASTRESPONS
                pass
    except Exception, e:
        print 'err:', str(e)
        rr = None

    return rr

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

def cmdChek(nalichnye, tovary, skidka=0, ser=None, port=None, passwd=PASSWORD):
    """Запрос «Фискальный документ»: Продажа
    Пример использования
    cmdChek(100, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
"""
    global BAUDRATE, LASTRESPONS, PORT
    if port is None:
        port = PORT

    chekSum = 0.0
    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE, timeout=0.5)

        resetMode()
        setMode(1)

        r = cmdCancel(ser, passwd)

        fgReturn = False
        r = openCheck(ser, fg_return=fgReturn)
        if r and '0000' == r[0]:
            fgNoErr = True
            for tovar, kolvo, cena in tovary:
                chekSum+=kolvo*cena
                r = sale(ser, kolvo, cena, text=tovar, fg_return=fgReturn)
                if '0000' <> r[0]:
                    fgNoErr = False
                    break
            if fgNoErr:
                if skidka:
                    skidkaSum = round(chekSum * skidka / 100.0, 2)
                    chekSum-=skidkaSum
                if not nalichnye:
                    nalichnye = chekSum
                if nalichnye < chekSum:
                    nalichnye = chekSum

                r = closeCheck(ser, nalichnye, skidka)
        resetMode()
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
    global LASTRESPONS, PORT
    if port is None:
        port = PORT

    chekSum = 0.0
    fgClose = False
    try:
        if ser is None:
            fgClose = True
            ser = serial.Serial(port, BAUDRATE, timeout=0.5)

        resetMode()
        setMode(1)

        r = cmdCancel(ser, passwd)

        fgReturn = True
        r = openCheck(ser, fg_return=fgReturn)
        if r and '0000' == r[0]:
            fgNoErr = True
            for tovar, kolvo, cena in tovary:
                chekSum+=kolvo*cena
                r = sale(ser, kolvo, cena, text=tovar, fg_return=fgReturn)
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

                r = closeCheck(ser, 0, skidka)
        resetMode()
    except Exception, e:
        LASTRESPONS = None
        r = (-1, str(e))
        #print 'Exception:', r
    finally:
        if fgClose and ser:
            ser.close()
    return r

def isPort(iPort, iSpeed):
    ser = None
    ports = []
    if isinstance(iPort, str):
        ports.append(iPort)
    else:
        if 'posix' == os.name:
            ports.append('/dev/ttyUSB%s' % iPort)
            ports.append('/dev/ttyS%s' % iPort)
        else:
            ports.append('COM%s' % (iPort + 1))
    for fPort in ports:
        try:
            ser = serial.Serial(fPort, iSpeed,\
                                parity=serial.PARITY_NONE,\
                                stopbits=serial.STOPBITS_ONE,\
                                timeout=0.5,\
                                writeTimeout=0.5)
            break
        except Exception, e:
            #print str(e)
            if ser:
                ser.close()
            ser = None
    return ser

def scanKkm():
    p, b = None, None
    fgBreak = False
    ports = {}
    for iPort in xrange(256):
        ser = None
        print '\r...',
        sys.stdout.flush()
        for iSpeed in [9600, 9600, 4800, 4800, 115200, 115200, 1200, 1200, 2400, 2400, 14400, 14400, 38400, 38400, 57600, 57600]:
            if ser:
                ser.close()
                ser = None
            ser = isPort(iPort, iSpeed)
            if ser and ser.isOpen():
                ports[ser.port] = ser.getBaudrate()
                print '\r', ser.port, ports[ser.port],
                sys.stdout.flush()

                ser.write(ENQ)
                ch = ser.read(1)
                #print repr(ch)

                if ch in [ACK, NAK]:
                    print '*'
                    #~ if 9600 <> iSpeed:
                        #~ data = setBaudrate(ser)
                        #~ if data:
                            #~ if '0000' == data[1]:
                                #~ print 'new baudrate 9600'
                    sys.stdout.flush()
                    p, b = ser.port, ser.getBaudrate()
                    fgBreak = True
                    break
        if ser:
            ser.close()
            ser = None
        if fgBreak:
            break
    #print ports
    return p, b

if __name__=="__main__":
    #PORT, BAUDRATE = scanKkm()
    #print PORT, BAUDRATE
    #if PORT is None:
    #    sys.exit()

    #~ ser = isPort(PORT, BAUDRATE)
    #~ if not (ser and ser.isOpen()):
        #~ print u'нет связи'.encode('utf8')
        #~ sys.exit()

    #~ ser.close()

    #print cmdSkip(True)
    #print cmdCopyDoc()

    #print cmdDrawer()
    #print cmdBeep()
    #print cmdGetKkmNo()
    #print cmdX()
    #print cmdZ()
    #print cmdSumIN(123.45)
    #print cmdSumOUT(123.45)
    #print cmdGetDT()
    #print cmdSetDT()
    #print cmdPrint(u'Привет2')
    #print cmdCancel()
    #err, note = cmdChek(100, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
    #print err, note
    #err, note = cmdChekReturn([(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
    #print err, note

    pass
