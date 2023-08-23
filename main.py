# import config as conf
# from routes import app

# if __name__ == "__main__":
#     app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

import config as conf
from routes import app
from threading import Thread

def run():
  app.run(debug=conf.DEBUG, port=conf.PORT, host="0.0.0.0")

def keep_alive():
  t = Thread(target=run)
  t.start()

if __name__ == "__main__":
  run()