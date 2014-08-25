#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import sys, os, time
from xml.dom.minidom import parse, parseString
from xml.sax.saxutils import escape as xmlescape

__version__ = '2012.0725'
# починил в драйвере Атол установку времени и возвратный чек

__version__ = '2011.1107'
# добавил пробивку чека по другим видам оплаты в драйвере Штрих-М

#__version__ = '2011.0714'
# исправлена пробивка чека в драйвере Штрих-М

#__version__ = '2011.0324'
try:
    awsPortNo = sys.argv[1]
except:
    awsPortNo = '8080'
fileconf = os.path.dirname(os.path.abspath(__file__)) + os.sep + 'aws%s.conf' % awsPortNo
print 'ver:', __version__
print 'cnf:', os.path.basename(fileconf)

if os.path.isfile(fileconf):
    with open(fileconf, 'rb') as f:
        CONF = eval(f.read())
else:
    CONF = {'kkmdefault': 'cdx2', 'port': '/dev/ttyS4', 'baudrate': 9600}
    with open(fileconf, 'wb') as f:
        f.write(str(CONF))
#print 'CONF:', CONF
KKM = {}
for i, nm in enumerate(('cdxGEPARD', 'cdxSHTRIX', 'cdxATOL')):
    nm_kkm = 'kkm%s' % (i+1)
    nm_cdx = 'cdx%s' % (i+1)
    if nm_cdx == CONF['kkmdefault']:
        print '*',
    else:
        print ' ',
    try:
        KKM[nm_cdx] = __import__(nm)
        KKM[nm_kkm] = KKM[nm_cdx]
        KKM[nm_kkm].PORT = CONF['port']
        KKM[nm_kkm].BAUDRATE = CONF['baudrate']
    except Exception, e:
        print 'err:', str(e)

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def kkmExec(kkm, xml):
    #~ print '-'*32
    #~ print xml
    #~ with open('/tmp/kkm.log', 'a') as f:
        #~ f.write(xml)
        #~ f.write('\n\n')
    #~ print '='*32

    fg_clear_lastcmd = True
    #rr = (-2, 'command is not implemented')
    rr = (-2, u'команда не реализована')
    fc = parseString(xml).firstChild
    nm_func = fc.getAttribute('name')
    rq = fc.firstChild
    #if rq:
    #    print rq.nodeName, rq.getAttribute('handle')
    if 'open' == nm_func:
        #print nm_func
        rr = ('0000', 'OK')
    elif 'properties' == nm_func:
        pl = rq.firstChild
        pl_method = pl.getAttribute('method')
        if 'set' == pl_method:
            d, t = getText(pl.firstChild.childNodes).split('T')
            dt = tuple(map(int, d.split('-') + t.split('.')[0].split(':')[:3]))
            rr = kkm.cmdSetDT(dt)
        else:
            #print nm_func, pl.nodeName
            fg_respons = False
            for node in pl.childNodes:
                if 'NumKKM' == node.nodeName:
                    fg_clear_lastcmd = False
                    #kkm.LASTCMD = ['', 0, time.localtime(), time.localtime(), None]
                    cmdNm = 'cmdGetKkmNo'
                    if cmdNm <> kkm.LASTCMD[0] or kkm.LASTCMD[1] > 4:
                        kkm.LASTCMD[0] = cmdNm
                        kkm.LASTCMD[1] = 0
                        kkm.LASTCMD[2] = time.localtime()
                        kkm.LASTCMD[3] = None
                        #rr = kkm.cmdGetKkmNo()
                        fg = 1
                        while fg:
                            fg+=1
                            rr = kkm.__dict__[cmdNm]()
                            #print fg, rr, kkm.__name__
                            if rr:
                                if not (rr[0] in ['001E', '009E']):  # для Меркурия
                                    fg = 0
                                    time.sleep(1)
                        kkm.LASTCMD[4] = rr
                        #rr = kkm.__dict__[cmdNm]()
                    else:
                        rr = kkm.LASTCMD[4]
                    if len(rr) > 2:
                        text = node.ownerDocument.createTextNode(rr[0])
                        node.appendChild(text)
                        fg_respons = True
                    else:
                        # Команда выполнелась с ошибкой, запоминать не надо.
                        #fg_clear_lastcmd = True
                        pass
                    kkm.LASTCMD[1]+=1
                    kkm.LASTCMD[3] = time.localtime()
                #print node.nodeName
            if fg_respons:
                rr = ('0000', 'OK', pl.toxml('1251'))
            #else:
            #    rr = ('0000', 'OK')
            #print rr
    elif 'sum' == nm_func:
        rq_action = rq.getAttribute('action')
        if 'out' == rq_action:
            rr = kkm.cmdSumOUT(float(getText(rq.childNodes)))
        elif 'in' == rq_action:
            rr = kkm.cmdSumIN(float(getText(rq.childNodes)))
    elif 'report' == nm_func:
        rq_name = rq.getAttribute('name')
        if 'PrintString' == rq_name:
            #print 'PrintString:', rq.getAttribute('text')
            rr = kkm.cmdPrint(rq.getAttribute('text'))
            rr = ('0000', 'OK')
        elif 'X' == rq_name:
            print 01010101, rq.getAttribute('sumDiscount'), type(rq.getAttribute('sumDiscount')) ##########
            sumDiscount = float(rq.getAttribute('sumDiscount'))
            if sumDiscount > 0:
                kkm.cmdPrint(u'СКИДКА%14.2f' % sumDiscount)
            rr = kkm.cmdX()
        elif 'S' == rq_name:
            sumDiscount = float(rq.getAttribute('sumDiscount'))
            if sumDiscount > 0:
                kkm.cmdPrint(u'СКИДКА%14.2f' % sumDiscount)
            rr = kkm.cmdX()
            pass
        elif 'Z' == rq_name:
            sumDiscount = float(rq.getAttribute('sumDiscount'))
            if sumDiscount > 0:
                kkm.cmdPrint(u'СКИДКА%14.2f' % sumDiscount)
            rr = kkm.cmdZ()
            kkm.REGKASSIR = False
            pass
    elif 'print' == nm_func:
        rq_method = rq.getAttribute('method')
        if 'check' == rq_method:
            #print rq_method
            pl = rq.firstChild
            pl_method = pl.getAttribute('method')
            if 'sale' == pl_method:
                #print pl.nodeName, pl_method
                tovary = []
                for node in pl.childNodes:
                    if 'product' == node.nodeName:
                        tovary.append((getText(node.childNodes), float(node.getAttribute('quantity')), float(node.getAttribute('price'))))
                        #print node.getAttribute('section')
                discount = float(pl.getAttribute('DiscountValue'))
                if discount < 0:
                    discount = abs(discount)
                try:
                    vidopl = int(pl.getAttribute('VidOpl'))
                except:
                    vidopl = 0
                if vidopl:
                    rr = kkm.cmdChek([float(pl.getAttribute('CashValue')), vidopl], tovary, discount)
                else:
                    rr = kkm.cmdChek(float(pl.getAttribute('CashValue')), tovary, discount)
                #print 'rr = kkm.cmdChek:', rr
            elif 'return' == pl_method:
                #print pl.nodeName, pl_method
                tovary = []
                for node in pl.childNodes:
                    if 'product' == node.nodeName:
                        tovary.append((getText(node.childNodes), float(node.getAttribute('quantity')), float(node.getAttribute('price'))))
                        #print node.getAttribute('section')
                discount = float(pl.getAttribute('DiscountValue'))
                if discount < 0:
                    discount = abs(discount)
                rr = kkm.cmdChekReturn(tovary, discount)
        elif 'repeat' == rq_method:
            kkm.cmdCancel()
            time.sleep(0.25)
            rr = kkm.cmdCopyDoc()
        elif 'skip' == rq_method:
            rr = kkm.cmdSkip()
#/получение выручки из Х-отчета Igor` добавил 04.04.2013
        elif 'virychka' == rq_method:
            res = kkm.getCachReg()
            rr = ('0000', 'OK', res)
            print rr, res
#/получение номера последнего чека Igor` добавил 04.04.2013
        elif 'num_chek' == rq_method:
            res = kkm.getOperReg()
            rr = ('0000', 'OK', res)
            #~ print rr, res
        elif 'connec' == rq_method:
            rr = kkm.cmdCachReg(regNumber = 5)
#\
        elif 'drawer' == rq_method:
            rr = kkm.cmdDrawer()
            #print rq_method, rr
        elif 'cancel' == rq_method:
            #print rq_method
            rr = kkm.cmdCancel()
            rr = ('0000', 'OK')
        #print 'rr0 = kkm.cmdChek:', rq_method, rr

    if fg_clear_lastcmd:
        kkm.LASTCMD[0] = ''
        kkm.LASTCMD[1] = 0
        kkm.LASTCMD[2] = None
        kkm.LASTCMD[3] = None

    if '0000' <> rr[0]:
        print '-' * 40
        print xml
        print '=' * 40
        print rr
        print '#' * 40
    return rr

#~ xml = open('data/20110218-165810.xml', 'rb').read()
#~ while True:
    #~ rr = kkmExec(xml)
    #~ print rr
    #~ time.sleep(1)
#~ sys.exit()


########################################################################

import web
#web.config.debug = False

urls = [
    '(.*)/cdx', 'cdx',
    '(.*)/kkm', 'cdx',
    '/save(.*)', 'save',

    '(.*)/cdx1', 'cdx1',
    '(.*)/kkm1', 'cdx1',

    '(.*)/cdx2', 'cdx2',
    '(.*)/kkm2', 'cdx2',

    '(.*)/cdx3', 'cdx3',
    '(.*)/kkm3', 'cdx3',

    '(.*)', 'cdx',
]

