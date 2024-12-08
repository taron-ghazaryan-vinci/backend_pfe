import uuid

from backend_pfe.db import db
import bcrypt
from pymongo import MongoClient

# Référence à la collection MongoDB
users_collection = db['users']

def get_all_users():
    """
    Récupérer tous les utilisateurs.
    """
    users = list(users_collection.find({}, {"_id": 0}))  # Exclure le champ _id de MongoDB
    return users

def create_user(username, email, password, role):
    """Créer un utilisateur"""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user_id = str(uuid.uuid4())

    # Créer l'utilisateur
    user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password": hashed_password,
        "role": role,
        "template": False,
        "templates": None,
        "responses": []
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

def set_user_template_true(custom_id):
    """
    Mettre à jour le champ 'template' d'un utilisateur en fonction de l'attribut personnalisé 'id'.
    Définit le champ 'template' à True.
    """
    result = users_collection.update_one(
        {"id": custom_id},
        {"$set": {"template": True}}
    )
    return result.modified_count > 0  # Retourne True si une modification a été effectuée


def get_user_by_id(user_id):
    """
    Récupérer un utilisateur par son ID.
    """
    user = users_collection.find_one({"id": user_id}, {"_id": 0})  # Exclure le champ _id de MongoDB
    return user


