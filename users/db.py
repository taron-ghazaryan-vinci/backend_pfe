from backend_pfe.db import db
import bcrypt
from pymongo import MongoClient

# Référence à la collection MongoDB
users_collection = db['users']

def create_user(username, email, password):
    """Créer un utilisateur"""
    # Hacher le mot de passe avant de le stocker
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        "username": username,
        "email": email,
        "password": hashed_password
    }
    return users_collection.insert_one(user).inserted_id

def find_user_by_email(email):
    """Rechercher un utilisateur par email"""
    return users_collection.find_one({"email": email})

def check_password(stored_password, provided_password):
    """
    Vérifier si le mot de passe fourni correspond au mot de passe haché.
    :param stored_password: Mot de passe haché récupéré de la base de données.
    :param provided_password: Mot de passe en clair fourni par l'utilisateur.
    :return: True si les mots de passe correspondent, sinon False.
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
