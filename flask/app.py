import os
import sys
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, abort, session, escape
from flask_mail import Message, Mail
import requests
import stripe
import binascii
import redis
import secrets
import asyncio
from flask_talisman import Talisman

from util import moltin, ethio, sesh, db


# CONSTANTS ################################
FORCE_HTTPS = False
SUPPORT_EMAIL = "damonsmedley12@gmail.com"

CSP_nonce_in = ['script-src', 'style-src']
CSP = {
    'default-src': [
        '\'self\''
    ],
    'script-src': [
        '\'self\'',
        'https://checkout.stripe.com/checkout.js',
        'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js',
        'https://cdn.rawgit.com/mgalante/jquery.redirect/master/jquery.redirect.js',
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'

    ],
    'style-src': [
        '\'self\'',
        'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
    ],
    'img-src': ['*'],
    'connect-src': [
        'https://checkout.stripe.com/'
    ],
    'frame-src': [
        'https://checkout.stripe.com/'
    ],
    'font-src': [
        '*'
    ]
}

# INIT CONF ####################################
# Moltin keyfile must have SID, CID, and CSC each on their own line, IN THAT ORDER
keyfile = open('.moltinkeys', 'r')
MOLTIN_SID = keyfile.readline().strip('\n')
MOLTIN_CID = keyfile.readline().strip('\n')
MOLTIN_CSC = keyfile.readline().strip('\n')
keyfile.close()

moltin.config({'cid': MOLTIN_CID, 'csc': MOLTIN_CSC})

# Stripe keyfile must have secret key on first line and pub key on second
keyfile = open('.stripekeys', 'r')
secret_key = keyfile.readline().strip('\n')
publishable_key = keyfile.readline().strip('\n')
keyfile.close()

stripe_keys = {
    'secret_key': secret_key,
    'publishable_key': publishable_key
}
stripe.api_key = stripe_keys['secret_key']

# Construct flask app object
# TODO: Pimp out config (http://flask.pocoo.org/docs/1.0/config/)
app = Flask(__name__, static_url_path='')
keyfile = open('.flaskkey', 'r')
app.config['SECRET_KEY'] = keyfile.readline().strip('\n')
keyfile.close()

app.session_interface = sesh.RedisSessionInterface()

# Configure mail
app.config['MAIL_SERVER'] = '172.70.0.5'
#app.config['MAIL_USERNAME'] = 'winston'
#app.config['MAIL_PASSWORD'] = 'smoke'
app.config['MAIL_DEFAULT_SENDER'] = 'winston@jeeves'
# instantiate mail with app config
mail = Mail(app)
mail.init_app(app)


# Enforce CSP
Talisman(app, force_https=FORCE_HTTPS, content_security_policy=CSP,
         content_security_policy_nonce_in=CSP_nonce_in)


# helper functions ==========================================================

def setKey():
    session['key'] = secrets.token_urlsafe()


def getKey():
    res = session.get('key', 'not set')
    if (res == 'not set'):
        print("CURRENT USER HAS NO SESSION KEY. GENERATING NOW.")
        setKey()
        return session.get('key', 'error')
    else:
        print("FOUND LIVE SESSION KEY: %s" % res)
        return res


def sendEmail(recipient, subject, message=None, html=None):
    # send notice to owner
    msg = Message(subject=subject, recipients=[recipient])
    if (message):
        msg.body = message
    if (html):
        msg.html = html
    mail.send(msg)


# APP ROUTES ==================================================================
@app.route('/')
def index():
    if 'key' in session:
        print("USER IS LOGGED IN as %s" % escape(session['key']))
    else:
        print("USER IS NOT LOGGED IN. GENERATING KEY.")
        setKey()

    return render_template('index.jinja', key=stripe_keys['publishable_key'])


@app.route('/_contractAddress')
def _contractAddress():
    return ethio.CONTRACT_ADDRESS


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/products', methods=['GET'])
def products():
    jdata = moltin.solidRequest(moltin.get_products)

    if 'error' in jdata:  # my error flag
        print(jdata['error'], file=sys.stderr)
        abort(500)
    if ('errors' in jdata):  # moltin's error flag
        print(jdata['errors'], file=sys.stderr)
        abort(400)

    images = {}
    shit = []
    for d in jdata['data']:
        # detect non-live/draft items
        if (d['status'] != 'live'):
            # add non-live item to shit list
            shit.append(d)
        elif ("main_image" in d["relationships"]):
            imgId = d['relationships']['main_image']['data']['id']

            imgJson = moltin.solidRequest(moltin.get_file, imgId=imgId)
            imgUrl = imgJson['data']['link']['href']
            images[d['id']] = imgUrl

    # remove draft items
    for s in shit:
        jdata['data'].remove(s)

    return render_template("products.jinja", products=jdata['data'], lproducts=len(jdata['data']), images=images)


