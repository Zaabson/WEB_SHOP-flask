from datetime import datetime

from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer

from web_shop import db, login_manager, app


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        if user.true_user:  # has email and password, is able to log in, otherwise User() only stores address
            return user


favourites = db.Table('favourites',
                      db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
                      db.Column('product_id', db.Integer(), db.ForeignKey('product.id'), primary_key=True))


class User(db.Model, UserMixin):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), nullable=True, unique=True)
    password = db.Column(db.String(), nullable=True)
    true_user = db.Column(db.Boolean(), default=False, nullable=False)  # if false means that User() object is used to store address for transaction only

    has_address = db.Column(db.Boolean(), default=False, nullable=False)
    first_name = db.Column(db.String(), nullable=True)
    last_name = db.Column(db.String(), nullable=True)
    street = db.Column(db.String(), nullable=True)
    street_number = db.Column(db.Integer(), nullable=True)
    apartment_number = db.Column(db.Integer(), nullable=True)
    city = db.Column(db.String(), nullable=True)
    country = db.Column(db.String(), nullable=True)
    postal_code = db.Column(db.String(), nullable=True)

    transactions = db.relationship('Transaction', backref='buyer', lazy=True)
    favourites = db.relationship('Product', secondary=favourites, lazy='subquery', backref=db.backref('lover', lazy=True))

    def __repr__(self):
        return f"User(id={self.id}, email={self.email}, has_address={self.has_address})"

    def get_token(self):
        serializer = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps({'user_id': self.id})
        return token

    @staticmethod
    def validate_token(token):
        serializer = TimedJSONWebSignatureSerializer(app.config['SECRET_KEY'])
        try:
            data = serializer.loads(token)
            user_id = data['user_id']
        except:
            return None
        user = User.query.get(int(user_id))
        return user


class Product(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)  # in cents
    description = db.Column(db.Text(), default='XDDDD', nullable=False)
    date_added = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    image = db.Column(db.String(), nullable=False, default='pokemon.jpg')

    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)
        self.description = kwargs.get('description') or f"This is a {self.name}"  # act like default

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name}, price={self.price})"


class Transaction(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)
    buyer_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(), nullable=False)

    items = db.relationship('TransactionItem', backref='transaction', lazy=True)


class TransactionItem(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    transaction_id = db.Column(db.Integer(), db.ForeignKey('transaction.id'))
    product_id = db.Column(db.Integer())
    quantity = db.Column(db.Integer())
