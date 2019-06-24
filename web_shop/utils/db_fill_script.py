
from datetime import datetime
from io import BytesIO

import numpy as np
import requests
from PIL import Image

from web_shop import db
from web_shop.models import Product, User

f = open('web_shop/utils/things.txt')

things = f.read().split('\n\n')
f.close()
things1 = []

for thing in things:
    thing = '_'.join(thing.split(' ')).lower()
    r = requests.get(url=f"https://www.randomlists.com/img/things/{thing}.jpg")
    try:
        i = Image.open(BytesIO(r.content))
        i = i.convert('RGB')
        output_size = (250, 250)
        i.thumbnail(output_size)
        i.save(f'web_shop/static/pictures/{thing}.jpg', format='JPEG')
        things1.append(thing)
    except:
        print('upss')

r = requests.get(url="https://norvig.com/big.txt")
text = r.text
texts = text.split('\n')
texts = ['\n'.join(texts[12*k:12*k+12]) for k in range(len(texts)//12)]

things = things1


db.drop_all()
db.create_all()

for thing, text in zip(things, texts):
    product1 = Product(name=' '.join(thing.split('_')), price=int(round(np.random.gamma(2, 2)*30000)),
                       description=text, image=f'{thing}.jpg', date_added=datetime.utcnow())
    db.session.add(product1)

user = User(email='setup@g.com', password='abcdefghijkl', true_user=True, has_address=False, first_name=None, last_name=None,
            street=None, street_number=None, apartment_number=None, city=None, postal_code=None, country=None)

db.session.add(user)

db.session.commit()



