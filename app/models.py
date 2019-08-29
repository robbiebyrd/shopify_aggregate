#!/usr/bin/env python
from app import db
from timelib import strtodatetime
import simplejson as json
import hashlib
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')

    def __init__(self, email, password, first_name, last_name):
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        self.email      = email
        self.password   = m.hexdigest()
        self.first_name = first_name
        self.last_name  = last_name
        self.active     = True

    @classmethod
    def get_all(cls):
        users = db.session.query(User) \
                .all()
        return users

    @classmethod
    def get(cls, id):
        user = db.session.query(User) \
                .filter(User.id == id) \
                .first()
        return user

    @classmethod
    def get_by_email(cls, email):
        user = db.session.query(User) \
                .filter(User.email == email) \
                .first()
        return user

    @classmethod
    def authenticate(cls, email, password):
        m = hashlib.md5()
        m.update(password.encode('utf-8'))
        user = db.session.query(User) \
                .filter(User.email == email) \
                .filter(User.password == m.hexdigest()) \
                .first()
        return user

    @classmethod
    def exists_by_email(cls, email, id=None):
        if id:
            user = db.session.query(User) \
                    .filter(User.email == email) \
                    .filter(User.id != id) \
                    .first()
        else:
            user = db.session.query(User) \
                    .filter(User.email == email) \
                    .first()
        if user:
            return True
        return False

    @classmethod
    def update_password(cls, id, new_password):
        user = User.get(id)
        m = hashlib.md5()
        m.update(new_password.encode('utf-8'))
        user.password = m.hexdigest()
        db.session.commit()

    @classmethod
    def update(cls, id, first_name, last_name, email, active):
        user = User.get(id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.active = active

        db.session.commit()

class UserShop(db.Model):
    id           = db.Column(db.Integer, primary_key=True)

    name         = db.Column(db.String(255), nullable=False)
    url          = db.Column(db.Text, nullable=False)
    active       = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')

    secret       = db.Column(db.String(100), nullable=False, server_default='')
    password     = db.Column(db.String(100), nullable=False, server_default='')

    shopify_id   = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)

    def __init__(self, name, url, active, secret, password):
        self.name     = name
        self.url      = url
        self.active   = active
        self.secret   = secret
        self.password = password

    @classmethod
    def get_all(cls):
        shops = db.session.query(UserShop) \
                .all()
        return shops

    @classmethod
    def get_dashboard(cls):
        query = """
            SELECT name,
                (SELECT status FROM audit_status
                    WHERE shop_id = shop.id 
                    ORDER BY id DESC
                    LIMIT 1) as status,
                (SELECT logged_on FROM audit_status
                    WHERE shop_id = shop.id 
                    ORDER BY id DESC
                    LIMIT 1) as logged_on,
                (SELECT run_id FROM audit_status
                    WHERE shop_id = shop.id 
                    ORDER BY id DESC
                    LIMIT 1) as last_run_id
                FROM
                    user_shop shop
                ORDER BY status DESC,
                    logged_on DESC
        """
        result = db.engine.execute(query)
        rows = []
        for row in result:
            rows.append(dict(
                name=row[0],
                status=row[1],
                logged_on=row[2],
                run_id=row[3]
                ))
        return rows

    @classmethod
    def get(cls, id):
        shop = db.session.query(UserShop) \
                .filter(UserShop.id == id) \
                .first()
        return shop

    @classmethod
    def update(cls, id, name, url, active, secret, password):
        shop = UserShop.get(id)

        shop.name = name
        shop.url = url
        shop.active = active
        shop.secret = secret
        shop.password = password
        
        db.session.commit()

    @classmethod
    def set_shopify_id(cls, id, shopify_id):
        userShop = UserShop.get(id)

        userShop.shopify_id = shopify_id
        db.session.commit()
        return True

    @classmethod
    def mark_updated(cls, id):
        userShop = UserShop.get(id)

        userShop.last_updated = datetime.datetime.utcnow()
        db.session.commit()
        return True

