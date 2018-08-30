import os, sys
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
import stripe

import ethio

SUPPORT_EMAIL = "damonsmedley12@gmail.com"

### SETUP
stripe_keys = {
    # TODO: Move these into system environment vars (or files)
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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/charge', methods=['POST'])
def charge():
    # amount in cents
    amount = request.form['amount']
    dollars = request.form['dollars']
    coins = request.form['coins']
    address = request.form['address']

    try:
        customer = stripe.Customer.create(
            email = request.form['stripeEmail'],
            source = request.form['stripeToken'],
        )
        print(customer, file=sys.stderr)

        charge = stripe.Charge.create(
            customer = customer.id,
            amount = amount,
            currency = 'usd',
            description = 'CWBY web payment'
        )
        print(charge, file=sys.stderr)
        
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
                print(ethResult, file=sys.stderr)
            except Exception as e:
                print("something went wrong with the ETH transaction\n%s" % str(e), file=sys.stderr)
                ethResult = 'none'

            # return confirmation page
            return render_template('charge.html', amount=amount, dollars=dollars, coins=coins, address=address, txid=str(ethResult))

    # except stripe.error.CardError as e:
    #     # card was declined
    #     return redirect("/#", code=302)
    # except stripe.error.IdempotencyError as e:
    #     # token was used more than once
    #     print(e, file=sys.stderr)
    #     return redirect("/#", code=303)
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