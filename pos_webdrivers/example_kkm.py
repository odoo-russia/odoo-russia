#!/usr/bin/env python
# -*- coding: utf-8 -*-


#Отправка запроса на драйвер
def request_print(cdx):
    try:
        r = urllib2.urlopen('http://127.0.0.1:8080/cdx', data = cdx.decode('utf8').encode('1251'))
        rr = r.read().decode('1251').encode('utf8')
        return rr
    except Exception as e:
        print datetime.datetime.now(), 'request_print', 'data', cdx, '\n', 'ERROR:', e
        return '<respons handle="0xff" error="-1">нет связи</respons>'

############### Команды ###############

#Изъять из кассы
def kkm_outSum():
    cdx = """<?xml version="1.0" ?>
        <cdx name="sum">
            <request handle="http://127.0.0.1:8080/cdx" action="out">2000</request>
        </cdx>"""
    print request_print(cdx)

#Внесите сумму в кассу
def kkm_inSum():
    cdx = """<?xml version="1.0" ?>
        <cdx name="sum">
            <request handle="http://127.0.0.1:8080/cdx" action="in">2000</request>
        </cdx>"""
    print request_print(cdx)

#Проверка работы кассы
def cdxOpen():
    cdx = """<?xml version="1.0" ?><cdx name="open"><request></request></cdx>"""
    print request_print(cdx)


#Отменить вывод
def print_cancel_check():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="cancel"/></cdx>"""
    print request_print(cdx)

#Повторить выввод последнего чека
def print_check_retry():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="repeat"/></cdx>"""
    print request_print(cdx)


#Установка даты
def KKM_SetDitetime():
    cdx = """<?xml version="1.0" ?>
<cdx name="properties">
<request handle="http://127.0.0.1:8080/cdx">
<PropertyList method="set"><DateTime>2014-01-27T10:22:51.961787</DateTime></PropertyList></request></cdx>"""
    print request_print(cdx)


#Открыть ящик
def kkm_OpenDrawer():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="drawer"/></cdx>"""
    print request_print(cdx)


#Настройки
def kkm_DopForm():
    cdx = """<?xml version="1.0" ?>
    <cdx name="Tune"><request handle="http://127.0.0.1:8080/cdx" AplicationHandle="AplicationHandle"/></cdx>"""
    print request_print(cdx)

#Прогон бумаги
def print_skip():
    cdx = """<?xml version="1.0" ?><cdx name="print"><request handle="http://127.0.0.1:8080/cdx" method="skip"/></cdx>"""
    print request_print(cdx)


#Печать Х Z отчетов
#name (X or Z or S-отчет по отделам)
def report_x_z_s():
    cdx = """<?xml version="1.0" ?><cdx name="report">
    <request handle="http://127.0.0.1:8080/cdx" name="X" sumDiscount="0.1"/></cdx>"""
    print request_print(cdx)

#Получить выручку из кассы
def GetCashReg():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="virychka"/></cdx>"""
    print request_print(cdx)

#Проверка связи с кассой
def GetConnectKKM():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="connec"/></cdx>"""
    print request_print(cdx)


#Получить номер последнего чека
def GetOperReg():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="num_chek"/></cdx>"""
    print request_print(cdx)


#Печать по строчно
def print_text():
    cdx = """<?xml version="1.0" ?>
    <cdx name="report"><request handle="http://127.0.0.1:8080/cdx" name="PrintString" text="examle text"/></cdx>"""
    print request_print(cdx)

#Печать чека
def print_check_s():
    cdx = """<?xml version="1.0" ?>
    <cdx name="print">
        <request handle="http://127.0.0.1:8080/cdx" method="check">
            <ProductList method="sale" DiscountValue="-0" CashValue="318.6" RoundValue="0" DiscountStr="0" VidOpl="0">
                <product quantity="1" price="104.6" section="1" discontstr="-0" summa="104.6" summaf="104.6">ГЕЛЬ-СМАЗКА CONTEX GREEN 30МЛ {Чешская Республика, Altermed Corporation a.s.}</product>
                <product quantity="1" price="107.0" section="1" discontstr="-0" summa="107.0" summaf="107.0">Гель-смазка Contex Plus  30мл Flash {Чешская Республика, Альтермед корпорейшн}</product>
                <product quantity="1" price="107.0" section="1" discontstr="-0" summa="107.0" summaf="107.0">Гель-смазка Contex Plus  30мл Lonq love {Чешская Республика, Альтермед корпорейшн}</product>
            </ProductList>
        </request>
    </cdx>"""
    print request_print(cdx)


#закрытие чека последнего чека
def cash_cheks():
    cdx = """<?xml version="1.0" ?><cdx name="print">
    <request handle="http://127.0.0.1:8080/cdx" method="check"/></cdx>"""
    print request_print(cdx))

#Получить номер контрольной ленты
def CheskingNumKKM():
    cdx = '<?xml version="1.0" ?><cdx name="properties"><request handel="http://127.0.0.1:8080/cdx"><PropertyList><NumKL/><NumNB/><axSum/><NumKKM/></PropertyList></request></cdx>'
    print request_print(cdx)




