from flask import Flask, current_app, g
import redis
import os
import socket
import argparse

# Connect to Redis
def get_redis():
   if 'redis' not in g:
      r = redis.Redis(host=current_app.config['REDIS_HOST'],port=int(current_app.config['REDIS_PORT']),password=current_app.config.get('REDIS_PASSWORD'))
      g.redis = r
   return g.redis

app = Flask(__name__)

@app.route("/webhook")
def webhook():
    try:
        redis = get_redis()
        count = redis.incr("counter")
    except RedisError:
        count = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Webhook registering callback</h3>" \
        "<b>Count:</b> {count}"
    return html.format(count=count)

@app.route("/status")
def status():
    try:
        redis = get_redis()
        count = int(redis.get("counter"))
    except RedisError:
        count = "<i>cannot connect to Redis, counter disabled</i>"

    html = "<h3>Total callbacks</h3>" \
        "<b>Count:</b> {count}"
    return html.format(count=count)

@app.route('/healthz')
def healthz():
    return 'Webhook alive alive-o'


def from_env(name,default_value,dtype=str):
   return dtype(os.environ[name]) if name in os.environ else default_value

def create_app(host='0.0.0.0',port=6379,password=None,app=None):
   if 'REDIS_HOST' not in app.config:
      app.config['REDIS_HOST'] = from_env('REDIS_HOST',host)
   if 'REDIS_PORT' not in app.config:
      app.config['REDIS_PORT'] = from_env('REDIS_PORT',port,dtype=int)
   if 'REDIS_PASSWORD' not in app.config:
      app.config['REDIS_PASSWORD'] = from_env('REDIS_PASSWORD',password)
   return app

class Config(object):
   DEBUG=True
   REDIS_HOST = from_env('REDIS_HOST','0.0.0.0')
   REDIS_PORT = from_env('REDIS_PORT',6379,dtype=int)
   REDIS_PASSWORD = from_env('REDIS_PASSWORD',None)

def main():
   argparser = argparse.ArgumentParser(description='Web')
   argparser.add_argument('--host',help='Redis host',default='0.0.0.0')
   argparser.add_argument('--port',help='Redis port',type=int,default=6379)
   argparser.add_argument('--password',help='Redis password')
   argparser.add_argument('--config',help='configuration file')
   args = argparser.parse_args()

   create_app(host=args.host,port=args.port,password=args.password,app=app)
   if args.config is not None:
      import os
      app.config.from_pyfile(os.path.abspath(args.config))
   app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
   main()

