import requests
from flask import session

# must be populated here or by caller
MOLTIN_CID = ''
MOLTIN_CSC = ''


def config(keydata):
    global MOLTIN_CID
    global MOLTIN_CSC
    MOLTIN_CID = keydata['cid']
    MOLTIN_CSC = keydata['csc']


def auth_header():
    res = session.get('moltinKey', 'not set')
    if (res == 'not set'):
        print("GENERATING NEW FRINKIN KEY.")
        auth = auth_moltin()
    else:
        print("NICE: %s" % res)
        auth = res

    return auth


def auth_moltin():
    url = "https://api.moltin.com/oauth/access_token"
    data = {'client_id': MOLTIN_CID,
            'client_secret': MOLTIN_CSC, 'grant_type': "client_credentials"}

    req = requests.post(url, data=data)
    res = req.json()

    authTokenType = res['token_type']
    authToken = res['access_token']

    auth = "%s %s" % (authTokenType, authToken)
    authHeader = {'Authorization': auth}
    session['moltinKey'] = authHeader
    return authHeader


# {bitch functions} these return request results
def get_products():
    url = "https://api.moltin.com/v2/products"
    return requests.get(
        url, headers=auth_header())


def get_file(imgId):
    url = "https://api.moltin.com/v2/files/%s" % imgId
    return requests.get(
        url, headers=auth_header())


def get_product(productId):
    # fetch data from DB to build product page with pid
    url = "https://api.moltin.com/v2/products/%s" % str(productId)

    return requests.get(
        url, headers=auth_header())


def add_cart_item(itemId, quantity):
    json = {"data": {"id": itemId, "type": "cart_item",
                     "quantity": int(quantity)}}
    url = "https://api.moltin.com/v2/carts/%s/items" % cartId
    return requests.post(
        url, json=json, headers=auth_header())


def get_cart_items(cartId):
    url = "https://api.moltin.com/v2/carts/%s/items" % cartId
    return requests.get(url, headers=auth_header())


def checkout(cartId):
    url = "https://api.moltin.com/v2/carts/%s/checkout" % cartId
    return requests.post(url, json=json, headers=auth_header())


def authorize_payment(orderId):
    url = "https://api.moltin.com/v2/orders/%s/payments" % orderId
    json = {"data": {"gateway": "manual", "method": "authorize"}}
    return requests.post(url, json=json, headers=auth_header())


def delete_cart(cartId):
    url = "https://api.moltin.com/v2/carts/%s" % cartId
    return requests.delete(url, headers=auth_header())


def get_settings():
    url = "https://api.moltin.com/v2/settings"
    return requests.get(url, headers=auth_header())
# end {bitch code}


# request wrapper, makes sure user is authenticated b4 returning result
# returns json from request result
# returns error after 3 failed auth attempts
def solidRequest(function, **kwargs):
    req = function(**kwargs)
    print(req)
    print(session)

    # if invalid key
    i = 0
    try:
        while (req.status_code == 401 and i < 3):
            print("gay fish")
            # renew key
            auth_moltin()
            req = function(**kwargs)

        return req.json()
    except Exception as e:
        return {"error": e}


# forces auth by trying to make a trivial request & authenticating if needed
# should be used if calling the {bitch functions} manually
def ensure_auth(session):
    request(get_settings)
