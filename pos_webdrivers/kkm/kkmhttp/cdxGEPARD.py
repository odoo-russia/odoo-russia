#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import sys, serial, binascii, os, time

def _bin(v, size=16, reverse=False):
    if reverse:
        return ''.join('1' if (2**i & v) > 0 else '0' for i in xrange(size))
    else:
        return ''.join('1' if (2**i & v) > 0 else '0' for i in xrange(size-1, -1, -1))

#print _bin(9, 16)
#print _bin(9, 16, True)
#sys.exit()

#print 'Merkuriy MS-K GEPARD'
print 'Merkuriy'
STX = '\x02'
ETX = '\x03'
PORT = '/dev/ttyS4'  # '/dev/ttyUSB0'
PASSWD = binascii.b2a_hex('0000')
LASTRESPONS = None
REGKASSIR = False

# Последняя запрошенная команда: имя, счетчик повторений, дата первого обращения, дата последнего обращения
LASTCMD = ['', 0, None, None, None]

def cmdCancel(passwd=PASSWD):
    """Отмена печати"""

    cmd = '01'

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        #time.sleep(0.3)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr


def cmdDrawer(passwd=PASSWD):
    """Запрос «Формирование импульсов управления внешним устройством»"""

    cmd30 = '38%s003000303100303100303100' % PASSWD
    cmd31 = '38%s003100303100303100303100' % PASSWD

    #~ global REGKASSIR
    #~ if not REGKASSIR:
        #~ rr = cmdRegKassir(passwd=passwd)
        #~ REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd30)
        time.sleep(0.25)
        rr = sendCmd(cmd31)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

def cmdSkip(fgCut=False, passwd=PASSWD):
    """Запрос «Управление прогоном/отрезом чековой ленты»"""

    if fgCut:
        cmd = '52%s00303500303100' % PASSWD
    else:
        cmd = '52%s00303100000000' % PASSWD

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

def cmdPrint(text, fgCut=False, passwd=PASSWD, ser=None, port=None):
    global PORT
    if port is None:
        port = PORT

    fgClose = False
    try:
        if ser is None:
            ser = serial.Serial(port, 9600, timeout=1)
        """Запрос «Нефискальный документ»"""
        cmd = "36%s00" % passwd
        r = sendCmd(cmd, ser=ser)

        #time.sleep(0.1)
        chLast = ''
        for chLast in text.encode('866'):
            ser.write(chLast)
            ch = ser.read(1)
            #print 'ch', type(ch), repr(ch), ch, binascii.b2a_hex(ch)

        if chLast == '\n':
            chLast = '\x1b\x1b'
        else:
            chLast = '\n\x1b\x1b'
        for t in chLast:
            ser.write(t)
            ch = ser.read(1)
            #print 'ch', type(ch), repr(ch), ch, binascii.b2a_hex(ch)
        if fgCut:
            #time.sleep(0.3)
            # Прогнать и отрезать
            sendCmd('52%s00303500303100' % PASSWD, ser=ser)
    except Exception, e:
        print 'err cmdPrint:', str(e)
        if fgClose and ser:
            ser.close()
    return ('0000', 'OK')

def sendCmd(cmd, fg_dump=False, ser=None, port=None):
    global LASTRESPONS, PORT
    if port is None:
        port = PORT

    r = []
    message = binascii.a2b_hex(cmd)
    message_bcc = hex(reduce(lambda result, x: (result + x) & 0xff, map(ord, message)))[2:]

    if fg_dump:
        cmd = '02%s%s03' % (cmd.upper(), binascii.b2a_hex(message_bcc.upper()))
        for i in xrange(0, len(cmd), 2):
            if i % 32 == 0:
                print
                print '%08X:' % (i / 2),
            if i % 16 == 0:
                print ' ',
            #print i, cmd[i:i+2], i % 16, i % 32
            print cmd[i:i+2],
        print
        r = (-1, 'dump')

    if True:
        #ser = None
        fgClose = False
        try:
            if ser is None:
                fgClose = True
                ser = serial.Serial(port, 9600, timeout=1)
            ser.write(STX)
            ser.write(message)
            ser.write(message_bcc)
            ser.write(ETX)
            countEmpty = 0
            while True:
                ch = ser.read(1)
                #print 'ch', type(ch), repr(ch), ch
                if ch == '\x03':
                    r.append(ch)
                    break
                if ch == '\x06':
                    countEmpty = 0
                    continue
                elif ch in ['', ETX]:
                    countEmpty+=1
                    if countEmpty > 1:
                        break
                else:
                    countEmpty = 0
                r.append(ch)
            r = binascii.b2a_hex(''.join(r))[0:-6]
            if r[:2] == '02':
                LASTRESPONS = r[2:]
            else:
                LASTRESPONS = r
            r = (0, 'OK')
        except Exception, e:
            LASTRESPONS = None
            r = (-1, str(e))
            #print 'Exception:', r
        finally:
            if fgClose and ser:
                ser.close()
    return r

def cmdX(passwd=PASSWD):
    """ X-отчет"""

    cmd = "5F%s003100303400000000" % passwd

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

def cmdZ(passwd=PASSWD):
    """ Z-отчет"""

    cmd = "5F%s003000303400000000" % passwd

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

resultKKM = {
'0000': u'OK',
'0001': u'Ошибка в фискальных данных, аппарат блокирован.',
'0002': u'Не закрыта смена.',
'0003': u'Исчерпан ресурс сменных записей в фискальную память.',
'0004': u'Превышена длина поля команды.',
'0005': u'Неверный формат поля команды.',
'0006': u'Ошибка чтения таймера.',
'0007': u'Неверная дата.',
'0008': u'Неверное время.',
'0009': u'Дата меньше последней даты, зарегистрированной в фискальной памяти.',
'000A': u'Операция прервана пользователем.',
'000B': u'Запрещенная команда ПУ (см п. 3.3).',
'000C': u'Не открыта смена.',
'000D': u'Кассир не зарегистрирован.',
'000E': u'Переполнение приёмного буфера.',
'000F': u'Ошибка записи в фискальную память.',
'0010': u'Ошибка установки таймера.',
'0011': u'Неверный пароль налогового инспектора.',
'0012': u'Неверный пароль на связь.',
'0013': u'Исчерпан ресурс перерегистраций.',
'0014': u'Аппарат не фискализирован.',
'0015': u'Значение поля команды вне диапазона.',
'0016': u'Ошибка чтения фискальной памяти.',
'0017': u'Переполнение или отрицательный результат счётчика.',
'0018': u'Обязательное поле команды имеет нулевую длину.',
'0019': u'Неверный формат команды.',
'001A': u'Дата или время последнего документа в смене меньше предыдущего.',
'001B': u'Не используется.',
'001C': u'Ошибка в расположении реквизитов (пересечение или выход за область печати).',
'001D': u'Нет такой команды.',
'001E': u'Неверная контрольная сумма (BCC)',

'002A': u'Текущее состояние ККМ не позволяет выполнить операцию.',

'0078': u'Переполнение сменного счётчика суммы наличных при вычитании.',
'007D': u'Переполнение счётчика итоговой суммы в чеке при вычислении скидки.',

'0099': u'Сумма оплаты меньше суммы чека.',
'009E': u'Блокировка выполнения команды. Выполняется тестирование оборудования ККМ.',
}