class Order(db.Model):
    __tablename__ = 'order'

    id                      = db.Column(db.Integer, primary_key=True)
    customer_id             = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer                = db.relationship("Customer")
    shop_id                 = db.Column(db.Integer, db.ForeignKey('shop.id'), nullable=False)
    shop                    = db.relationship("Shop")
    email                   = db.Column(db.String(255), nullable=False)
    closed_at               = db.Column(db.DateTime, nullable=True)
    created_at              = db.Column(db.DateTime, nullable=False)
    updated_at              = db.Column(db.DateTime, nullable=True)
    number                  = db.Column(db.Integer, nullable=False)
    note                    = db.Column(db.Text, nullable=True)
    token                   = db.Column(db.String(200), nullable=False)
    gateway                 = db.Column(db.String(200), nullable=True)
    test                    = db.Column(db.Integer, nullable=False)
    total_price             = db.Column(db.Float, nullable=False)
    subtotal_price          = db.Column(db.Float, nullable=False)
    total_weight            = db.Column(db.Integer, nullable=False)
    total_tax               = db.Column(db.Float, nullable=False)
    taxes_included          = db.Column(db.Integer, nullable=False)
    currency                = db.Column(db.String(10), nullable=False)
    financial_status        = db.Column(db.String(20), nullable=False)
    confirmed               = db.Column(db.Integer, nullable=False)
    total_discounts         = db.Column(db.Float, nullable=False)
    total_line_items_price  = db.Column(db.Float, nullable=False)
    cart_token              = db.Column(db.String(200), nullable=True)
    buyer_accepts_marketing = db.Column(db.Integer, nullable=False)
    name                    = db.Column(db.String(200), nullable=False)
    referring_site          = db.Column(db.Text, nullable=True)
    landing_site            = db.Column(db.Text, nullable=True)
    cancelled_at            = db.Column(db.DateTime, nullable=True)
    cancel_reason           = db.Column(db.Text, nullable=True)
    total_price_usd         = db.Column(db.Float, nullable=False)
    checkout_token          = db.Column(db.String(200), nullable=True)
    reference               = db.Column(db.String(200), nullable=True)
    user_id                 = db.Column(db.String(200), nullable=True)
    location_id             = db.Column(db.String(200), nullable=True)
    source_identifier       = db.Column(db.String(200), nullable=True)
    source_url              = db.Column(db.String(200), nullable=True)
    processed_at            = db.Column(db.DateTime, nullable=True)
    device_id               = db.Column(db.Text, nullable=True)
    browser_ip              = db.Column(db.Text, nullable=True)
    landing_site_ref        = db.Column(db.Text, nullable=True)
    order_number            = db.Column(db.Integer, nullable=True)
    processing_method       = db.Column(db.String(200), nullable=False)
    checkout_id             = db.Column(db.Integer, nullable=True)
    source_name             = db.Column(db.String(200), nullable=False)
    fulfillment_status      = db.Column(db.String(200), nullable=True)
    tags                    = db.Column(db.Text, nullable=False)
    contact_email           = db.Column(db.String(255), nullable=True)
    order_status_url        = db.Column(db.String(255), nullable=True)
    client_details          = db.Column(db.Text, nullable=True)
    discount_codes          = db.Column(db.Text, nullable=True)
    note_attributes         = db.Column(db.Text, nullable=True)
    payment_gateway_names   = db.Column(db.Text, nullable=True)
    tax_lines               = db.Column(db.Text, nullable=True)
    payment_details         = db.Column(db.Text, nullable=True)
    shipping_lines          = db.Column(db.Text, nullable=True)

    @classmethod
    def get_store_data(cls, shop_id, date_start, date_end):
        query = """
        SELECT 
            o.name as 'Order ID',
            o.financial_status AS 'Order Status',
            DATE(o.created_at) AS 'Order Date',
            MIN(DATE(ot.created_at)) AS 'Invoice Date',
            MIN(DATE(otr.created_at)) AS 'Refund Date',
            MIN(DATE(oful.created_at)) AS 'Ship Date',
            oli.sku AS 'SKU',
            oli.name AS 'Item Description',
            oli.quantity AS 'Order Quantity',
            oli.quantity AS 'Invoiced Quantity',
            oli.quantity AS 'Shipped Quantity',
            oli.price AS 'Unit Price',
            o.total_tax AS 'Total Tax',
            oli.tax_lines AS 'Tax Lines',
            oli.price as 'Shipped Amount',
            o.shipping_lines as 'Shipping Lines',
            o.total_price_usd as 'Order Total',
            CONCAT(c.first_name, ' ', c.last_name) AS 'Customer Name',
            c.email as 'Email',
            GROUP_CONCAT(ot.gateway) as 'Payment Method',
            osa.city as 'Ship To City',
            osa.province as 'Ship To State',
            osa.zip as 'Ship To Zip',
            osa.country as 'Ship To Country',
            SUM(osl.price) as 'Shipping Total'
        FROM
            olm.`order` o
                INNER JOIN
            `order_line_items` oli ON oli.order_id = o.id
                LEFT JOIN
            `order_transaction` ot ON ot.order_id = o.id AND ot.kind = 'sale'
                LEFT JOIN
            `order_transaction` otr ON otr.order_id = o.id
                AND ot.kind = 'refund'
                LEFT JOIN
            `order_fulfillment` oful ON oful.order_id = o.id
                LEFT JOIN
            `customer` c ON c.id = o.customer_id
                LEFT JOIN
            `order_shipping_address` osa ON osa.order_id = o.id
                LEFT JOIN
            `order_shipping_lines` osl ON osl.order_id = o.id
        WHERE
            o.shop_id = 7990083
            AND o.created_at > '%s'
            AND o.created_at < '%s'
            GROUP BY oli.id;
        """ % (date_start, date_end)
        result = db.engine.execute(query)
        rows = []
        for row in result:
            rows.append(dict(
                order_id=row[0],
                order_status=row[1],
                order_date=row[2],
                invoice_date=row[3],
                refund_date=row[4],
                ship_date=row[5],
                sku=row[6],
                item=row[7],
                order_quantity=row[8],
                invoiced_quantity=row[9],
                shipped_quantity=row[10],
                unit_price=row[11],
                total_tax=row[12],
                total_price_usd=row[16],
                customer_name=row[17],
                email=row[18],
                payment_method=row[19],
                ship_to_city=row[20],
                ship_to_state=row[21],
                ship_to_zip=row[22],
                ship_to_country=row[23],
                shipping_total=row[24],
                ))
        return rows

    @classmethod
    def get_sales_activity_by_order_status(cls, shop_id, date_start, date_end):
        query = """
            SELECT
                SUM(oli.quantity) AS qty,
                financial_status,
                SUM(oli.price * oli.quantity)
            FROM
                olm.`order` o
                    INNER JOIN
                `order_line_items` oli ON oli.order_id = o.id
                    LEFT JOIN
                `order_fulfillment` oful ON oful.order_id = o.id
            WHERE
                    o.shop_id = 7990083
                    AND o.created_at > '%s'
                    AND o.created_at < '%s'
                    GROUP BY financial_status;
        """ % (date_start, date_end)

        result = db.engine.execute(query)
        rows = []
        for row in result:
            rows.append(dict(
                number_shipped=row[0],
                financial_status=row[1],
                amount_shipped=row[2]
                ))

        return rows

    @classmethod
    def get_sales_by_best_sellers(cls, shop_id, date_start, date_end):
        query = """
        SELECT
            SUM(oli.price * oli.quantity) as price,
            SUM(oli.quantity) AS qty,
            oli.name,
            oli.sku
        FROM
            olm.`order` o
                INNER JOIN
            `order_line_items` oli ON oli.order_id = o.id
                LEFT JOIN
            `order_fulfillment` oful ON oful.order_id = o.id
        WHERE
                    o.shop_id = 7990083
                    AND o.created_at > '%s'
                    AND o.created_at < '%s'
                    GROUP BY oli.sku, oli.name
                    ORDER BY SUM(oli.price * oli.quantity) DESC;
        """ % (date_start, date_end)

        result = db.engine.execute(query)
        rows = []
        for row in result:
            rows.append(dict(
                total_amount=row[0],
                total_quantity=row[1],
                name=row[2],
                sku=row[3]
                ))
        return rows

    @classmethod
    def get_list(cls, page=1):
        orders = Order.query \
                .paginate(page, 25, False)

        return orders

    @classmethod
    def get(cls, id):
        order = db.session.query(Order) \
                .filter(Order.id == id) \
                .first()
        return order

    @classmethod
    def upsert(cls, data, shop_id):
        add = False
        try:
            o = Order.get(data['id'])
            if not o:
                o = Order()
                add = True
            o.id                      = data['id']
            o.shop_id                 = shop_id
            if 'customer' in data and 'id' in data['customer']:
                o.customer_id             = data['customer']['id']
            o.email                   = data['email']
            o.closed_at               = data['closed_at']
            o.created_at              = strtodatetime(data['created_at'].encode('utf-8'))
            o.updated_at              = strtodatetime(data['updated_at'].encode('utf-8'))
            o.number                  = data['number']
            o.note                    = data['note']
            o.token                   = data['token']
            o.gateway                 = data['gateway']
            o.test                    = data['test']
            o.total_price             = data['total_price']
            o.subtotal_price          = data['subtotal_price']
            o.total_weight            = data['total_weight']
            o.total_tax               = data['total_tax']
            o.taxes_included          = data['taxes_included']
            o.currency                = data['currency']
            o.financial_status        = data['financial_status']
            o.confirmed               = data['confirmed']
            o.total_discounts         = data['total_discounts']
            o.total_line_items_price  = data['total_line_items_price']
            o.cart_token              = data['cart_token']
            o.buyer_accepts_marketing = data['buyer_accepts_marketing']
            o.name                    = data['name']
            o.referring_site          = data['referring_site']
            o.landing_site            = data['landing_site']
            o.cancelled_at            = data['cancelled_at']
            o.cancel_reason           = data['cancel_reason']
            o.total_price_usd         = data['total_price_usd']
            o.checkout_token          = data['checkout_token']
            o.reference               = data['reference']
            o.user_id                 = data['user_id']
            o.location_id             = data['location_id']
            o.source_identifier       = data['source_identifier']
            o.source_url              = data['source_url']
            o.processed_at            = strtodatetime(data['processed_at'].encode('utf-8'))
            o.device_id               = data['device_id']
            o.browser_ip              = data['browser_ip']
            o.landing_site_ref        = data['landing_site_ref']
            o.order_number            = data['order_number']
            o.processing_method       = data['processing_method']
            o.checkout_id             = data['checkout_id']
            o.source_name             = data['source_name']
            o.fulfillment_status      = data['fulfillment_status']
            o.tags                    = data['tags']
            o.contact_email           = data['contact_email']
            o.order_status_url        = data['order_status_url']
            o.client_details          = json.dumps(data['client_details']) if 'client_details' in data else None
            o.discount_codes          = json.dumps(data['discount_codes'])
            o.note_attributes         = json.dumps(data['note_attributes'])
            o.payment_gateway_names   = json.dumps(data['payment_gateway_names'])
            o.tax_lines               = json.dumps(data['tax_lines'])
            o.shipping_lines          = json.dumps(data['shipping_lines'])
            if 'payment_details' in data:
                o.payment_details         = json.dumps(data['payment_details'])
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            sys.exit(0)
            return
        except Exception as e:
            print("Order Exception: ", e)
            sys.exit(0)
            return
        return o.id


class Product(db.Model):
    __tablename__ = 'product'

    id              = db.Column(db.Integer, primary_key=True)
    shop_id         = db.Column(db.Integer, nullable=False)
    title           = db.Column(db.Text, nullable=False)
    body_html       = db.Column(db.Text, nullable=False)
    vendor          = db.Column(db.String(255), nullable=False)
    product_type    = db.Column(db.String(255), nullable=False)
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=True)
    published_at    = db.Column(db.DateTime, nullable=True)
    handle          = db.Column(db.String(255), nullable=False)
    template_suffix = db.Column(db.String(255), nullable=True)
    published_scope = db.Column(db.String(255), nullable=False)
    tags            = db.Column(db.String(255), nullable=False)

    @classmethod
    def get_all(cls, page=1):
        products = Product.query \
                .paginate(page, 25, False)
        return products

    @classmethod
    def upsert(self, data, shop_id):
        add = False
        try:
            p = Product.get(data['id'])
            if not p:
                p = Product()
                add = True
            p.id = data['id']
            p.shop_id = shop_id
            p.title = data['title']
            p.body_html = data['body_html']
            p.vendor = data['vendor']
            p.product_type = data['product_type']
            p.created_at = strtodatetime(data['created_at'].encode('utf-8')) if data['created_at'] else None
            p.updated_at = strtodatetime(data['updated_at'].encode('utf-8')) if data['updated_at'] else None
            p.published_at = strtodatetime(data['published_at'].encode('utf-8')) if data['published_at'] else None
            p.handle = data['handle']
            p.template_suffix = data['template_suffix']
            p.published_scope = data['published_scope']
            p.tags = data['tags']

            if add:
                db.session.add(p)
            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
        except Exception as e:
            print("Product EXCEPTION: ", e)
            return
        return p.id

    @classmethod
    def get(cls, id):
        product = db.session.query(Product) \
                .filter(Product.id == id) \
                .first()
        return product


class ProductVariant(db.Model):
    __tablename__ = 'productVariant'

    id                     = db.Column(db.Integer, primary_key=True)
    product_id             = db.Column(db.Integer, nullable=False)
    title                  = db.Column(db.Text, nullable=False)
    price                  = db.Column(db.Float, nullable=False)
    sku                    = db.Column(db.String(255), nullable=True)
    position               = db.Column(db.Integer, nullable=False)
    grams                  = db.Column(db.Integer, nullable=True)
    inventory_policy       = db.Column(db.String(10), nullable=False)
    compare_at_price       = db.Column(db.String(200), nullable=True)
    fulfillment_service    = db.Column(db.String(10), nullable=True)
    inventory_management   = db.Column(db.String(255), nullable=True)
    option1                = db.Column(db.String(255), nullable=True)
    option2                = db.Column(db.String(255), nullable=True)
    option3                = db.Column(db.String(255), nullable=True)
    created_at             = db.Column(db.DateTime, nullable=False)
    updated_at             = db.Column(db.DateTime, nullable=True)
    taxable                = db.Column(db.Integer, nullable=False)
    barcode                = db.Column(db.String(255), nullable=True)
    image_id               = db.Column(db.Integer, nullable=True)
    inventory_quantity     = db.Column(db.Integer, nullable=False)
    weight                 = db.Column(db.Float, nullable=False)
    weight_unit            = db.Column(db.String(20), nullable=False)
    old_inventory_quantity = db.Column(db.Integer, nullable=False)
    requires_shipping      = db.Column(db.Integer, nullable=False)

    @classmethod
    def upsert(self, data, product_id):
        add = False
        try:
            p = ProductVariant.get(data['id'])
            if not p:
                p = ProductVariant()
                add = True
            p.id = data['id']
            p.product_id = product_id
            p.title = data['title']
            p.price = data['price']
            p.sku = data['sku']
            p.position = data['position']
            p.grams = data['grams']
            p.inventory_policy = data['inventory_policy']
            p.compare_at_price = data['compare_at_price']
            p.fulfillment_service = data['fulfillment_service']
            p.inventory_management = data['inventory_management']
            p.option1 = data['option1']
            p.option2 = data['option2']
            p.option3 = data['option3']
            p.created_at = strtodatetime(data['created_at'].encode('utf-8'))
            p.updated_at = strtodatetime(data['updated_at'].encode('utf-8'))
            p.taxable = data['taxable']
            p.barcode = data['barcode']
            p.image_id = data['image_id']
            p.inventory_quantity = data['inventory_quantity']
            p.weight = data['weight']
            p.weight_unit = data['weight_unit']
            p.old_inventory_quantity = data['old_inventory_quantity']
            p.requires_shipping = data['requires_shipping']

            if add:
                db.session.add(p)
            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
        except Exception as e:
            print("ProductVariant EXCEPTION: ", e)
            return
        return p.id

    @classmethod
    def get(cls, id):
        productVariant = db.session.query(ProductVariant) \
                .filter(ProductVariant.id == id) \
                .first()
        return productVariant

class Shop(db.Model):
    __tablename__ = 'shop'

    id                                   =  db.Column(db.Integer, primary_key=True)
    name                                 =  db.Column(db.String(200), nullable=False)
    email                                =  db.Column(db.String(200), nullable=False)
    domain                               =  db.Column(db.String(200), nullable=False)
    created_at                           =  db.Column(db.DateTime, nullable=False)
    province                             =  db.Column(db.String(200), nullable=False)
    country                              =  db.Column(db.String(200), nullable=False)
    address1                             =  db.Column(db.String(200), nullable=False)
    zip                                  =  db.Column(db.String(200), nullable=False)
    city                                 =  db.Column(db.String(200), nullable=False)
    source                               =  db.Column(db.String(200), nullable=True)
    phone                                =  db.Column(db.String(200), nullable=False)
    updated_at                           =  db.Column(db.DateTime, nullable=False)
    customer_email                       =  db.Column(db.String(200), nullable=True)
    latitude                             =  db.Column(db.Float, nullable=False)
    longitude                            =  db.Column(db.Float, nullable=False)
    primary_location_id                  =  db.Column(db.String(200), nullable=True)
    primary_locale                       =  db.Column(db.String(200), nullable=False)
    country_code                         =  db.Column(db.String(200), nullable=False)
    country_name                         =  db.Column(db.String(200), nullable=False)
    currency                             =  db.Column(db.String(200), nullable=False)
    timezone                             =  db.Column(db.String(200), nullable=False)
    iana_timezone                        =  db.Column(db.String(200), nullable=False)
    shop_owner                           =  db.Column(db.String(200), nullable=False)
    money_format                         =  db.Column(db.String(200), nullable=False)
    money_with_currency_format           =  db.Column(db.String(200), nullable=False)
    province_code                        =  db.Column(db.String(200), nullable=True)
    taxes_included                       =  db.Column(db.Integer, nullable=False)
    tax_shipping                         =  db.Column(db.String(200), nullable=True)
    county_taxes                         =  db.Column(db.Integer, nullable=False)
    plan_display_name                    =  db.Column(db.String(200), nullable=False)
    plan_name                            =  db.Column(db.String(200), nullable=False)
    has_discounts                        =  db.Column(db.Integer, nullable=False)
    has_gift_cards                       =  db.Column(db.Integer, nullable=False)
    myshopify_domain                     =  db.Column(db.String(200), nullable=False)
    google_apps_domain                   =  db.Column(db.String(200), nullable=True)
    google_apps_login_enabled            =  db.Column(db.Integer, nullable=True)
    money_in_emails_format               =  db.Column(db.String(200), nullable=False)
    money_with_currency_in_emails_format =  db.Column(db.String(200), nullable=False)
    eligible_for_payments                =  db.Column(db.Integer, nullable=True)
    requires_extra_payments_agreement    =  db.Column(db.Integer, nullable=False)
    password_enabled                     =  db.Column(db.Integer, nullable=False)
    has_storefront                       =  db.Column(db.Integer, nullable=False)
    eligible_for_card_reader_giveaway    =  db.Column(db.Integer, nullable=False)
    setup_required                       =  db.Column(db.Integer, nullable=False)
    force_ssl                            =  db.Column(db.Integer, nullable=False)

    def upsert(self, data):
        add = False
        try:
            s = Shop.get(data['id'])
            if not s:
                s = Shop()
                add = True
            s.id = data['id']
            s.name = data['name']
            s.email = data['email']
            s.domain = data['domain']
            s.created_at = strtodatetime(data['created_at'].encode('utf-8'))
            s.province = data['province']
            s.country = data['country']
            s.address1 = data['address1']
            s.zip = data['zip']
            s.city = data['city']
            s.source = data['source']
            s.phone = data['phone']
            s.updated_at = strtodatetime(data['updated_at'].encode('utf-8'))
            s.customer_email = data['customer_email']
            s.latitude = data['latitude']
            s.longitude = data['longitude']
            s.primary_location_id = data['primary_location_id']
            s.primary_locale = data['primary_locale']
            s.country_code = data['country_code']
            s.country_name = data['country_name']
            s.currency = data['currency']
            s.timezone = data['timezone']
            s.iana_timezone = data['iana_timezone']
            s.shop_owner = data['shop_owner']
            s.money_format = data['money_format']
            s.money_with_currency_format = data['money_with_currency_format']
            s.province_code = data['province_code']
            s.taxes_included = data['taxes_included']
            s.tax_shipping = data['tax_shipping']
            s.county_taxes = data['county_taxes']
            s.plan_display_name = data['plan_display_name']
            s.plan_name = data['plan_name']
            s.has_discounts = data['has_discounts']
            s.has_gift_cards = data['has_gift_cards']
            s.myshopify_domain = data['myshopify_domain']
            s.google_apps_domain = data['google_apps_domain']
            s.google_apps_login_enabled = data['google_apps_login_enabled']
            s.money_in_emails_format = data['money_in_emails_format']
            s.money_with_currency_in_emails_format = data['money_with_currency_in_emails_format']
            s.eligible_for_payments = data['eligible_for_payments']
            s.requires_extra_payments_agreement = data['requires_extra_payments_agreement']
            s.password_enabled = data['password_enabled']
            s.has_storefront = data['has_storefront']
            s.eligible_for_card_reader_giveaway = data['eligible_for_card_reader_giveaway']
            s.setup_required = data['setup_required']
            s.force_ssl = data['force_ssl']

            if add:
                db.session.add(s)
            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
        except Exception as e:
            print("Shop EXCEPTION: ", e)
            return

    @classmethod
    def get(cls, shop_id):
        shop = db.session.query(Shop) \
                .filter(Shop.id == shop_id) \
                .first()
        return shop

class AuditStatuses:
    COMPLETE = 'complete'
    RUNNING  = 'running'
    ERROR    = 'error'

class AuditStatus(db.Model):
    __tablename__ = 'audit_status'

    id        = db.Column(db.Integer, primary_key=True)
    run_id    = db.Column(db.String(100), nullable=True)
    shop_id   = db.Column(db.Integer, nullable=False)
    status    = db.Column(db.String(100), nullable=False)
    logged_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, run_id, shop_id, status=AuditStatuses.RUNNING):
        self.run_id    = run_id
        self.shop_id   = shop_id
        self.status    = status
        self.logged_on = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_shop_id_by_run_id(cls, run_id):
        msg = db.session.query(AuditStatus) \
                .filter(AuditStatus.run_id == run_id) \
                .first()
        if not msg:
            return 0
        return msg.shop_id


class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    
    id        = db.Column(db.Integer, primary_key=True)
    run_id    = db.Column(db.String(100), nullable=False)
    shop_id   = db.Column(db.Integer, nullable=False)
    message   = db.Column(db.Text, nullable=False)
    logged_on = db.Column(db.DateTime, nullable=False)


    def __init__(self, run_id, shop_id, message):
        self.run_id    = run_id
        self.shop_id   = shop_id
        self.message   = message
        self.logged_on = datetime.datetime.utcnow()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_run(cls, run_id):
        log_messages = db.session.query(AuditLog) \
                .filter(AuditLog.run_id == run_id) \
                .order_by(db.desc(AuditLog.logged_on)) \
                .order_by(db.desc(AuditLog.id)) \
                .all()
        return log_messages


class OrderFulfillment(db.Model):
    __tablename__ = 'order_fulfillment'

    id               = db.Column(db.Integer, primary_key=True)
    order_id         = db.Column(db.Integer, nullable=False)
    created_at       = db.Column(db.DateTime, nullable=False)
    updated_at       = db.Column(db.DateTime, nullable=True)
    status           = db.Column(db.String(100), nullable=False)
    service          = db.Column(db.String(100), nullable=False)
    tracking_company = db.Column(db.String(100), nullable=True)
    tracking_number  = db.Column(db.String(100), nullable=True)
    tracking_numbers = db.Column(db.Text, nullable=True)
    tracking_url     = db.Column(db.Text, nullable=True)
    tracking_urls    = db.Column(db.Text, nullable=True)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            o = OrderFulfillment.get(data['id'])
            if not o:
                o = OrderFulfillment()
                add = True
            o.id = data['id']
            o.order_id = data['order_id']
            o.created_at = strtodatetime(data['created_at'].encode('utf-8'))
            o.updated_at = strtodatetime(data['updated_at'].encode('utf-8'))
            o.status = data['status']
            o.service = data['service']
            o.tracking_company = data['tracking_company']
            o.tracking_number = data['tracking_number']
            o.tracking_numbers = json.dumps(data['tracking_numbers'])
            o.tracking_url = data['tracking_url']
            o.tracking_urls = json.dumps(data['tracking_urls'])
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderFulfillment Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderFulfillment = db.session.query(OrderFulfillment) \
                .filter(OrderFulfillment.id == id) \
                .first()
        return orderFulfillment

class OrderLineItems(db.Model):
    __tablename__ = 'order_line_items'

    id                           = db.Column(db.Integer, primary_key=True)
    order_id                     = db.Column(db.Integer, nullable=False)
    variant_id                   = db.Column(db.Integer, nullable=True)
    title                        = db.Column(db.Text, nullable=False)
    quantity                     = db.Column(db.Integer, nullable=False)
    price                        = db.Column(db.Float, nullable=False)
    grams                        = db.Column(db.Integer, nullable=False)
    sku                          = db.Column(db.String(200), nullable=True)
    variant_title                = db.Column(db.String(200), nullable=True)
    vendor                       = db.Column(db.String(200), nullable=True)
    fulfillment_service          = db.Column(db.String(200), nullable=False)
    product_id                   = db.Column(db.Integer, nullable=True)
    requires_shipping            = db.Column(db.Integer, nullable=False)
    taxable                      = db.Column(db.Integer, nullable=False)
    gift_card                    = db.Column(db.Integer, nullable=False)
    name                         = db.Column(db.Text, nullable=False)
    variant_inventory_management = db.Column(db.String(100), nullable=True)
    properties                   = db.Column(db.Text, nullable=False)
    product_exists               = db.Column(db.Integer, nullable=False)
    fulfillable_quantity         = db.Column(db.Integer, nullable=False)
    total_discount               = db.Column(db.Float, nullable=False)
    fulfillment_status           = db.Column(db.String(200), nullable=True)
    tax_lines                    = db.Column(db.Text, nullable=False)

    @classmethod
    def upsert(cls, data, order_id):
        add = False
        try:
            o = OrderLineItems.get(data['id'])
            if not o:
                o = OrderLineItems()
                add = True
            o.id = data['id']
            o.order_id = order_id
            o.variant_id = data['variant_id']
            o.title = data['title']
            o.quantity = data['quantity']
            o.price = data['price']
            o.grams = data['grams']
            o.sku = data['sku']
            o.variant_title = data['variant_title']
            o.vendor = data['vendor']
            o.fulfillment_service = data['fulfillment_service']
            o.product_id = data['product_id']
            o.requires_shipping = data['requires_shipping']
            o.taxable = data['taxable']
            o.gift_card = data['gift_card']
            o.name = data['name']
            o.variant_inventory_management = data['variant_inventory_management']
            o.product_exists = data['product_exists']
            o.fulfillable_quantity = data['fulfillable_quantity']
            o.total_discount = data['total_discount']
            o.fulfillment_status = data['fulfillment_status']

            o.properties = json.dumps(data['properties'])
            o.tax_lines = json.dumps(data['tax_lines'])
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderLineItems Exception: ", e)
            return
        return o.id



    @classmethod
    def get(cls, id):
        orderLineItem = db.session.query(OrderLineItems) \
                .filter(OrderLineItems.id == id) \
                .first()
        return orderLineItem

class OrderShippingLines(db.Model):
    __tablename__ = 'order_shipping_lines'

    id                 = db.Column(db.Integer, primary_key=True)
    order_id           = db.Column(db.Integer, nullable=False)
    title              = db.Column(db.Text, nullable=True)
    price              = db.Column(db.Float, nullable=True)
    code               = db.Column(db.Text, nullable=True)
    source             = db.Column(db.String(200), nullable=True)
    phone              = db.Column(db.String(200), nullable=True)
    delivery_category  = db.Column(db.String(200), nullable=True)
    carrier_identifier = db.Column(db.String(200), nullable=True)
    tax_lines          = db.Column(db.Text, nullable=True)

    @classmethod
    def upsert(cls, data, order_id):
        add = False
        try:
            o = OrderShippingLines.get(data['id'])
            if not o:
                o = OrderShippingLines()
                add = True

            o.id                 = data['id']
            o.order_id           = order_id
            o.title              = data['title']
            o.price              = data['price']
            o.code               = data['code']
            o.source             = data['source']
            o.phone              = data['phone']
            if 'delivery_category' in data:
                o.delivery_category  = data['delivery_category']
            o.carrier_identifier = data['carrier_identifier']
            o.tax_lines          = json.dumps(data['tax_lines'])
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderShippingLines Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderShippingLines = db.session.query(OrderShippingLines) \
                .filter(OrderShippingLines.id == id) \
                .first()
        return orderShippingLines

class OrderShippingAddress(db.Model):
    __tablename__ = 'order_shipping_address'

    order_id      = db.Column(db.Integer, primary_key=True)
    first_name    = db.Column(db.String(255), nullable=True)
    last_name     = db.Column(db.String(255), nullable=True)
    address1      = db.Column(db.String(255), nullable=True)
    address2      = db.Column(db.String(255), nullable=True)
    phone         = db.Column(db.String(255), nullable=True)
    city          = db.Column(db.String(255), nullable=True)
    zip           = db.Column(db.String(255), nullable=True)
    province      = db.Column(db.String(255), nullable=True)
    country       = db.Column(db.String(255), nullable=True)
    company       = db.Column(db.String(255), nullable=True)
    latitude      = db.Column(db.String(255), nullable=True)
    longitude     = db.Column(db.String(255), nullable=True)
    name          = db.Column(db.String(255), nullable=True)
    country_code  = db.Column(db.String(255), nullable=True)
    province_code = db.Column(db.String(255), nullable=True)

    @classmethod
    def upsert(cls, data, order_id):
        add = False
        try:
            o = OrderShippingAddress.get(order_id)
            if not o:
                o = OrderShippingAddress()
                add = True

            o.order_id = order_id
            o.first_name = data['first_name']
            o.last_name = data['last_name']
            o.address1 = data['address1']
            o.address2 = data['address2']
            o.phone = data['phone']
            o.city = data['city']
            o.zip = data['zip']
            o.province = data['province']
            o.country = data['country']
            o.company = data['company']
            o.latitude = data['latitude']
            o.longitude = data['longitude']
            o.name = data['name']
            o.country_code = data['country_code']
            o.province_code = data['province_code']

            if add:
                db.session.add(o)

            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderShippingAddress Exception: ", e)
            return

        return o.order_id

    @classmethod
    def get(cls, order_id):
        orderShippingAddress = db.session.query(OrderShippingAddress) \
                .filter(OrderShippingAddress.order_id == order_id) \
                .first()
        return orderShippingAddress

class OrderRefund(db.Model):
    __tablename__ = 'order_refund'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, nullable=False);
    created_at = db.Column(db.DateTime, nullable=False);
    note       = db.Column(db.Text, nullable=True);
    restock    = db.Column(db.Text, nullable=True);
    user_id    = db.Column(db.Integer, nullable=True);

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            o = OrderRefund.get(data['id'])
            if not o:
                o = OrderRefund()
                add = True
            o.id         = data['id']
            o.order_id   = data['order_id']
            o.created_at = strtodatetime(data['created_at'].encode('utf-8'))
            o.note       = data['note']
            o.restock    = data['restock']
            o.user_id    = data['user_id']
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderRefund Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderRefund = db.session.query(OrderRefund) \
                .filter(OrderRefund.id == id) \
                .first()
        return orderRefund

class OrderRefundLineItem(db.Model):
    __tablename__ = 'order_refund_line_item'

    id           = db.Column(db.Integer, primary_key=True)
    refund_id    = db.Column(db.Integer, nullable=False)
    quantity     = db.Column(db.Integer, nullable=False)
    line_item_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def upsert(cls, data, refund_id):
        add = False
        try:
            o = OrderRefundLineItem.get(data['id'])
            if not o:
                o = OrderRefundLineItem()
                add = True
            o.id           = data['id']
            o.refund_id    = refund_id
            o.quantity     = data['quantity']
            o.line_item_id = data['line_item_id']
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderRefundLineItem Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderRefundLineItem = db.session.query(OrderRefundLineItem) \
                .filter(OrderRefundLineItem.id == id) \
                .first()
        return orderRefundLineItem


class OrderRefundTransaction(db.Model):
    __tablename__ = 'order_refund_transaction'

    id            = db.Column(db.Integer, primary_key=True)
    refund_id     = db.Column(db.Integer, nullable=False)
    order_id      = db.Column(db.Integer, nullable=False)
    amount        = db.Column(db.Float, nullable=False)
    kind          = db.Column(db.String(100), nullable=False)
    gateway       = db.Column(db.String(100), nullable=True)
    status        = db.Column(db.String(100), nullable=False)
    message       = db.Column(db.Text, nullable=True)
    created_at    = db.Column(db.DateTime, nullable=False)
    test          = db.Column(db.Integer, nullable=False)
    authorization = db.Column(db.String(200), nullable=True)
    currency      = db.Column(db.String(20), nullable=False)
    location_id   = db.Column(db.Integer, nullable=True)
    user_id       = db.Column(db.Integer, nullable=True)
    parent_id     = db.Column(db.Integer, nullable=True)
    device_id     = db.Column(db.Integer, nullable=True)
    error_code    = db.Column(db.String(200), nullable=True)
    source_name   = db.Column(db.String(200), nullable=False)

    @classmethod
    def upsert(cls, data, refund_id):
        add = False
        try:
            o = OrderRefundTransaction.get(data['id'])
            if not o:
                o = OrderRefundTransaction()
                add = True
            o.id            = data['id']
            o.refund_id     = refund_id
            o.order_id      = data['order_id']
            o.amount        = data['amount']
            o.kind          = data['kind']
            o.gateway       = data['gateway']
            o.status        = data['status']
            o.message       = data['message']
            o.created_at    = strtodatetime(data['created_at'].encode('utf-8'))
            o.test          = data['test']
            o.authorization = data['authorization']
            o.currency      = data['currency']
            o.location_id   = data['location_id']
            o.user_id       = data['user_id']
            o.parent_id     = data['parent_id']
            o.device_id     = data['device_id']
            o.error_code    = data['error_code']
            o.source_name   = data['source_name']
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderRefundTransaction Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderRefundTransaction = db.session.query(OrderRefundTransaction) \
                .filter(OrderRefundTransaction.id == id) \
                .first()
        return orderRefundTransaction

class OrderRisk(db.Model):
    __tablename__ = 'order_risk'

    id               = db.Column(db.Integer, primary_key=True)
    order_id         = db.Column(db.Integer, nullable=False)
    checkout_id      = db.Column(db.Integer, nullable=False)
    source           = db.Column(db.String(50), nullable=False)
    score            = db.Column(db.Float, nullable=False)
    recommendation   = db.Column(db.String(100), nullable=False)
    display          = db.Column(db.Integer, nullable=False)
    cause_cancel     = db.Column(db.String(255), nullable=True)
    message          = db.Column(db.Text, nullable=True)
    merchant_message = db.Column(db.Text, nullable=False)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            o = OrderRisk.get(data['id'])
            if not o:
                o = OrderRisk()
                add = True
            o.id               = data['id']
            o.order_id         = data['order_id']
            o.checkout_id      = data['order_id']
            o.source           = data['source']
            o.score            = data['score']
            o.recommendation   = data['recommendation']
            o.display          = data['display']
            o.cause_cancel     = data['cause_cancel']
            o.message          = data['message']
            o.merchant_message = data['merchant_message']
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderRisk Exception: ", e)
            return
        return o.id


    @classmethod
    def get(cls, id):
        orderRisk = db.session.query(OrderRisk) \
                .filter(OrderRisk.id == id) \
                .first()
        return orderRisk

class OrderTransaction(db.Model):
    __tablename__ = 'order_transaction'

    id              = db.Column(db.Integer, primary_key=True)
    order_id        = db.Column(db.Integer, nullable=False)
    amount          = db.Column(db.Float, nullable=False)
    kind            = db.Column(db.String(100), nullable=False)
    gateway         = db.Column(db.String(100), nullable=True)
    status          = db.Column(db.String(100), nullable=False)
    message         = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, nullable=False)
    test            = db.Column(db.Integer, nullable=False)
    authorization   = db.Column(db.String(200), nullable=True)
    currency        = db.Column(db.String(20), nullable=False)
    location_id     = db.Column(db.Integer, nullable=True)
    user_id         = db.Column(db.Integer, nullable=True)
    parent_id       = db.Column(db.Integer, nullable=True)
    device_id       = db.Column(db.Integer, nullable=True)
    error_code      = db.Column(db.String(200), nullable=True)
    source_name     = db.Column(db.String(200), nullable=False)
    payment_details = db.Column(db.Text, nullable=True)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            o = OrderTransaction.get(data['id'])
            if not o:
                o = OrderTransaction()
                add = True
            o.id            = data['id']
            o.order_id      = data['order_id']
            o.amount        = data['amount']
            o.kind          = data['kind']
            o.gateway       = data['gateway']
            o.status        = data['status']
            o.message       = data['message']
            o.created_at    = strtodatetime(data['created_at'].encode('utf-8'))
            o.test          = data['test']
            o.authorization = data['authorization']
            o.currency      = data['currency']
            o.location_id   = data['location_id']
            o.user_id       = data['user_id']
            o.parent_id     = data['parent_id']
            o.device_id     = data['device_id']
            o.error_code    = data['error_code']
            o.source_name   = data['source_name']
            if 'payment_details' in data:
                o.payment_details = json.dumps(data['payment_details'])
            
            if add:
                db.session.add(o)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("OrderTransaction Exception: ", e)
            return
        return o.id

    @classmethod
    def get(cls, id):
        orderTransaction = db.session.query(OrderTransaction) \
                .filter(OrderTransaction.id == id) \
                .first()
        return orderTransaction

class Customer(db.Model):
    __tablename__ = 'customer'

    id                   = db.Column(db.Integer, primary_key=True)
    shop_id              = db.Column(db.Integer, nullable=False)
    email                = db.Column(db.String(200), nullable=True)
    accepts_marketing    = db.Column(db.Integer, nullable=False)
    created_at           = db.Column(db.DateTime, nullable=False)
    updated_at           = db.Column(db.DateTime, nullable=False)
    first_name           = db.Column(db.String(200), nullable=True)
    last_name            = db.Column(db.String(200), nullable=True)
    orders_count         = db.Column(db.Integer, nullable=False)
    state                = db.Column(db.String(100), nullable=False)
    total_spent          = db.Column(db.Float, nullable=False)
    last_order_id        = db.Column(db.Integer, nullable=True)
    note                 = db.Column(db.Text, nullable=True)
    verified_email       = db.Column(db.Integer, nullable=False)
    multipass_identifier = db.Column(db.String(200), nullable=True)
    tax_exempt           = db.Column(db.Integer, nullable=False)
    tags                 = db.Column(db.Text, nullable=True)
    last_order_name      = db.Column(db.String(200), nullable=True)

    @classmethod
    def upsert(self, data, shop_id):
        add = False
        try:
            c = Customer.get(data['id'])
            if not c:
                c = Customer()
                add = True
            c.id = data['id']
            c.shop_id = shop_id
            c.email = data['email']
            c.accepts_marketing = data['accepts_marketing']
            c.created_at = strtodatetime(data['created_at'].encode('utf-8'))
            c.updated_at = strtodatetime(data['updated_at'].encode('utf-8'))
            c.first_name = data['first_name']
            c.last_name = data['last_name']
            c.orders_count = data['orders_count']
            c.state = data['state']
            c.total_spent = data['total_spent']
            c.last_order_id = data['last_order_id']
            c.note = data['note']
            c.verified_email = data['verified_email']
            c.multipass_identifier = data['multipass_identifier']
            c.tax_exempt = data['tax_exempt']
            c.tags = data['tags']
            c.last_order_name = data['last_order_name']

            if add:
                db.session.add(c)
            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
        except Exception as e:
            print("Customer EXCEPTION: ", e)
            return
        return c.id

    @classmethod
    def get(cls, id):
        customer = db.session.query(Customer) \
                .filter(Customer.id == id) \
                .first()
        return customer

class CustomerAddress(db.Model):
    __tablename__ = 'customerAddress'

    id            = db.Column(db.Integer, primary_key=True)
    customer_id   = db.Column(db.Integer, nullable=False)
    first_name    = db.Column(db.String(200), nullable=True)
    last_name     = db.Column(db.String(200), nullable=False)
    company       = db.Column(db.String(200), nullable=True)
    address1      = db.Column(db.String(200), nullable=True)
    address2      = db.Column(db.String(200), nullable=True)
    city          = db.Column(db.String(200), nullable=True)
    province      = db.Column(db.String(200), nullable=True)
    country       = db.Column(db.String(200), nullable=True)
    zip           = db.Column(db.String(100), nullable=True)
    phone         = db.Column(db.String(200), nullable=True)
    name          = db.Column(db.String(255), nullable=False)
    province_code = db.Column(db.String(10), nullable=True)
    country_code  = db.Column(db.Text, nullable=True)
    country_name  = db.Column(db.String(255), nullable=True)
    default       = db.Column(db.Integer, nullable=False)

    @classmethod
    def upsert(self, data, customer_id):
        add = False
        try:
            c = CustomerAddress.get(data['id'])
            if not c:
                c = CustomerAddress()
                add = True
            c.id = data['id']
            c.customer_id = customer_id
            c.first_name = data['first_name']
            c.last_name = data['last_name']
            c.company = data['company']
            c.address1 = data['address1']
            c.address2 = data['address2']
            c.city = data['city']
            c.province = data['province']
            c.country = data['country']
            c.zip = data['zip']
            c.phone = data['phone']
            c.name = data['name']
            c.province_code = data['province_code']
            c.country_code = data['country_code']
            c.country_name = data['country_name']
            c.default = data['default']

            if add:
                db.session.add(c)
            db.session.commit()
        except KeyError as e:
            print("Key Error: ", e)
        except Exception as e:
            print("CustomerAddress EXCEPTION: ", e)
            return
        return c.id

    @classmethod
    def get(cls, id):
        customerAddress = db.session.query(CustomerAddress) \
                .filter(CustomerAddress.id == id) \
                .first()
        return customerAddress

