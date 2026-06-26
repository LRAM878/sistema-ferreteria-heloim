import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-super-secreta-heloim-2026'
    # Configuración para MySQL con PyMySQL
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ferreteria.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False