statKKM = (
  ((0,), u'Смена', (u'Закрыта', u'Открыта')),
  ((1,), u'Ширина ленты', (u'80 мм', u'57 мм')),
  ((2,), u'Буфер копии документа близок к концу (осталось менее 5%)', (u'Нет', u'Да')),
  ((3,), u'Графическое клише', (u'Выключено', u'Включено')),
  ((4,), u'Аппарат фискализирован', (u'Нет', u'Да')),
  ((5,), u'Фискальная память близка к концу (осталось менее 30 записей)', (u'Нет', u'Да')),
  ((6,), u'Фискальная память исчерпана', (u'Нет', u'Да')),
  ((7,), u'Протокол', (u'BS', u'XON/XOFF')),
  ((8,9), u'Состояние документа', {u'00': u'Документ закрыт',
                                   u'01': u'Документ открыт (возможно проведение финансовых операций)',
                                   u'10': u'Итог (проведение финансовых операций запрещено, документ не может быть закрыт т.к. напечатаны не все обязательные реквизиты)',
                                   u'11': u'Завершение документа (проведение финансовых операций запрещено, документ может быть закрыт)',
                                  }),
  ((10,14),u'Проводимая операция',{u'00000': u'Продажа',
                                   u'00001': u'Возврат продажи за наличные',
                                   u'00010': u'Внесение суммы (подкрепление)',
                                   u'00011': u'Выплата суммы (инкассация)',
                                   u'10010': u'Возврат продажи за безналичные',
                                   u'11111': u'Завершена',
                                  }),
  ((15,), u'Наличие копии последнего документа', (u'Нет', u'Да')),
)

statPRN = (
  ((0,), u'Готовность дисплея', (u'Нет', u'Да')),
  ((1,), u'Состояние датчика денежного ящика', (u'Замкнут', u'Разомкнут')),
  ((2,), u'Технологический режим', (u'Да', u'Нет')),
  ((3,), u'Ошибка принтера', (u'Ошибка', u'Нет')),
  ((4,), u'Отрезной нож', (u'Включен', u'Выключен')),
  ((5,), u'Конец бумаги', (u'Нет', u'Да')),
  ((6,), u'Готовность принтера', (u'Нет', u'Да')),
  ((7,), u'Принтер занят, находится в состоянии offline или произошла ошибка', (u'Нет', u'Да')),
)

def sendPrint(ser=None, passwd=PASSWD):
    """Запрос «Нефискальный документ»"""
    cmd = "36%s00" % passwd
    r = sendCmd(cmd, ser=ser)
    #getRespons(data=r)


def cmdPovtoritOtvet(passwd=PASSWD):
    """Запрос «Повторить ответ»"""
    cmd = "49%s00" % passwd
    rr = sendCmd(cmd)
    if 0 == rr[0]:
        rr = getRespons()
    return rr

def cmdGetKkmNo(passwd=PASSWD):
    """Запрос «Информация о версии ПО ККМ»"""
    global LASTRESPONS
    rr = None
    try:
        cmd = "45%s000000" % passwd
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #print 'kkmno:', rr
            if '0000' == rr[0]:
                r = LASTRESPONS
                kkmNo = binascii.a2b_hex(r[30:44]).strip('\x00').decode('866')
                kkmNM = binascii.a2b_hex(r[46:106]).strip('\x00').decode('866')
                zavod = binascii.a2b_hex(r[108:168]).strip('\x00').decode('866')
                verPO = binascii.a2b_hex(r[170:230]).strip('\x00').decode('866')
                rr = (kkmNo, kkmNM, zavod, verPO)
    except:
        rr = None
    return rr

def cmdGetDT(passwd=PASSWD):
    """Запрос «Считать текущее время и дату ККМ»"""
    global LASTRESPONS
    rr = None
    try:
        cmd = "48%s00" % passwd
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                r = LASTRESPONS
                d = binascii.a2b_hex(r[30:46])
                t = binascii.a2b_hex(r[48:56])
                rr = tuple(map(int, [d[-4:], d[2:4], d[:2], t[:2], t[2:]]))
    except:
        rr = None
    return rr

def _cmdSetDT(dt=None, passwd=PASSWD):
    """Запрос «Программирование времени и даты»"""
    global LASTRESPONS
    rr = None
    try:
        if dt is None:
            dt = time.localtime()[:5]
        d = '%02d%02d%04d' % (dt[2], dt[1], dt[0])
        t = '%02d%02d' % (dt[3], dt[4])
        cmd = "47%s00%s00%s00" % (passwd, binascii.b2a_hex(d), binascii.b2a_hex(t))
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except Exception, e:
        #print str(e)
        rr = None
    return rr

def cmdSetDT(curDT=None, passwd=PASSWD):
    """Программирование времени и даты"""
    rr = cmdGetDT()
    if len(rr) > 2:
        kkmDT = rr
        if curDT is None:
            curDT = time.localtime()[:5]
        if not (kkmDT == curDT):
            rr = _cmdSetDT(curDT, passwd)
            if '0000' == rr[0]:
                rr = _cmdSetDT(curDT, passwd)
        else:
            rr = ('0000', 'OK')
        #print rr, curDT
    return rr

def cmdCopyDoc(passwd=PASSWD):
    """Запрос «Копия документа»"""
    global LASTRESPONS
    rr = None
    try:
        cmd = "54%s00" % passwd
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

def cmdSumIN(nalichka, passwd=PASSWD):
    """Внесение наличной суммы в кассу"""
    r = []

    rek_tip = '01'  # Наименование учреждения, строка 1
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 0  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()


    rek_tip = '02'  # Наименование учреждения, строка 2
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    #print binascii.a2b_hex('3000')
    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    #print binascii.a2b_hex('310000')
    moveY = 1  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303200303032300030000031000000"


    rek_tip = '03'  # Наименование учреждения, строка 3
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 2  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303300303032300030000032000000"


    rek_tip = '04'  # Наименование учреждения, строка 4
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 3  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303400303032300030000033000000"

    r.append(cmdTxt(4, 0, u'-'*40))

    r.append(cmdTxt(5, 0, u'ККМ'))

   #print  binascii.a2b_hex('3036')
    rek_tip = '06'  # Номер кассира
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 4  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303600303032300030000031300000'


    rek_tip = '00'  # Номер ККМ
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 6  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303000303032300030000035000000"

    r.append(cmdTxt(5, 32, u'ВНЕСЕНИЕ'))

    #print  binascii.a2b_hex('3130')
    rek_tip = '10'  # ИНН
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "313000303032300030000036000000"


    r.append(cmdTxt(6, 30, u'Док№'))

    #print  binascii.a2b_hex('3037')
    rek_tip = '07'  # Номер документа
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303700303032300030000038000000'


    #print  binascii.a2b_hex('3035')
    rek_tip = '05'  # Дата совершения операции и Время совершения операции
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303500303032300030000037000000"


    r.append(cmdTxt(7, 30, u'Чек№'))

    #print  binascii.a2b_hex('3038')
    rek_tip = '08'  # Номер чека
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303800303032300030000039000000'

    posIndex = 8
    r.append(cmdTxt(posIndex, 0, u'-'*40))

    posIndex+=1
    r.append(cmdCena(posIndex, 0, 0, nalichka))

    posIndex+=1
    rek_tip = binascii.b2a_hex('12')  # Итоговая сумма
    fg_rek = '30303230' # Флаги реквизита

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '313200303032300030000031360000'


    # Head
    kod_msg = '53'
    kod_cmd = '32'  # Внесение

    #fg_dok = '3134'  # Оформление документа, Расширенный формат ответа: включить
    fg_dok = '0034'  # Оформление документа, Расширенный формат ответа: выключить

    rek_kolvo = len(r)  # Количество передаваемых реквизитов
    s = binascii.b2a_hex(str(rek_kolvo))
    rek_kolvo = s+'0'*(6-len(s))

    cmd = "%(kod_msg)s%(passwd)s00%(kod_cmd)s00%(fg_dok)s00%(rek_kolvo)s00" % locals()
    r.insert(0, cmd)
    cmd = ''.join(r)

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr


