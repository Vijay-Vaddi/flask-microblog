from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

''' imported after creating app to avoid common 
flask problem of secular dependencies''' 
from app import routes 