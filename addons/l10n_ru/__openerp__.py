# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Russia - Accounting',
    'version': '1.2',
    'category': 'Localization/Account Charts',
    'description': """
This module is the localization of OpenERP for Russian Federation.
==============================================================================
Возможности:

  - План счетов бухгалтерского учёта финансово-хозяйственной деятельности организаций, утверждённый Приказом Минфина РФ от 31.10.2000 года № 94н
  - План российских налогов
  - Справочник российских регионов
  - Справочник российских организационно-правовых форм (ООО, ЗАО, ОАО, ИП)
  - Дополнительные реквизиты партнеров на вкладке Учет (Официальное наименование, ИНН, КПП, ОКПО, Номер договора, Дата договора, Руководитель, Главный бухгалтер)
  - Дополнительный реквизит "Корр. счет" для банков
  - Автоматическая загрузка актуального справочника российских банков (пункт меню Учет-Настройки-Обновить банки, для этого нужно чтобы пользователь имел права финансового менеджера)
    """,
    'author': 'OpenERP Russian Localization Team, Transparent Technologies, CodUP',
    'website': 'https://launchpad.net/~openerp-l10n-ru, http://tterp.ru, http://codup.com',
    'images': ['images/flag_ru.png'],
    'depends': ['account'],
    'data': [
        'data/account_chart_template.xml',
        'data/account.account.template.csv',
        'data/okv.xml',
        'data/res_country_data.xml',
        'data/account.tax.template.csv',
        'data/res.country.state.csv',
        'data/res.partner.title.csv',
        'l10n_ru_view.xml',
        'data/account_chart_template_post.xml',
        'data/account_chart_template.yml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
