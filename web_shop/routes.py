import os
from datetime import datetime
from decimal import Decimal

from flask import render_template, url_for, redirect, request, session, flash, abort
from flask_login import login_user, current_user, login_required

from web_shop import app, bcrypt, db
from web_shop.cart import Cart
from web_shop.forms import FilterForm, RegisterForm, LoginForm, AddressForm, CartForm, LoginAdminForm
from web_shop.models import Product, User, Transaction, TransactionItem


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', title='Web shop!', active='home', cart=session.get('cart'), Product=Product, show_modal=False)


@app.route('/products', methods=['POST', 'GET'])
def products():

    form = FilterForm()

    if form.validate_on_submit():  # redirect with filter arguments

        if form.show_all.data:
            return redirect(url_for('products'))

        return redirect(url_for('products', search=form.search.data, sort=form.sort.data,
                                min=form.min_price.data, max=form.max_price.data))

    min = request.args.get('min')
    if min:
        min_price = Decimal(min) * 100
    else:
        min_price = 0

    max = request.args.get('max')
    if max:
        max_price = Decimal(max) * 100
    else:
        max_price = float('inf')

    search = request.args.get('search') or ''
    sort = request.args.get('sort') or 'Newest Arrivals'
    products = Product.query.filter(Product.name.like(f"%{search}%"))
    products = products.filter(Product.price >= min_price, Product.price <= max_price)

    if sort == 'A-Z':
        products = products.order_by(Product.name)
    elif sort == 'Z-A':
        products = products.order_by(Product.name.desc())
    elif sort == 'price_decreasing':
        products = products.order_by(Product.price.desc())
    elif sort == 'price-increasing':
        products = products.order_by(Product.price)
    elif sort == 'Newest Arrivals':
        products = products.order_by(Product.date_added)

    # pagination
    page = request.args.get('page', 1, type=int)  # if only had i known this earlier
    products = products.paginate(per_page=5, page=page)

    # fill form data
    form.search.data = request.args.get('search')
    form.sort.data = sort
    if min:
        form.min_price.data = Decimal(min)
    else:
        form.min_price.data = None
    if max:
        form.max_price.data = Decimal(max)
    else:
        form.max_price.data = None

    args = {'search': search, 'sort': sort, 'min': min, 'max': max}
    return render_template('products.html', title='Products', active='products', products=products,
                           form=form, page=page, args=args, cart=session.get('cart'), Product=Product, show_modal=False)


@app.route('/products/<int:id>')
def this_product(id):
    product = Product.query.filter_by(id=id).first()
    return render_template('this_product.html', title=product.name,
                           product=product, cart=session.get('cart'), Product=Product, show_modal=False)


@app.route('/products/<int:id>/add+to+cart')
def add_to_cart(id):

    product = Product.query.filter_by(id=id).first()
    id = str(id)  # somehow it was giving strange bug with id as int

    if 'cart' in session:
        if id in session['cart'].keys():
            session['cart'][id] += 1
        else:
            session['cart'][id] = 1
    else:
        session['cart'] = {id: 1}

    session.modified = True

    return render_template('this_product.html', show_modal=True, title=product.name, product=product, cart=session.get('cart'), Product=Product)


@app.route('/about')
def about():
    return render_template('about.html', title='About', active='about', cart=session.get('cart'), Product=Product, show_modal=False)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():

        hash = bcrypt.generate_password_hash(form.password.data)
        user = User(email=form.email.data, password=hash, true_user=True)
        db.session.add(user)
        db.session.commit()

        login_user(user, remember=form.remember.data)
        flash("Your account has been created and You are logged in!", category="success")
        return redirect(url_for('home'))

    return render_template('register.html', title='Create and account', form=form, active='register', cart=session.get('cart'), Product=Product)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('You have been successfully logged in!', category='success')
            return redirect(url_for('home'))
        else:
            flash("Login unsuccessful, try again.", category='danger')

    return render_template('login.html', title="Login", active='login', form=form, cart=session.get('cart'), Product=Product)


