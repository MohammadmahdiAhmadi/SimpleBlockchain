from flask import Flask

app = Flask(__name__)

from app import nodes_connection

from app import views