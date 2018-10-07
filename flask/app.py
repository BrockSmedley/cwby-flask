import os
import sys
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, abort
import requests
import stripe
import binascii
from flask_talisman import Talisman

import ethio

force_https = False
SUPPORT_EMAIL = "damonsmedley12@gmail.com"

MOLTIN_SID = '1884465437547168601'
MOLTIN_CID = 'x60kAvxYDej5b3sabMWHy08xi0Z24S6CYJeoaaGouZ'
MOLTIN_CSC = 'db2gPRaGP9zDhBoP1bUf3U4uPG3dxwlsyJSkKzFi7C'

moltin_auth_url = "https://api.moltin.com/oauth/access_token"
moltin_auth_body = {'client_id': MOLTIN_CID,
                    'client_secret': MOLTIN_CSC, 'grant_type': "client_credentials"}

auth_req = requests.post(moltin_auth_url, data=moltin_auth_body)
auth_resp = auth_req.json()

auth_token_type = auth_resp['token_type']
auth_token = auth_resp['access_token']

auth = "%s %s" % (auth_token_type, auth_token)
auth_header = {'Authorization': auth}
print(auth_header)

csp = {
    'default-src': [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'"  # change this!
    ]
}

# SETUP
# stripe keyfile must have secret key on first line and pub key on second
keyfile = open('.stripekeys', 'r')
secret_key = keyfile.readline().strip('\n')
publishable_key = keyfile.readline().strip('\n')
keyfile.close()
stripe_keys = {
    # TODO: Move these into system environment vars (or files)
    # os.environ['VAR_NAME']
    'secret_key': secret_key,
    'publishable_key': publishable_key
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__, static_url_path='')
# Talisman(app, force_https=force_https, content_security_policy=csp)


# APP ROUTES
@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


# product description page
@app.route('/product/<pid>', methods=['GET'])
def product(pid):
    print(pid, file=sys.stderr)
    # fetch data from DB to build product page with pid
    url = "https://api.moltin.com/v2/products/%s" % str(pid)

    print(url, file=sys.stderr)
    productRequest = requests.get(
        url, headers=auth_header)

    jdata = productRequest.json()

    if ('errors' in jdata):
        print(jdata['errors'], file=sys.stderr)
        abort(404)

    print("JDATA")
    print(jdata, file=sys.stderr)
    productData = jdata['data']
    metaData = productData['meta']

    if (metaData['stock']['availability'] != "in-stock"):
        return render_template("product.html", pid=pid, cost=999999, status="Sold Out")

    name = productData['name']
    description = productData['description']
    price = productData['price'][0]['amount']

    imageId = productData['relationships']['main_image']['data']['id']
    url = "https://api.moltin.com/v2/files/%s" % imageId
    imgReq = requests.get(url, headers=auth_header)
    imgResult = imgReq.json()
    imgUrl = imgResult['data']['link']['href']

    # add arguments for product data
    return render_template('product.html', name=name, description=description, cost=price, imgUrl=imgUrl)


@app.route('/charge', methods=['POST'])
def charge():
    # amount in cents
    amount = request.form['amount']
    dollars = request.form['dollars']
    coins = request.form['coins']
    address = request.form['address']

    try:
        customer = stripe.Customer.create(source=request.form['stripeToken'])

        #print(customer, file=sys.stderr)

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='CWBY web payment'
        )
        #print(charge, file=sys.stderr)

        if (charge['outcome']['network_status'] != "approved_by_network"):
            # transaction error
            return render_template('error.html', charge=charge, customer=customer, supportEmail=SUPPORT_EMAIL)
        else:
            # payment processed successfully
            # disburse coins
            ethResult = ''
            try:
                ethResult = ethio.orderCoins(coins, address)
                #print(ethio.getProvider(), file=sys.stderr)
                #print(ethResult, file=sys.stderr)
            except Exception as e:
                print("something went wrong with the ETH transaction\n%s" %
                      str(e), file=sys.stderr)
                ethResult = 'none'

            # return confirmation page
            return render_template('charge.html', amount=amount, dollars=dollars, coins=coins, address=address, txid=ethResult)
    except Exception as e:
        print(e, file=sys.stderr)
        return redirect("/#", code=302)


@app.route('/price')
def price():
    # price in CENTS
    return "420"


@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('scripts', path)


@app.route('/support')
def support():
    return render_template('support.html', supportEmail=SUPPORT_EMAIL)


# RUN THAT SHIT
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
