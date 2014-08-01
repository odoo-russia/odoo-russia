{
    'name': 'Check quantity on hands in Stock Move, Incoming Shipments, Internal Moves and Delivery Orders',
    'version': '1.0',
    'category': 'Warehouse Management',
    'author': 'Transparent Technologies',
    'license': 'AGPL-3',
    'depends': ['stock'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'description': '''
This module checks available quantity of product on a confirmation of stock move. "Force availability" and
"Confirm & Transfer" buttons don't work after the fix. You get notification that it's not possible to send the product
because you haven't enough quantity.
    '''
}