def cmdSumOUT(nalichka, passwd=PASSWD):
    """Изъятие/выплата наличной суммы из кассы"""
    r = []

    rek_tip = '01'  # Наименование учреждения, строка 1
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 0  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()


    rek_tip = '02'  # Наименование учреждения, строка 2
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    #print binascii.a2b_hex('3000')
    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    #print binascii.a2b_hex('310000')
    moveY = 1  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303200303032300030000031000000"


    rek_tip = '03'  # Наименование учреждения, строка 3
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 2  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303300303032300030000032000000"


    rek_tip = '04'  # Наименование учреждения, строка 4
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 3  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303400303032300030000033000000"

    r.append(cmdTxt(4, 0, u'-'*40))

    r.append(cmdTxt(5, 0, u'ККМ'))

   #print  binascii.a2b_hex('3036')
    rek_tip = '06'  # Номер кассира
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 4  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303600303032300030000031300000'


    rek_tip = '00'  # Номер ККМ
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 6  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303000303032300030000035000000"

    r.append(cmdTxt(5, 33, u'ВЫПЛАТА'))

    #print  binascii.a2b_hex('3130')
    rek_tip = '10'  # ИНН
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "313000303032300030000036000000"


    r.append(cmdTxt(6, 30, u'Док№'))

    #print  binascii.a2b_hex('3037')
    rek_tip = '07'  # Номер документа
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303700303032300030000038000000'


    #print  binascii.a2b_hex('3035')
    rek_tip = '05'  # Дата совершения операции и Время совершения операции
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303500303032300030000037000000"


    r.append(cmdTxt(7, 30, u'Чек№'))

    #print  binascii.a2b_hex('3038')
    rek_tip = '08'  # Номер чека
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303800303032300030000039000000'

    posIndex = 8
    r.append(cmdTxt(posIndex, 0, u'-'*40))

    posIndex+=1
    r.append(cmdCena(posIndex, 0, 0, nalichka))

    posIndex+=1
    rek_tip = binascii.b2a_hex('12')  # Итоговая сумма
    fg_rek = '30303230' # Флаги реквизита

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '313200303032300030000031360000'


    # Head
    kod_msg = '53'
    kod_cmd = '33'  # Изъятие/выплата

    #fg_dok = '3134'  # Оформление документа, Расширенный формат ответа: включить
    fg_dok = '0034'  # Оформление документа, Расширенный формат ответа: выключить

    rek_kolvo = len(r)  # Количество передаваемых реквизитов
    s = binascii.b2a_hex(str(rek_kolvo))
    rek_kolvo = s+'0'*(6-len(s))

    cmd = "%(kod_msg)s%(passwd)s00%(kod_cmd)s00%(fg_dok)s00%(rek_kolvo)s00" % locals()
    r.insert(0, cmd)
    cmd = ''.join(r)

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr


def cmdTxt(y, x, text, fg_rek='30303230'):
    rek_tip = '99'  # Дополнительный реквизит (Название товара)
    rek_tip = binascii.b2a_hex(rek_tip)

    #fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = x  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = y  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    #rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка
    rek_nm = text[:40]  # Собственно реквизит строка
    s = binascii.b2a_hex(rek_nm.encode('866'))
    rek_nm = s+'0'*(80-len(s))

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    return cmd
    #print cmd
    #print '393900303032300030000031310000'

def cmdCena(y, x, kolvo, cena, edizm=u'', fg_rek='30303232'):
    #print binascii.a2b_hex('3131')
    rek_tip = '11'  # Цена услуги
    rek_tip = binascii.b2a_hex(rek_tip)

    #fg_rek = '30303232' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100010)  # Использовать шрифты по умолчанию: Да; Товар (услуга), денежная сумма.

    moveX = x  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = y  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    #Таб. 3.2.2 Реквизит «Цена услуги»
    otdelNo = '3100'  # Номер отдела (секции)
    tovKod = '300000000000'  # Код товара
    procSkid = '0000000000'  # Процентная скидка/надбавка6

    tovKolvo = kolvo  # Количество (вес, литры)
    if tovKolvo:
        s = binascii.b2a_hex(str(tovKolvo))
    else:
        s = '00'
    tovKolvo = s+'0'*(22-len(s))

    tovCena = '%.2f' % cena  # Цена услуги, денежная скидка, надбавка
    if len(tovCena.split('.')[-1]) < 2:
        tovCena+='0'
    s = binascii.b2a_hex(tovCena)
    tovCena = s+'0'*(22-len(s))

    tovEdizm = u''[:5]  # Единица измерения количества
    s = binascii.b2a_hex(tovEdizm.encode('866'))
    tovEdizm = s+'0'*(10-len(s))

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s00" \
    "%(otdelNo)s00%(tovKod)s00%(procSkid)s00%(tovKolvo)s00%(tovCena)s00%(tovEdizm)s00" % locals()
    #print cmd
    #print '31310030303232003000003132000031000030000000000000000000000000340000000000000000000000312E32330000000000000000000000000000'
    return cmd



