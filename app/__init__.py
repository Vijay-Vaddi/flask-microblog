from flask import Flask

app = Flask(__name__)
# imported after creating app to avoid common flask problem of secular dependencies 

from app import routes 