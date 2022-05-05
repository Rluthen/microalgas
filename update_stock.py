import xmlrpc.client
import traceback
import logging
import os
from dotenv import load_dotenv

load_dotenv() 

def update_stock(read_id, read_weight):

    url = os.getenv("URL")
    db = os.getenv("DB")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    items = [
        {
            'tag_id': 0,
            'odoo_id': 5,
            'name': 'Fosfato de sodio monopotásico (MKP) agrícola',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 6,
            'name': 'Sulfato de magnesio',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 7,
            'name': 'Sulfato ferroso agrícola',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 8,
            'name': 'Glutamato monosódico',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 9,
            'name': 'Sulfato de zinc agrícola',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 10,
            'name': 'Ácido bórico',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 11,
            'name': 'Carbonato de calcio agícola',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 12,
            'name': 'Sulfato de potasio agrícloa',
            'barrel_weight': 3.2
        },
        {
            'tag_id': 0,
            'odoo_id': 13,
            'name': 'Ácido cítrico conservador',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 14,
            'name': 'Benzonato de sodio conservador',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 15,
            'name': 'Sorbato de potasio',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 16,
            'name': 'Bicarbonato de sodio agrícola',
            'barrel_weight': 2.42
        },
        {
            'tag_id': 0,
            'odoo_id': 17,
            'name': 'Nitrato de sodio/potasio',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 18,
            'name': 'Cloruro de sodio agrícola',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 19,
            'name': 'Bicarbonato de amonio agrícola',
            'barrel_weight': 2.4
        },
        {
            'tag_id': 0,
            'odoo_id': 20,
            'name': 'urea',
            'barrel_weight': 2.4
        }
    ]

    read_qty = read_weight
    read_tag_id = read_id
    item = {}


    # Datos del item leido
    for x in items:
        if x['tag_id'] == read_tag_id:
            print(x)
            item = x
    if item == {}:
        raise
    try:
        # Usar endpoint /common para conseguir UID de usuario para usar despues
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})

        # Usar endpoint /object para operaciones sobre los datos
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        # Cantidad actual de articulo 
        [old_obj] = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['name', '=', item['name']]]], {'fields': ['id', 'name', 'qty_available', 'stock_quant_ids', 'stock_move_ids']})
        item_id = old_obj["id"]
        # Obtener cantidad necesaria para obtener desired_qty
        curr_qty = old_obj["qty_available"]
        diff_qty = read_qty - item['barrel_weight'] - curr_qty
        # garantizar que no hay negativos
        if diff_qty < 0:
            diff_qty = 0

        # Crear entrada de almacen para ajustar
        res = models.execute_kw(db, uid, password, 'stock.quant', 'create', [{'quantity': diff_qty,'product_id': item_id, 'location_id': 8}])

        # Ver si tuvo éxito la movida de almacen
        [new_obj] = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['name', '=', item['name']]]], {'fields': ['id', 'name', 'qty_available', 'stock_quant_ids', 'stock_move_ids']})


        print(old_obj)
        print(res)
        print(new_obj)
        print()

    except Exception as e:
        logging.error(traceback.format_exc())
        # Logs the error appropriately.