def cmdChek(nalichnye, tovary, skidka=0, passwd=PASSWD):
    """Запрос «Фискальный документ»: Продажа
    Пример использования
    cmdChek(100, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
"""
    #~ print 'nalichnye:', nalichnye
    #~ print 'tovary:', tovary
    #~ print 'skidka:', skidka
    #~ sys.exit()

    r = []

    rek_tip = '01'  # Наименование учреждения, строка 1
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 0  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()


    rek_tip = '02'  # Наименование учреждения, строка 2
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    #print binascii.a2b_hex('3000')
    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    #print binascii.a2b_hex('310000')
    moveY = 1  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303200303032300030000031000000"


    rek_tip = '03'  # Наименование учреждения, строка 3
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 2  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303300303032300030000032000000"


    rek_tip = '04'  # Наименование учреждения, строка 4
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 3  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303400303032300030000033000000"

    r.append(cmdTxt(4, 0, u'-'*40))

    r.append(cmdTxt(5, 0, u'ККМ'))

   #print  binascii.a2b_hex('3036')
    rek_tip = '06'  # Номер кассира
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 4  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303600303032300030000031300000'


    rek_tip = '00'  # Номер ККМ
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 6  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303000303032300030000035000000"

    r.append(cmdTxt(5, 33, u'ПРОДАЖА'))


    #print  binascii.a2b_hex('3130')
    rek_tip = '10'  # ИНН
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "313000303032300030000036000000"


    r.append(cmdTxt(6, 30, u'Док№'))

    #print  binascii.a2b_hex('3037')
    rek_tip = '07'  # Номер документа
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303700303032300030000038000000'


    #print  binascii.a2b_hex('3035')
    rek_tip = '05'  # Дата совершения операции и Время совершения операции
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303500303032300030000037000000"


    r.append(cmdTxt(7, 30, u'Чек№'))

    #print  binascii.a2b_hex('3038')
    rek_tip = '08'  # Номер чека
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303800303032300030000039000000'

    posIndex = 8
    r.append(cmdTxt(posIndex, 0, u'-'*40))

    chekSum = 0.0
    for tovar, kolvo, cena in tovary:
        chekSum+=kolvo*cena
        posIndex+=1
        r.append(cmdTxt(posIndex, 0, tovar))
        posIndex+=1
        r.append(cmdCena(posIndex, 0, kolvo, cena))
    if skidka:
        skidkaSum = round(chekSum * skidka / 100.0, 2)
        chekSum-=skidkaSum

    #~ r.append(cmdTxt(9, 0, u'Товар1'))
    #~ r.append(cmdCena(10, 0, 1, 1.23))
    #~ r.append(cmdTxt(11, 0, u'Товар2'))
    #~ r.append(cmdCena(12, 0, 2, 0.45))

    posIndex+=1
    if skidka:
        #print binascii.a2b_hex('3231')
        rek_tip = '21'  # Общая скидка/надбавка чек
        rek_tip = binascii.b2a_hex(rek_tip)

        fg_rek = '30304130' # Флаги реквизита
        #print _bin(int(binascii.a2b_hex(fg_rek), 16))
        #print _bin(0b0000000010100000)  # Использовать шрифты по умолчанию: Да; Для реквизитов "Цена услуги", Надбавка "Общая скидка/надбавка на чек"

        moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
        s = binascii.b2a_hex(str(moveX))
        moveX = s+'0'*(4-len(s))

        posIndex+=1
        moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
        s = binascii.b2a_hex(str(moveY))
        moveY = s+'0'*(6-len(s))

        rek_nm = '%.2f' % skidka  # Процент скидки Собственно реквизит строка
        s = binascii.b2a_hex(rek_nm.encode('866'))
        rek_nm = s+'0'*(80-len(s))

        cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
        r.append(cmd)
        #print cmd
        #print '3231003030413000300000313500000000000000'

    posIndex+=1

    #fg_rek = '30303230' # Флаги реквизита
    fg_rek = binascii.b2a_hex('6020') # Двойная ширина и высота шрифта
    #fg_rek = binascii.b2a_hex(hex(0b0110000000100000)[2:])
    r.append(cmdTxt(posIndex, 0, u'ИТОГ     =', fg_rek))

    #print binascii.a2b_hex('3132')
    rek_tip = '12'  # Итоговая сумма
    rek_tip = binascii.b2a_hex(rek_tip)

    #fg_rek = '30303230' # Флаги реквизита
    fg_rek = binascii.b2a_hex('6020') # Двойная ширина и высота шрифта
    #fg_rek = binascii.b2a_hex(hex(0b0110000000100000)[2:])  # Двойная ширина и высота шрифта

    moveX = 10  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '313200303032300030000031360000'


    posIndex+=1
    r.append(cmdTxt(posIndex, 0, u'НАЛИЧНЫЕ'))

    #print binascii.a2b_hex('3133')
    rek_tip = '13'  # Уплаченная сумма
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: Да

    moveX = 20  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    #rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка
    if not nalichnye:
        nalichnye = chekSum
    if nalichnye < chekSum:
        nalichnye = chekSum
    rek_nm = '%.2f' % nalichnye  # Уплаченная сумма Собственно реквизит строка
    #print rek_nm
    if len(rek_nm.split('.')[-1]) < 2:
        rek_nm+='0'
    s = binascii.b2a_hex(rek_nm.encode('866'))
    rek_nm = s+'0'*(80-len(s))
    #print rek_nm
    #sys.exit()

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '313300303032300030000031380000'

    if nalichnye <> chekSum:
        #print binascii.a2b_hex('3134')
        rek_tip = '14'  # Сумма сдачи
        rek_tip = binascii.b2a_hex(rek_tip)

        fg_rek = '30303230' # Флаги реквизита
        #print _bin(int(binascii.a2b_hex(fg_rek), 16))
        #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: Да

        moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
        s = binascii.b2a_hex(str(moveX))
        moveX = s+'0'*(4-len(s))

        posIndex+=1
        moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
        s = binascii.b2a_hex(str(moveY))
        moveY = s+'0'*(6-len(s))

        rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка
        #rek_nm = u'100.00'  # Собственно реквизит строка
        #s = binascii.b2a_hex(rek_nm.encode('866'))
        #rek_nm = s+'0'*(80-len(s))

        cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
        r.append(cmd)
        #print cmd
        #print '313400303032300030000031390000'

    posIndex+=1
    #r.append(cmdTxt(posIndex, 0, u'-'*40))
    r.append(cmdTxt(posIndex, 0, u''*40))


    # Head
    kod_msg = '53'
    kod_cmd = '30'  # Продажа

    #fg_dok = '3134'  # Оформление документа, Расширенный формат ответа: включить
    #print binascii.b2a_hex(hex(0b00010100)[2:])
    fg_dok = '0034'  # Оформление документа, Расширенный формат ответа: выключить
    #print _bin(int(binascii.a2b_hex('3134'), 16), 8)
    #print binascii.b2a_hex(hex(0b00000100)[2:])

    rek_kolvo = len(r)  # Количество передаваемых реквизитов
    s = binascii.b2a_hex(str(rek_kolvo))
    rek_kolvo = s+'0'*(6-len(s))

    cmd = "%(kod_msg)s%(passwd)s00%(kod_cmd)s00%(fg_dok)s00%(rek_kolvo)s00" % locals()
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()
    r.insert(0, cmd)
    cmd = ''.join(r)

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    #print 'REGKASSIR:', REGKASSIR

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except Exception, e:
        print 'cmdChek err:', str(e)
        rr = None
    return rr

