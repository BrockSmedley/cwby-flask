import os
from flask import Flask, render_template, request, redirect, send_from_directory
import stripe

### SETUP
stripe_keys = {
    # TODO: Move these into system environment vars
    # os.environ['VAR_NAME']
    'secret_key': 'sk_test_dwKjrYs3uesCqpl7cPpWkXmY',
    'publishable_key': 'pk_test_zgMCciFrinSpuc74Mp825Asb'
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__, static_url_path='')


### APP ROUTES
@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])

@app.route('/charge', methods=['POST'])
def charge():
    # amount in cents
    amount = request.form['amount']
    dollars = request.form['dollars']
    coins = request.form['coins']
    address = request.form['address']

    try:
        customer = stripe.Customer.create(
            email = 'brocksmedley@gmail.com',
            source = request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer = customer.id,
            amount = amount,
            currency = 'usd',
            description = 'CWBY web payment'
        )
        return render_template('charge.html', amount=amount, dollars=dollars, coins=coins, address=address)

    except Exception as identifier:
        return redirect("/#/", code=302)


@app.route('/price')
def price():
    # price in CENTS
    return "420"


@app.route('/js/<path:path>')
def js(path):
    return send_from_directory('scripts', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)