class save(object):
    def GET(self, name):
        #i = web.input()
        #print i.keys()
        #web.header('Content-type', 'text/html; charset=utf-8')
        #return '111'
        self.POST(name)

    def POST(self, name):
        #print 'POST save1'
        #data = web.data()
        #print len(data), data
        i = web.input(kkmdefault=CONF['kkmdefault'], port=CONF['port'], baudrate=CONF['baudrate'])
        #print 'POST save2'
        #print i.keys()
        CONF['kkmdefault'] = i.kkmdefault
        CONF['port'] = i.port
        CONF['baudrate'] = i.baudrate
        #print 'POST save3', CONF

        with open(fileconf, 'wb') as f:
            f.write(str(CONF).encode('utf8'))
        #web.header('Content-type', 'text/javascript; charset=utf-8')
        #return '222'
        #return '<script>alert("111")</script>'  # web.seeother('/cdx')
        #raise web.seeother('/cdx')
        raise web.redirect('/cdx')

class cdx(object):
    def __init__(self):
        self.kkm = KKM[CONF['kkmdefault']]
        self.kkm.PORT = CONF['port']
        self.kkm.BAUDRATE = CONF['baudrate']
        self.xHandle = '0xff'

    #~ def GET(self, name):
            #~ web.header('Content-type', 'text/html; charset=utf-8')
            #~ web.header('Content-encoding', 'deflate')
#~
            #~ r = u'/cdx1 Merkuriy<br/>/cdx2 Shtrih-M<br/>/cdx3 ATOL'
            #~ return r.encode('utf8').encode('zlib')

    def GET(self, name):
        web.header('Content-type', 'text/html; charset=utf-8')
        ops = u''
        for i, o in enumerate([u'Меркурий', u'Штрих', u'Атол']):
            rn = 'cdx%s' % (i+1)
            if rn == CONF['kkmdefault']:
                sel = 'selected'
                o = '*&nbsp;' + o
            else:
                sel = ''
                o = '&nbsp;&nbsp;' + o
            ops+=u'<option value="%s" %s>%s</option>' % (rn, sel, o)
        s = u'''
<html>
<body>
<form method="post" action="/save">
<select name="kkmdefault">
%s
</select>
<input type="text" name="port" value="%s"/>
<input type="text" name="baudrate" value="%s"/>
<input type="button" value="Найти" onClick="alert('Не нашол!')"/>
<input type="submit" value="Сохранить"/>
</form>
</body>
</html>
        ''' % (ops, CONF['port'], CONF['baudrate'])
        return s.encode('utf8')

    def POST(self, name):
        xml = web.data().decode('1251').encode('utf8')
        #print '*'*40
        #print xml
        #print 'self.kkm:', self.kkm.__name__, self.kkm.PORT, self.kkm.BAUDRATE
        rr = kkmExec(self.kkm, xml)
        #print rr
        #xHandle = hex(id(urls))
        if '0000' == rr[0]:
            #r = '<respons handle="%s" />' % hex(id(urls))
            r = '<respons handle="%s">%s</respons>' % (self.xHandle, rr[-1])
        elif -2 == rr[0]:
            print 'web.data:', xml
            #qnm = 'data/%04d%02d%02d-%02d%02d%02d.xml' % time.localtime()[:6]
            #with open(qnm, 'wb') as f:
            #    f.write(xml)
            #time.sleep(0.5)
            if isinstance(rr[0], int):
                rc = str(rr[0])
            else:
                rc = int(rr[0], 16)
            r = '<respons handle="%s" error="%s">%s</respons>' % (self.xHandle, rc, xmlescape(rr[1].encode('1251')))
        else:
            if isinstance(rr[0], int):
                rc = str(rr[0])
            else:
                rc = int(rr[0], 16)
            r = '<respons handle="%s" error="%s">%s</respons>' % (self.xHandle, rc, xmlescape(rr[1].encode('1251')))
        #print 'respons:', r
        return r

class cdx1(cdx):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.kkm = KKM[self.__class__.__name__]
        self.kkm.PORT = CONF['port']
        self.kkm.BAUDRATE = CONF['baudrate']
        self.xHandle = '0x01'

    def GET(self, name):
        if not name:
            return 'Merkuriy'
        else:
            return 'Hello, ' + name + '!'

class cdx2(cdx):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.kkm = KKM[self.__class__.__name__]
        self.kkm.PORT = CONF['port']
        self.kkm.BAUDRATE = CONF['baudrate']
        self.xHandle = '0x02'

    def GET(self, name):
        if not name:
            return 'Shtrih-M'
        else:
            return 'Hello, ' + name + '!'

class cdx3(cdx):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.kkm = KKM[self.__class__.__name__]
        self.kkm.PORT = CONF['port']
        self.kkm.BAUDRATE = CONF['baudrate']
        self.xHandle = '0x03'

    def GET(self, name):
        if not name:
            return 'ATOL'
        else:
            return 'Hello, ' + name + '!'

########################################################################


app = web.application(urls, globals())

if __name__ == "__main__":
    app.run()