@app.route('/account/<int:id>/<string:active>', methods=['GET', 'POST'])
@login_required
def account(id, active):
    id = int(id)
    if current_user.id != id:
        flash('Log in first', category='danger')
        abort(403)

    user = User.query.get_or_404(id)

    address_form = AddressForm()
    email_form = LoginForm()
    #email_form.email.data = user.email

    if address_form.validate_on_submit():

        user.has_address = True
        user.first_name = address_form.first_name.data
        user.last_name = address_form.last_name.data
        user.street = address_form.street.data
        user.street_number = address_form.street_number.data
        user.apartment_number = address_form.apartment_number.data
        user.city = address_form.city.data
        user.country = address_form.country.data
        user.postal_code = address_form.postal_code.data

        db.session.commit()

        flash("Your address has been updated. You won't need to type it next time you shop!", category="success")
        return redirect(url_for('account', id=user.id, active='favourites'))

    if user.has_address:  # fill up form with address if user specified address already
        address_form.first_name.data = user.first_name
        address_form.last_name.data = user.last_name
        address_form.street.data = user.street
        address_form.street_number.data = user.street_number
        address_form.apartment_number.data = user.apartment_number
        address_form.city.data = user.city
        address_form.country.data = user.country
        address_form.postal_code.data = user.postal_code

    return render_template('account.html', title='Your Account', user=user, active=active,
                           address_form=address_form, cart=session.get('cart'), Product=Product, email_form=email_form)


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():

    if 'cart' not in session:
        flash('Your cart is empty', category='info')
        return redirect(url_for('home'))

    quantities = [{'product_id': int(product_id), 'quantity': int(quantity)} for product_id, quantity in session['cart'].items()]
    form = CartForm(quantities=quantities)

    if form.validate_on_submit():
        cart = Cart.from_form_data(form.quantities.data)
        session['cart'] = cart.for_session()
        session.modified = True
        if current_user.is_authenticated:
            return redirect(url_for('finalize_transaction_user'))
        else:
            return redirect(url_for('finalize_transaction_anonymous'))

    return render_template('checkout.html', cart=session.get('cart'), Product=Product, form=form)


@app.route('/checkout/finalize/1', methods=['POST', 'GET'])
@login_required
def finalize_transaction_user():

    if 'cart' not in session:
        flash('Your cart is empty')
        return redirect('home')

    cart = Cart(session.get('cart'))
    total_price = cart.get_total_price()
    form = AddressForm()

    if current_user.has_address:

        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.street.data = current_user.street
        form.street_number.data = current_user.street_number
        form.apartment_number.data = current_user.apartment_number
        form.city.data = current_user.city
        form.country.data = current_user.country
        form.postal_code.data = current_user.postal_code

    if form.validate_on_submit():

        transaction = Transaction(date=datetime.now(), status='new', buyer=current_user)

        transaction_items = []
        for id, quantity in session.get('cart').items():
            transaction_item = TransactionItem(product_id=int(id), quantity=quantity, transaction=transaction)
            transaction_items.append(transaction_item)

        db.session.add(transaction)
        for item in transaction_items:
            db.session.add(item)
        db.session.commit()

        flash('Your order has been submitted. You can track progress in "Account" page', category='success')
        return redirect(url_for('home'))

    return render_template('finalize_transaction_user.html', form=form,
                           cart=session.get('cart'), Product=Product, total_price=total_price)


@app.route('/checkout/finalize/2', methods=['GET', 'POST'])
def finalize_transaction_anonymous():

    if 'cart' not in session:
        flash('Your cart is empty')
        return redirect('home')

    cart = Cart(session.get('cart'))
    total_price = cart.get_total_price()
    form = AddressForm()

    if form.validate_on_submit():

        user = User(true_user=False, has_address=True, first_name=form.first_name.data, last_name=form.last_name.data,
                    street=form.street.data, street_number=form.street_number.data, apartment_number=form.apartment_number.data,
                    city=form.city.data, country=form.country.data, postal_code=form.postal_code.data)

        transaction = Transaction(date=datetime.now(), status='new', buyer=user)

        transaction_items = []
        for id, quantity in session.get('cart').items():
            transaction_item = TransactionItem(product_id=int(id), quantity=quantity, transaction=transaction)
            transaction_items.append(transaction_item)

        db.session.add(user)
        db.session.add(transaction)
        for item in transaction_items:
            db.session.add(item)
        db.session.commit()

        flash('Your order has been submitted', category='success')
        return redirect(url_for('home'))

    return render_template('finalize_transaction_anonymous.html', form=form,
                           cart=session.get('cart'), Product=Product, total_price=total_price)


@app.route('/admin', methods=['GET', 'POST'])
def admin():

    form = LoginAdminForm()

    if form.validate_on_submit():

        if form.username.data == os.environ.get('ADMIN_USERNAME') and form.password.data == os.environ.get('ADMIN_PASSWORD'):
            transactions = Transaction.query.all()
            return render_template('admin_page.html', transactions=transactions)
        else:
            flash('Wrong credentials!', category='danger')
            return redirect(url_for('home'))

    return render_template('admin_login.html', form=form)