def cmdChekReturn(tovary, skidka=0, passwd=PASSWD):
    """Запрос «Фискальный документ»: Возврат
    Пример использования
    cmdChek([100, (u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 7)
"""
    r = []

    rek_tip = '01'  # Наименование учреждения, строка 1
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 0  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()


    rek_tip = '02'  # Наименование учреждения, строка 2
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    #print binascii.a2b_hex('3000')
    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    #print binascii.a2b_hex('310000')
    moveY = 1  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303200303032300030000031000000"


    rek_tip = '03'  # Наименование учреждения, строка 3
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 2  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303300303032300030000032000000"


    rek_tip = '04'  # Наименование учреждения, строка 4
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 3  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303400303032300030000033000000"

    r.append(cmdTxt(4, 0, u'-'*40))

    r.append(cmdTxt(5, 0, u'ККМ'))

   #print  binascii.a2b_hex('3036')
    rek_tip = '06'  # Номер кассира
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 4  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303600303032300030000031300000'


    rek_tip = '00'  # Номер ККМ
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 6  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 5  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303000303032300030000035000000"

    r.append(cmdTxt(5, 33, u'ВОЗВРАТ'))


    #print  binascii.a2b_hex('3130')
    rek_tip = '10'  # ИНН
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "313000303032300030000036000000"


    r.append(cmdTxt(6, 30, u'Док№'))

    #print  binascii.a2b_hex('3037')
    rek_tip = '07'  # Номер документа
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 6  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303700303032300030000038000000'


    #print  binascii.a2b_hex('3035')
    rek_tip = '05'  # Дата совершения операции и Время совершения операции
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print "303500303032300030000037000000"


    r.append(cmdTxt(7, 30, u'Чек№'))

    #print  binascii.a2b_hex('3038')
    rek_tip = '08'  # Номер чека
    rek_tip = binascii.b2a_hex(rek_tip)

    fg_rek = '30303230' # Флаги реквизита
    #print _bin(int(binascii.a2b_hex(fg_rek), 16))
    #print _bin(0b0000000000100000)  # Использовать шрифты по умолчанию: lf

    moveX = 35  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = 7  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '303800303032300030000039000000'

    posIndex = 8
    r.append(cmdTxt(posIndex, 0, u'-'*40))

    chekSum = 0.0
    for tovar, kolvo, cena in tovary:
        chekSum+=kolvo*cena
        posIndex+=1
        r.append(cmdTxt(posIndex, 0, tovar))
        posIndex+=1
        r.append(cmdCena(posIndex, 0, kolvo, cena))
    if skidka:
        skidkaSum = round(chekSum * skidka / 100.0, 2)
        chekSum-=skidkaSum

    posIndex+=1
    if skidka:
        #print binascii.a2b_hex('3231')
        rek_tip = '21'  # Общая скидка/надбавка чек
        rek_tip = binascii.b2a_hex(rek_tip)

        fg_rek = '30304130' # Флаги реквизита
        #print _bin(int(binascii.a2b_hex(fg_rek), 16))
        #print _bin(0b0000000010100000)  # Использовать шрифты по умолчанию: Да; Для реквизитов "Цена услуги", Надбавка "Общая скидка/надбавка на чек"

        moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
        s = binascii.b2a_hex(str(moveX))
        moveX = s+'0'*(4-len(s))

        posIndex+=1
        moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
        s = binascii.b2a_hex(str(moveY))
        moveY = s+'0'*(6-len(s))

        rek_nm = '%.2f' % skidka  # Процент скидки Собственно реквизит строка
        s = binascii.b2a_hex(rek_nm.encode('866'))
        rek_nm = s+'0'*(80-len(s))

        cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
        r.append(cmd)
        #print cmd
        #print '3231003030413000300000313500000000000000'

    posIndex+=1
    rek_tip = binascii.b2a_hex('12')  # Итоговая сумма
    fg_rek = '30303230' # Флаги реквизита

    moveX = 0  # Смещение реквизита по горизонтали в символах от начала печати
    s = binascii.b2a_hex(str(moveX))
    moveX = s+'0'*(4-len(s))

    moveY = posIndex  # Смещение реквизита по вертикали в строках от начала печати
    s = binascii.b2a_hex(str(moveY))
    moveY = s+'0'*(6-len(s))

    rek_nm = binascii.b2a_hex("\x00"*40)  # Собственно реквизит строка

    cmd = "%(rek_tip)s00%(fg_rek)s00%(moveX)s00%(moveY)s000000000000%(rek_nm)s00" % locals()
    r.append(cmd)
    #print cmd
    #print '313200303032300030000031360000'


    # Head
    kod_msg = '53'
    kod_cmd = '31'  # Возврат

    #fg_dok = '3134'  # Оформление документа, Расширенный формат ответа: включить
    #print binascii.b2a_hex(hex(0b00010100)[2:])
    fg_dok = '0034'  # Оформление документа, Расширенный формат ответа: выключить
    #print _bin(int(binascii.a2b_hex('3134'), 16), 8)
    #print binascii.b2a_hex(hex(0b00000100)[2:])

    rek_kolvo = len(r)  # Количество передаваемых реквизитов
    s = binascii.b2a_hex(str(rek_kolvo))
    rek_kolvo = s+'0'*(6-len(s))

    cmd = "%(kod_msg)s%(passwd)s00%(kod_cmd)s00%(fg_dok)s00%(rek_kolvo)s00" % locals()
    #print "5330303030003000313400323000003031003030323000300000300000000000000000%(rek_nm)s00" % locals()
    r.insert(0, cmd)
    cmd = ''.join(r)

    global REGKASSIR
    if not REGKASSIR:
        rr = cmdRegKassir(passwd=passwd)
        REGKASSIR = '0000' == rr[0]

    global LASTRESPONS
    rr = None
    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            #if '0000' == rr[0]:
            #    r = LASTRESPONS
    except:
        rr = None
    return rr

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
    respons_cmd = binascii.a2b_hex(r[14:22]).upper()

    #~ print 'A:', r
    #~ print u'Выполненая команда', r[:2] # выполненая команда
    #~ #print binascii.a2b_hex(r[4:12])  # текущий статус ккм
    #~ print u'Текущий статус ккм'
    #~ st = _bin(int(binascii.a2b_hex(r[4:12]), 16), 16, True)
    #~ for i in statKKM:
        #~ k = i[1]
        #~ if 1 == len(i[0]):
            #~ v = int(st[i[0][0]])
        #~ else:
            #~ v = ''.join(reversed(st[i[0][0]:i[0][1]+1]))
        #~ print ' ', k, ':', i[2][v], '=', v
    #~ respons_cmd = binascii.a2b_hex(r[14:22]).upper()
    #~ print resultKKM.get(respons_cmd, respons_cmd), respons_cmd  # результат выполнения команды
    #st = _bin(int(binascii.a2b_hex(r[24:28]), 16), 8, True)
    #print u'Текущий статус принтера:', st, len(statPRN)
    #for i in [3,6,7]:  # statPRN:
    #    i = statPRN[i]
    #    k = i[1]
    #    v = int(st[i[0][0]])
    #    print '  %01d' % i[0], k, ':', i[2][v], v

    if respons_cmd:
        return respons_cmd, resultKKM.get(respons_cmd, respons_cmd)  # результат выполнения команды
    else:
        return -1, u'нет связи'

