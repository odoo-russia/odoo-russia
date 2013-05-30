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
{   'name': 'Russia - Accounting',
    'version': '1.0',
    'category': 'Localization/Account Charts',
    'description': """
This is the base module to manage the accounting chart for Russia in OpenERP.
""",
    'author': 'OpenERP Russian Localization Team',
    'depends': ['base', 'account', 'account_chart'],
    'init_xml': [],
    'update_xml': [
        'data/account.account.type.csv',
        'data/account.account.template.csv',
        'data/account.tax.code.template.csv',
        'data/l10n_ru_account_chart_template.xml',
	'data/res.country.state.csv',
	"data/res.partner.title.csv",
        "l10n_ru_view.xml",
    ],
    'demo_xml': [],
    'installable': True,
    'images': [],
}


