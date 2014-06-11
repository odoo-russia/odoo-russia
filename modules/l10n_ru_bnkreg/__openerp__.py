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
    'name': 'Russia - Banks and regions upload',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'description': """
Возможности:
  - Справочник российских регионов
  - Дополнительный реквизит "Корр. счет" для банков
  - Автоматическая загрузка актуального справочника российских банков (пункт меню Учет-Настройки-Обновить банки, для этого нужно чтобы пользователь имел права финансового менеджера)
    """,
    'author': 'Transparent Technologies',
    'website': 'http://tterp.ru',
    'depends': ['base'],
    'data': [
        'data/res.country.state.csv',
        'l10n_ru_view.xml',
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: