from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_required, login_user, current_user, logout_user
from app import app, db
from app.utils.user import User
from app.models import User as dbUser, UserShop as dbShop, Product, Order as dbOrder, AuditLog, AuditStatus
from app.forms.users import AddUser, EditUser, ChangePassword
from app.forms.shops import AddShop, EditShop
from app.obj.Payout import Payout

@app.route('/')
@app.route('/index')
@login_required
def index():
    dashboard_data = dbShop.get_dashboard()
    return render_template('index.html', data=dict(dashboard=dashboard_data, js="dashboard.js"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', data=dict())

    email = request.form['email']
    user_record = dbUser.authenticate(email, request.form['password'])
    if user_record:
        user = User(user_record)
        login_user(user)
        return redirect(url_for('index'))

    return render_template('login.html', data=dict(error=True))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/users')
@login_required
def list_users():
    users = dbUser.get_all()
    return render_template('users.html', data=dict(users=users))

@app.route('/user/edit/<int:user_id>', methods=['GET','POST'])
@login_required
def edit_user(user_id):
    user_id = int(user_id)
    user = dbUser.get(user_id)
    form = EditUser(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        if dbUser.exists_by_email(form.email.data, user_id):
            flash('Email already in use. Please choose another email to use.')
        else:
            dbUser.update(user_id, form.first_name.data, form.last_name.data, form.email.data, form.active.data)
            return redirect(url_for('list_users'))
    passwordform = ChangePassword(request.form, obj=user)

    return render_template('edit_user.html', data=dict(user_id=user_id), form=form, passwordform=passwordform)

@app.route('/user/change_password/<int:user_id>', methods=['GET','POST'])
@login_required
def edit_user_change_password(user_id):
    user_id = int(user_id)
    user = dbUser.get(user_id)
    passwordform = ChangePassword(request.form, obj=user)
    if request.method == 'POST' and passwordform.validate():
        dbUser.update_password(passwordform.id.data, passwordform.password.data)
        return redirect(url_for('list_users'))

    form = EditUser(request.form, obj=user)
    return render_template('edit_user.html', data=dict(user_id=user_id), form=form, passwordform=passwordform)

@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    form = AddUser(request.form)
    if request.method == 'POST' and form.validate():
        if dbUser.exists_by_email(form.email.data):
            flash('Email already in use. Please choose another email to use.')
        else:
            user = dbUser(form.email.data, form.password.data, \
                    form.first_name.data, form.last_name.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('list_users'))

    return render_template('add_user.html', data=dict(js='users.js'), form=form)

@app.route('/products')
@login_required
def list_products():
    page = int(request.args.get('page', 1))
    products = Product.get_all(page)
    return render_template('products.html', data=dict(products=products))

@app.route('/orders')
@login_required
def list_orders():
    page = int(request.args.get('page', 1))
    orders = dbOrder.get_list(page)
    return render_template('orders.html', data=dict(orders=orders))

@app.route('/shops')
@login_required
def list_shops():
    shops = dbShop.get_all()

    return render_template('shops.html', data=dict(shops=shops))

@app.route('/shop/add', methods=['GET', 'POST'])
@login_required
def add_shop():
    form = AddShop(request.form)
    if request.method == 'POST' and form.validate():
        shop = dbShop(form.name.data, form.url.data, \
                form.active.data, form.secret.data, \
                form.password.data)
        db.session.add(shop)
        db.session.commit()
        return redirect(url_for('list_shops'))

    return render_template('add_shop.html', form=form, data=dict())

@app.route('/shop/edit/<int:shop_id>', methods=['GET', 'POST'])
@login_required
def edit_shop(shop_id):
    shop_id = int(shop_id)
    shop = dbShop.get(shop_id)
    form = EditShop(request.form, obj=shop)

    if request.method == 'POST' and form.validate():
        dbShop.update(form.id.data, form.name.data, form.url.data, form.active.data, \
                form.secret.data, form.password.data)

        return redirect(url_for('list_shops'))

    return render_template('edit_shop.html', form=form, data=dict(shop_id=shop_id))

@app.route('/payout/<int:shop_id>') # 53 = Varese Sarabande
@login_required
def payout(shop_id):
    shop_id = int(shop_id)
    payout = Payout(shop_id)

    store_data = payout.get_store_data()
    sales_activity_by_status = payout.get_sales_activity_by_order_status()
    totals = payout.get_totals()
    sales_by_best_sellers = payout.get_sales_by_best_sellers()

    return render_template('payout.html', data=dict(
        shop_id=shop_id, 
        store_data=store_data, 
        sales_activity_by_status=sales_activity_by_status,
        totals=totals,
        sales_by_best_sellers=sales_by_best_sellers
        ))

@app.route('/audit/<string:run_id>')
@login_required
def audit_view(run_id):
    messages = AuditLog.get_by_run(run_id)
    print(messages)
    shop_id = AuditStatus.get_shop_id_by_run_id(run_id)
    shop = dbShop.get(shop_id)

    return render_template('audit_log.html', data=dict(
        shop_id=shop_id,
        shop=shop,
        messages=messages,
        ))
