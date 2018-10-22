import redis

REDIS_HOST = '172.70.0.4'

red = redis.StrictRedis(host=REDIS_HOST)


def newOrder(orderId, customerData):
    red.set('order:%s' % orderId, customerData)


def getOrder(orderId):
    return red.get('order:%s' % orderId)


def setCustomerAddress(email, ethAddress):
    red.set('customer:%s' % email, ethAddress)


def getCustomerAddress(email):
    return red.get('customer:%s' % email)