def cmdRegKassir(passwd=PASSWD):
    """Запрос «Регистрация кассира»"""
    global LASTRESPONS
    rr = None

    kod_msg = '31'

    kod_kassir = '0'
    s = binascii.b2a_hex(kod_kassir)
    kod_kassir = s+'0'*(4-len(s))

    nm_kassir = u'Касса'
    s = binascii.b2a_hex(nm_kassir.encode('866'))
    nm_kassir = s+'0'*(80-len(s))

    cmd = "%(kod_msg)s%(passwd)s00%(kod_kassir)s00%(nm_kassir)s00" % locals()

    try:
        rr = sendCmd(cmd)
        if 0 == rr[0]:
            rr = getRespons()
            if '0000' == rr[0]:
                r = LASTRESPONS
    except:
        rr = None
    return rr

########################################################################

def main():
    #while True:
    #    rr = cmdGetKkmNo()
    #    if rr:
    #        print rr[0], rr[1]
    #    else:
    #        u'нет связи'
        #for r in rr:
        #    print r
        #rr = getRespons()
        #print rr[0], rr[1]
        #time.sleep(1)

    #text = u'Привет1\nПривет2\nПокаПока3\nПокаПока4'
    #sendPrint(u'    Манускрипт Солюшн\n  -=в с е   н у ж н о е   п р о с т о=-', True)

    #rr = cmdDrawer()
    #print rr[0], rr[1]

    #print cmdSkip()

    #time.sleep(0.3)
    # Прогнать и отрезать
    #sendCmd('52%s00303500303100' % PASSWD)

    #print cmdPovtoritOtvet()

    #rr = cmdCancel()
    #print rr[0], rr[1]

    #rr = cmdGetKkmNo()
    #for r in rr:
    #    print r

    #rr = cmdGetDT()
    #print rr

    #rr = cmdSetDT()
    #if '0000' == rr[0]:
    #    print cmdGetDT()
    #else:
    #    print rr[0], rr[1]

    #rr = cmdRegKassir()
    #print rr[0], rr[1]

    #print cmdSumIN(123.45)
    #print cmdSumOUT(23.45)

    #cmdChek(50.0, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 5)
    #rr = cmdChek(3, [(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.60), (u'Товар3', 3, 0.41)], 3)
    #print rr[0], rr[1]

    #rr = cmdPovtoritOtvet()
    #print rr[0], rr[1]

    #cmdChekReturn([(u'Товар1', 1, 1.23), (u'Товар2', 2, 0.45)], 0)

    #rr = cmdX()
    #print rr[0], rr[1]

    #rr = cmdZ()
    #print rr[0], rr[1]
    pass

if __name__ == '__main__':
    main()
    sys.exit()