class ShippingZone(db.Model):
    __tablename__ = 'shipping_zone'

    id      =  db.Column(db.Integer, primary_key=True)
    shop_id =  db.Column(db.Integer, nullable=False)
    name    =  db.Column(db.String(255), nullable=False)

    @classmethod
    def upsert(cls, data, shop_id):
        add = False
        try:
            s = ShippingZone.get(data['id'])
            if not s:
                s = ShippingZone()
                add = True
            s.id = data['id']
            s.shop_id = shop_id
            s.name = data['name']

            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZone Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZone = db.session.query(ShippingZone) \
                .filter(ShippingZone.id == id) \
                .first()
        return shippingZone

class ShippingZoneCountries(db.Model):
    __tablename__ = 'shipping_zone_countries'
    
    id               =  db.Column(db.Integer, primary_key=True)
    shipping_zone_id =  db.Column(db.Integer, nullable=False)
    name             =  db.Column(db.String(255), nullable=False)
    tax              =  db.Column(db.Float, nullable=False)
    code             =  db.Column(db.String(20), nullable=False)
    tax_name         =  db.Column(db.String(255), nullable=False)

    @classmethod
    def upsert(cls, data, shipping_zone_id):
        add = False
        try:
            s = ShippingZoneCountries.get(data['id'])
            if not s:
                s = ShippingZoneCountries()
                add = True
            s.id = data['id']
            s.shipping_zone_id = shipping_zone_id
            s.name = data['name']
            s.tax = data['tax']
            s.code = data['code']
            s.tax_name = data['tax_name']

            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZoneCountries Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZoneCountries = db.session.query(ShippingZoneCountries) \
                .filter(ShippingZoneCountries.id == id) \
                .first()
        return shippingZoneCountries

class ShippingZoneCountriesProvinces(db.Model):
    __tablename__ = 'shipping_zone_countries_provinces'

    id               =  db.Column(db.Integer, primary_key=True)
    shipping_zone_id =  db.Column(db.Integer, nullable=False)
    country_id       =  db.Column(db.Integer, nullable=False)
    name             =  db.Column(db.String(255), nullable=False)
    code             =  db.Column(db.String(20), nullable=False)
    tax              =  db.Column(db.Float, nullable=False)
    tax_name         =  db.Column(db.String(255), nullable=False)
    tax_type         =  db.Column(db.String(255), nullable=True)
    tax_percentage   =  db.Column(db.Float, nullable=True)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            s = ShippingZoneCountriesProvinces.get(data['id'])
            if not s:
                s = ShippingZoneCountriesProvinces()
                add = True
            s.id = data['id']
            s.shipping_zone_id = data['shipping_zone_id']
            s.country_id = data['country_id']
            s.name = data['name']
            s.code = data['code']
            s.tax = data['tax']
            s.tax_name = data['tax_name']
            s.tax_type = data['tax_type']
            s.tax_percentage = data['tax_percentage']

            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZoneCountriesProvinces Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZoneCountriesProvinces = db.session.query(ShippingZoneCountriesProvinces) \
                .filter(ShippingZoneCountriesProvinces.id == id) \
                .first()
        return shippingZoneCountriesProvinces

class ShippingZoneWeightBasedShippingRates(db.Model):
    __tablename__ = 'shipping_zone_weight_based_shipping_rates'

    id               =  db.Column(db.Integer, primary_key=True)
    shipping_zone_id =  db.Column(db.Integer, nullable=False)
    weight_low       =  db.Column(db.Float, nullable=False)
    weight_high      =  db.Column(db.Float, nullable=False)
    name             =  db.Column(db.String(255), nullable=False)
    price            =  db.Column(db.Float, nullable=False)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            s = ShippingZoneWeightBasedShippingRates.get(data['id'])
            if not s:
                s = ShippingZoneWeightBasedShippingRates()
                add = True
            s.id = data['id']
            s.shipping_zone_id = data['shipping_zone_id']
            s.weight_low = data['weight_low']
            s.weight_high = data['weight_high']
            s.name = data['name']
            s.price = data['price']
            
            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZoneWeightBasedShippingRates Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZoneWeightBasedShippingRates = db.session.query(ShippingZoneWeightBasedShippingRates) \
                .filter(ShippingZoneWeightBasedShippingRates.id == id) \
                .first()
        return shippingZoneWeightBasedShippingRates

class ShippingZonePriceBasedShippingRates(db.Model):
    __tablename__ = 'shipping_zone_price_based_shipping_rates'

    id                 =  db.Column(db.Integer, primary_key=True)
    shipping_zone_id   =  db.Column(db.Integer, nullable=False)
    name               =  db.Column(db.String(255), nullable=False)
    price              =  db.Column(db.Float, nullable=False)
    min_order_subtotal =  db.Column(db.Float, nullable=True)
    max_order_subtotal =  db.Column(db.Float, nullable=True)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            s = ShippingZonePriceBasedShippingRates.get(data['id'])
            if not s:
                s = ShippingZonePriceBasedShippingRates()
                add = True
            s.id = data['id']
            s.shipping_zone_id = data['shipping_zone_id']
            s.name = data['name']
            s.price = data['price']
            s.min_order_subtotal = data['min_order_subtotal']
            s.max_order_subtotal = data['max_order_subtotal']
            
            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZonePriceBasedShippingRates Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZonePriceBasedShippingRates = db.session.query(ShippingZonePriceBasedShippingRates) \
                .filter(ShippingZonePriceBasedShippingRates.id == id) \
                .first()
        return shippingZonePriceBasedShippingRates

class ShippingZoneCarrierShippingRateProviders(db.Model):
    __tablename__ = 'shipping_zone_carrier_shipping_rate_providers'

    id                 =  db.Column(db.Integer, primary_key=True)
    shipping_zone_id   =  db.Column(db.Integer, nullable=False)
    carrier_service_id =  db.Column(db.Integer, nullable=False)
    flat_modifier      =  db.Column(db.Float, nullable=False)
    percent_modifier   =  db.Column(db.Integer, nullable=False)
    service_filter     =  db.Column(db.Text, nullable=True)

    @classmethod
    def upsert(cls, data):
        add = False
        try:
            s = ShippingZoneCarrierShippingRateProviders.get(data['id'])
            if not s:
                s = ShippingZoneCarrierShippingRateProviders()
                add = True
            s.id = data['id']
            s.shipping_zone_id = data['shipping_zone_id']
            s.carrier_service_id = data['carrier_service_id']
            s.flat_modifier = data['flat_modifier']
            s.percent_modifier = data['percent_modifier']
            s.service_filter = json.dumps(data['service_filter'])
            
            if add:
                db.session.add(s)
            db.session.commit()

        except KeyError as e:
            print("Key Error: ", e)
            return
        except Exception as e:
            print("ShippingZoneCarrierShippingRateProviders Exception: ", e)
            return
        return s.id

    @classmethod
    def get(cls, id):
        shippingZoneCarrierShippingRateProviders = db.session.query(ShippingZoneCarrierShippingRateProviders) \
                .filter(ShippingZoneCarrierShippingRateProviders.id == id) \
                .first()
        return shippingZoneCarrierShippingRateProviders
