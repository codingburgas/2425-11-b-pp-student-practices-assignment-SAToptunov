from flask import Blueprint
bp = Blueprint('classifier', __name__)
from app.classifier import routes