""" Продажа
Џа®¤ ¦ ...
00000000:  02 5C 30 30 30 30 00 33  32 39 00 42 41 03 02 5C  і .\0000.329.BA..\
00000010:  30 30 30 30 00 33 32 39  00 42 41 03 02 5C 30 30  і 0000.329.BA..\00
00000020:  30 30 00 33 33 30 00 42  32 03 02 5C 30 30 30 30  і 00.330.B2..\0000
00000030:  00 33 33 31 00 42 33 03  02 5C 30 30 30 30 00 33  і .331.B3..\0000.3
00000040:  33 32 00 42 34 03 02 5C  30 30 30 30 00 33 32 39  і 32.B4..\0000.329
00000050:  00 42 41 03 02 5C 30 30  30 30 00 33 32 39 00 42  і .BA..\0000.329.B
00000060:  41 03 02 5C 30 30 30 30  00 33 33 30 00 42 32 03  і A..\0000.330.B2.
00000070:  02 5C 30 30 30 30 00 33  33 30 00 42 32 03 02 5C  і .\0000.330.B2..\
00000080:  30 30 30 30 00 33 33 31  00 42 33 03 02 5C 30 30  і 0000.331.B3..\00
00000090:  30 30 00 33 33 31 00 42  33 03 02 5C 30 30 30 30  і 00.331.B3..\0000
000000A0:  00 33 33 32 00 42 34 03  02 5C 30 30 30 30 00 33  і .332.B4..\0000.3
000000B0:  33 32 00 42 34 03 02 4A  30 30 30 30 00 30 41 03  і 32.B4..J0000.0A.

000000C0:  02 53 30 30 30 30 00 30  00 31 34 00 32 30 00 00  і .S0000.0.14.20..
           Тип реквизита3
                    Флаги реквизита5
                                    Смещение реквизита по горизонтали в символах от начала печати3
                                             Смещение реквизита по вертикали в строках от начала печати4
000000D0:  30 31 00 30 30 32 30 00  30 00 00 30 00 00 00 00  і 01.0020.0..0....
000000E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                                   Тип реквизита3
00000100:  00 00 00 00 00 00 00 00  00 00 00 00 00 30 32 00  і .............02.
00000110:  30 30 32 30 00 30 00 00  31 00 00 00 00 00 00 00  і 0020.0..1.......
00000120:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000130:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                          Тип реквизита3
00000140:  00 00 00 00 00 00 00 00  00 00 30 33 00 30 30 32  і ..........03.002
00000150:  30 00 30 00 00 32 00 00  00 00 00 00 00 00 00 00  і 0.0..2..........
00000160:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000170:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                Тип реквизита3
00000180:  00 00 00 00 00 00 00 30  34 00 30 30 32 30 00 30  і .......04.0020.0
00000190:  00 00 33 00 00 00 00 00  00 00 00 00 00 00 00 00  і ..3.............
000001A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                       Тип реквизита3
                                Флаги реквизита5
000001C0:  00 00 00 00 39 39 00 30  30 32 30 00 30 00 00 34  і ....99.0020.0..4
000001D0:  00 00 00 00 00 00 00 00  3D 3D 3D 3D 3D 3D 3D 3D  і ........========
000001E0:  3D 3D 3D 3D 3D 3D 3D 3D  3D 3D 3D 3D 3D 3D 3D 3D  і ================
000001F0:  3D 3D 3D 3D 3D 3D 3D 3D  3D 3D 3D 3D 3D 3D 3D 3D  і ================
              Тип реквизита3
                       Флаги реквизита5
00000200:  00 30 30 00 30 30 32 30  00 30 00 00 35 00 00 00  і .00.0020.0..5...
00000210:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000220:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                                      Тип реквизита3
00000230:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 31 30  і ..............10
00000240:  00 30 30 32 30 00 30 00  00 36 00 00 00 00 00 00  і .0020.0..6......
00000250:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000260:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                             Тип реквизита3
00000270:  00 00 00 00 00 00 00 00  00 00 00 30 35 00 30 30  і ...........05.00
00000280:  32 30 00 30 00 00 37 00  00 00 00 00 00 00 00 00  і 20.0..7.........
00000290:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                    Тип реквизита3
000002B0:  00 00 00 00 00 00 00 00  30 37 00 30 30 32 30 00  і ........07.0020.
000002C0:  30 00 00 38 00 00 00 00  00 00 00 00 00 00 00 00  і 0..8............
000002D0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                          Тип реквизита3
000002F0:  00 00 00 00 00 30 38 00  30 30 32 30 00 30 00 00  і .....08.0020.0..
00000300:  39 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і 9...............
00000310:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000320:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                 Тип реквизита3
00000330:  00 00 30 36 00 30 30 32  30 00 30 00 00 31 30 00  і ..06.0020.0..10.
00000340:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000350:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                                         Тип реквизита3
00000360:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 39  і ...............9
00000370:  39 00 30 30 32 30 00 30  00 00 31 31 00 00 00 00  і 9.0020.0..11....
00000380:  00 00 00 92 AE A2 A0 E0  31 00 00 00 00 00 00 00  і ...’®ў а1.......
00000390:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                                Тип реквизита3
000003A0:  00 00 00 00 00 00 00 00  00 00 00 00 31 31 00 30  і ............11.0
                                             Номер отдела (секции)3
                                                      Код товара7
000003B0:  30 32 32 00 30 00 00 31  32 00 00 31 00 00 30 00  і 022.0..12..1..0.
                          Процентная скидка/надбавка6
                                             Количество (вес, литры)12
000003C0:  00 00 00 00 00 00 00 00  00 00 00 34 00 00 00 00  і ...........4....
                                Цена услуги, денежная скидка, надбавка12
000003D0:  00 00 00 00 00 00 00 31  2E 32 33 00 00 00 00 00  і .......1.23.....
                    Единица измерения количества6
                                       Тип реквизита3
000003E0:  00 00 00 00 00 00 00 00  00 39 39 00 30 30 32 30  і .........99.0020
000003F0:  00 30 00 00 31 33 00 00  00 00 00 00 00 92 AE A2  і .0..13.......’®ў
00000400:  A0 E0 32 00 00 00 00 00  00 00 00 00 00 00 00 00  і  а2.............
00000410:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                             Тип реквизита3
00000420:  00 00 00 00 00 00 31 31  00 30 30 32 32 00 30 00  і ......11.0022.0.
00000430:  00 31 34 00 00 31 00 00  30 00 00 00 00 00 00 00  і .14..1..0.......
00000440:  00 00 00 00 00 37 00 00  00 00 00 00 00 00 00 00  і .....7..........
00000450:  00 34 2E 35 36 00 00 00  00 00 00 00 00 00 00 00  і .4.56...........
                    Тип реквизита3
                             Флаги реквизита5
                                             Смещение реквизита по горизонтали в символах от начала печати3
                                                      Смещение реквизита по вертикали в строках от начала печати4

00000460:  00 00 00 32 31 00 30 30  41 30 00 30 00 00 31 35  і ...21.00A0.0..15
00000470:  00 00 00 00 00 00 00 33  2E 30 30 00 00 00 00 00  і .......3.00.....
00000480:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000490:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
           Тип реквизита3 Итоговая сумма
000004A0:  31 32 00 30 30 32 30 00  30 00 00 31 36 00 00 00  і 12.0020.0..16...
000004B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000004C0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                                   Тип реквизита3 Сумма налогов по налоговой ставке 0
000004D0:  00 00 00 00 00 00 00 00  00 00 00 00 00 31 35 00  і .............15.
000004E0:  30 30 32 30 00 30 00 00  31 37 00 00 00 00 00 00  і 0020.0..17......
000004F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000500:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                          Тип реквизита3 Уплаченная сумма
00000510:  00 00 00 00 00 00 00 00  00 00 31 33 00 30 30 32  і ..........13.002
00000520:  30 00 30 00 00 31 38 00  00 00 00 00 00 00 31 30  і 0.0..18.......10
00000530:  30 2E 30 30 00 00 00 00  00 00 00 00 00 00 00 00  і 0.00............
00000540:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                                Тип реквизита3 Сумма сдачи
00000550:  00 00 00 00 00 00 00 31  34 00 30 30 32 30 00 30  і .......14.0020.0
00000560:  00 00 31 39 00 00 00 00  00 00 00 00 00 00 00 00  і ..19............
00000570:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000580:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
                             Конец запроса
00000590:  00 00 00 00 34 41 03 02  5C 30 30 30 30 00 33 30  і ....4A..\0000.30
000005A0:  36 00 42 35 03                                    і 6.B5.
ответ
Џа®¤ ¦ ...
00000000:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000010:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000020:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000030:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000040:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000050:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000060:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000070:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000080:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000090:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
000000A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
000000C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000000D0:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
000000E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
00000100:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000110:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
00000120:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000130:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000140:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000150:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000160:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000170:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000180:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000190:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
000001A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
000001C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000001D0:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
000001E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
00000200:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000210:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
00000220:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000230:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
00000240:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000250:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
00000260:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000270:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
00000280:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000290:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
000002A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
000002C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000002D0:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
000002E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000300:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000310:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
00000320:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000330:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000340:  02 4A 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .J.fc13.0000.4e.
00000350:  30 30 00 30 30 32 38 32  00 31 35 30 32 32 30 31  і 00.00282.1502201
00000360:  31 00 31 39 31 35 00 30  34 00 30 2E 30 30 00 00  і 1.1915.04.0.00..
00000370:  00 00 00 00 00 00 00 00  00 00 30 30 30 30 32 00  і ..........00002.
00000380:  30 30 30 30 34 00 39 30  03 06 06 06 06 06 06 06  і 00004.90........
00000390:  06 06 06 06 06 06 06 02  53 00 66 63 31 33 00 30  і ........S.fc13.0
000003A0:  30 30 30 00 34 65 00 30  30 00 30 30 32 38 33 00  і 000.4e.00.00283.
000003B0:  31 35 30 32 32 30 31 31  00 31 39 32 33 00 30 30  і 15022011.1923.00
000003C0:  00 33 35 2E 37 33 00 00  00 00 00 00 00 00 00 00  і .35.73..........
000003D0:  00 30 30 30 30 33 00 00  00 00 00 00 00 65 34 03  і .00003.......e4.
000003E0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000003F0:  33 30 36 00 33 34 34 30  30 30 30 30 30 30 00 00  і 306.3440000000..
00000400:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000410:  00 00 00 00 00 00 00 00  00 00 00 00 00 36 36 03  і .............66.
"""
""" Выплата
‚лЇ« в ...
00000000:  02 5C 30 30 30 30 00 33  32 39 00 42 41 03 02 5C  і .\0000.329.BA..\
00000010:  30 30 30 30 00 33 32 39  00 42 41 03 02 5C 30 30  і 0000.329.BA..\00
00000020:  30 30 00 33 33 30 00 42  32 03 02 5C 30 30 30 30  і 00.330.B2..\0000
00000030:  00 33 33 31 00 42 33 03  02 5C 30 30 30 30 00 33  і .331.B3..\0000.3
00000040:  33 32 00 42 34 03 02 5C  30 30 30 30 00 33 32 39  і 32.B4..\0000.329
00000050:  00 42 41 03 02 5C 30 30  30 30 00 33 32 39 00 42  і .BA..\0000.329.B
00000060:  41 03 02 5C 30 30 30 30  00 33 33 30 00 42 32 03  і A..\0000.330.B2.
00000070:  02 5C 30 30 30 30 00 33  33 30 00 42 32 03 02 5C  і .\0000.330.B2..\
00000080:  30 30 30 30 00 33 33 31  00 42 33 03 02 5C 30 30  і 0000.331.B3..\00
00000090:  30 30 00 33 33 31 00 42  33 03 02 5C 30 30 30 30  і 00.331.B3..\0000
000000A0:  00 33 33 32 00 42 34 03  02 5C 30 30 30 30 00 33  і .332.B4..\0000.3
000000B0:  33 32 00 42 34 03 02 4A  30 30 30 30 00 30 41 03  і 32.B4..J0000.0A.
000000C0:  02 53 30 30 30 30 00 33  00 31 34 00 31 33 00 00  і .S0000.3.14.13..
000000D0:  30 31 00 30 30 32 30 00  30 00 00 30 00 00 00 00  і 01.0020.0..0....
000000E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000100:  00 00 00 00 00 00 00 00  00 00 00 00 00 30 32 00  і .............02.
00000110:  30 30 32 30 00 30 00 00  31 00 00 00 00 00 00 00  і 0020.0..1.......
00000120:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000130:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000140:  00 00 00 00 00 00 00 00  00 00 30 33 00 30 30 32  і ..........03.002
00000150:  30 00 30 00 00 32 00 00  00 00 00 00 00 00 00 00  і 0.0..2..........
00000160:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000170:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000180:  00 00 00 00 00 00 00 30  34 00 30 30 32 30 00 30  і .......04.0020.0
00000190:  00 00 33 00 00 00 00 00  00 00 00 00 00 00 00 00  і ..3.............
000001A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001C0:  00 00 00 00 39 39 00 30  30 32 30 00 30 00 00 34  і ....99.0020.0..4
000001D0:  00 00 00 00 00 00 00 00  3D 3D 3D 3D 3D 3D 3D 3D  і ........========
000001E0:  3D 3D 3D 3D 3D 3D 3D 3D  3D 3D 3D 3D 3D 3D 3D 3D  і ================
000001F0:  3D 3D 3D 3D 3D 3D 3D 3D  3D 3D 3D 3D 3D 3D 3D 3D  і ================
00000200:  00 30 30 00 30 30 32 30  00 30 00 00 35 00 00 00  і .00.0020.0..5...
00000210:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000220:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000230:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 31 30  і ..............10
00000240:  00 30 30 32 30 00 30 00  00 36 00 00 00 00 00 00  і .0020.0..6......
00000250:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000260:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000270:  00 00 00 00 00 00 00 00  00 00 00 30 35 00 30 30  і ...........05.00
00000280:  32 30 00 30 00 00 37 00  00 00 00 00 00 00 00 00  і 20.0..7.........
00000290:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002B0:  00 00 00 00 00 00 00 00  30 37 00 30 30 32 30 00  і ........07.0020.
000002C0:  30 00 00 38 00 00 00 00  00 00 00 00 00 00 00 00  і 0..8............
000002D0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002F0:  00 00 00 00 00 30 38 00  30 30 32 30 00 30 00 00  і .....08.0020.0..
00000300:  39 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і 9...............
00000310:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000320:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000330:  00 00 30 36 00 30 30 32  30 00 30 00 00 31 30 00  і ..06.0020.0..10.
00000340:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000350:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000360:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 31  і ...............1
00000370:  31 00 30 30 32 32 00 30  00 00 31 31 00 00 00 00  і 1.0022.0..11....
00000380:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000390:  00 00 00 00 00 00 00 00  00 00 31 30 2E 35 35 00  і ..........10.55.
000003A0:  00 00 00 00 00 00 00 00  00 00 00 00 31 32 00 30  і ............12.0
000003B0:  30 32 30 00 30 00 00 31  32 00 00 00 00 00 00 00  і 020.0..12.......
000003C0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000003D0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000003E0:  00 00 00 00 00 00 00 00  00 32 42 03 02 5C 30 30  і .........2B..\00
000003F0:  30 30 00 33 30 36 00 42  35 03                    і 00.306.B5.
ответ
‚лЇ« в ...
00000000:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000010:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000020:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000030:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000040:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000050:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000060:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000070:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000080:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000090:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
000000A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
000000C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000000D0:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
000000E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000000F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
00000100:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000110:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
00000120:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000130:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000140:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000150:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
00000160:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000170:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
00000180:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000190:  33 32 39 00 30 00 00 00  00 00 00 00 00 00 00 00  і 329.0...........
000001A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 62 30 03  і .............b0.
000001C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000001D0:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
000001E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000001F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
00000200:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000210:  33 33 30 00 30 00 00 00  00 00 00 00 00 00 00 00  і 330.0...........
00000220:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000230:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 38 03  і .............a8.
00000240:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000250:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
00000260:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000270:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
00000280:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000290:  33 33 31 00 30 00 00 00  00 00 00 00 00 00 00 00  і 331.0...........
000002A0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002B0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 39 03  і .............a9.
000002C0:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
000002D0:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
000002E0:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
000002F0:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000300:  02 5C 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .\.fc13.0000.4e.
00000310:  33 33 32 00 30 00 00 00  00 00 00 00 00 00 00 00  і 332.0...........
00000320:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000330:  00 00 00 00 00 00 00 00  00 00 00 00 00 61 61 03  і .............aa.
00000340:  02 4A 00 66 63 31 33 00  30 30 30 30 00 34 65 00  і .J.fc13.0000.4e.
00000350:  30 30 00 30 30 32 38 33  00 31 35 30 32 32 30 31  і 00.00283.1502201
00000360:  31 00 31 39 32 33 00 30  30 00 33 35 2E 37 33 00  і 1.1923.00.35.73.
00000370:  00 00 00 00 00 00 00 00  00 00 30 30 30 30 33 00  і ..........00003.
00000380:  00 00 00 00 00 00 64 62  03 06 06 06 06 06 06 06  і ......db........
00000390:  06 06 02 53 00 66 63 31  33 00 30 30 30 30 00 34  і ...S.fc13.0000.4
000003A0:  65 00 30 30 00 30 30 32  38 34 00 31 35 30 32 32  і e.00.00284.15022
000003B0:  30 31 31 00 31 39 33 33  00 30 33 00 31 30 2E 35  і 011.1933.03.10.5
000003C0:  35 00 00 00 00 00 00 00  00 00 00 00 30 30 30 30  і 5...........0000
000003D0:  34 00 00 00 00 00 00 00  65 33 03 02 5C 00 66 63  і 4.......e3..\.fc
000003E0:  31 33 00 30 30 30 30 00  34 65 00 33 30 36 00 33  і 13.0000.4e.306.3
000003F0:  34 34 30 30 30 30 30 30  30 00 00 00 00 00 00 00  і 440000000.......
00000400:  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  і ................
00000410:  00 00 00 00 00 00 00 00  36 36 03                 і ........66.
"""
