import redis

REDIS_HOST = '172.70.0.4'

red = redis.StrictRedis(host=REDIS_HOST)


def newOrder(customer, orderId):
    red.set('order:%s' % orderId, customer)


def getOrder(orderId):
    return red.get('order:%s' % orderId)