# product description page
@app.route('/product/<pid>', methods=['GET'])
def product(pid):
    jdata = moltin.solidRequest(moltin.get_product, productId=pid)

    if ('errors' in jdata):
        print(jdata['errors'], file=sys.stderr)
        abort(404)

    productData = jdata['data']
    metaData = productData['meta']
    name = productData['name']
    description = productData['description']
    price = productData['price'][0]['amount']
    imgId = productData['relationships']['main_image']['data']['id']

    imgResult = moltin.solidRequest(moltin.get_file, imgId=imgId)
    imgUrl = imgResult['data']['link']['href']

    if (metaData['stock']['availability'] != "in-stock"):
        return render_template("product.jinja", pid=pid, status="Sold Out", description=description, imgUrl=imgUrl)
    else:
        return render_template('product.jinja', name=name, description=description, cost=price, imgUrl=imgUrl, pid=pid)


@app.route('/charge', methods=['POST'])
def charge():
    # amount in cents
    amount = request.form['amount']
    dollars = request.form['dollars']
    coins = request.form['coins']
    address = request.form['address']

    try:
        customer = stripe.Customer.create(source=request.form['stripeToken'])
        email = customer.email
        db.setCustomerAddress(email, address)
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='CWBY web payment'
        )

        if (charge['outcome']['network_status'] != "approved_by_network"):
            # transaction error
            return render_template('error.jinja', charge=charge, customer=customer, supportEmail=SUPPORT_EMAIL)
        else:
            # payment processed successfully
            # disburse coins
            ethResult = ''
            try:
                ethResult = ethio.orderCoins(coins, address)
            except Exception as e:
                print("something went wrong with the ETH transaction\n%s" %
                      str(e), file=sys.stderr)
                ethResult = 'none'

            # return confirmation page
            return render_template('charge.jinja', amount=amount, dollars=dollars, coins=coins, address=address, txid=ethResult)
    except Exception as e:
        print(e, file=sys.stderr)
        return redirect("/#", code=302)


@app.route('/cart', methods=["GET", "POST"])
def cart():
    cartId = getKey()
    if (request.method == "POST"):
        # add item to cart
        itemId = request.form['id']
        quantity = request.form['quantity']
        req = moltin.solidRequest(
            moltin.add_cart_item, itemId=itemId, quantity=quantity, cartId=cartId)
        if ('errors' in req or 'error' in req):
            print(req)
            abort(500)

    # retrieve cart items
    items = moltin.solidRequest(moltin.get_cart_items, cartId=cartId)

    cost = 0
    for i in items['data']:
        # adds total cost for item x quantity
        cost += i['value']['amount']

    # render cart items
    return render_template("cart.jinja", items=items, cost=cost, cartId=cartId)


@app.route('/shipping', methods=['POST'])
def shipping():
    data = request.form
    cost = data['cost']
    cartId = data['cartId']
    return render_template("shipping.jinja", cartId=cartId, cost=cost)


def _authorize(orderId):
    # authorize payment on moltin
    moltin.ensure_auth()
    req = moltin.authorize_payment(orderId)

    return req


@app.route('/confirmation', methods=["POST"])
def confirmation():
    cartId = request.form['cartId']
    address1 = request.form['address1']
    address2 = request.form['address2']
    city = request.form['city']
    state = request.form['state']
    zipcode = request.form['zip']
    country = request.form['country']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']

    ethAddress = db.getCustomerAddress(email)

    json = {
        "data": {
            "customer": {
                "email": email,
                "name": ("%s %s" % (firstname, lastname))
            },
            "billing_address": {
                "first_name": firstname,
                "last_name": lastname,
                "company_name": "NA",
                "line_1": address1,
                "line_2": address2,
                "city": city,
                "postcode": zipcode,
                "county": "NA",
                "country": country
            },
            "shipping_address": {
                "first_name": firstname,
                "last_name": lastname,
                "company_name": "NA",
                "line_1": address1,
                "line_2": address2,
                "city": city,
                "postcode": zipcode,
                "county": "NA",
                "country": country
            }
        }
    }

    # send order request to moltin
    customer = moltin.solidRequest(
        moltin.checkout, cartId=cartId, orderData=json)
    orderId = customer['data']['id']

    # store order info in local DB
    db.newOrder(orderId, json)

    # subscribe to transfer event w/ customer address filter
    ethio.handlePayment(ethAddress)

    # authorize payment manually
    req = _authorize(orderId)

    # delete cart after payment
    moltin.ensure_auth()
    moltin.delete_cart(cartId)

    # email user with confirmation
    sendEmail(email, "Order received",
              "Thank you for your purchase. Your gear will ship as soon as your payment is received.")

    return render_template("confirmation.jinja", orderid=orderId, code=200)


@app.route('/price')
def price():
    # price in CENTS
    return "420"


@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('scripts', path)


@app.route('/support')
def support():
    return render_template('support.jinja', supportEmail=SUPPORT_EMAIL)


# RUN THAT  ===================================================================
if __name__ == '__main__':
    # TODO: disable debug
    app.run(debug=True, host='0.0.0.0', port=5000)
