import uuid

from backend_pfe.db import db
import bcrypt
from pymongo import MongoClient

from questionsTemplate.db import question_is_valid

# Référence à la collection MongoDB
users_collection = db['users']
question_collection = db['questions']

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



def get_user_responses_by_email(email):
    """
    Récupérer les réponses d'un utilisateur avec les détails des questions en utilisant son email.
    """
    # Rechercher l'utilisateur par email
    user = users_collection.find_one({"email": email}, {"responses": 1, "_id": 0})
    if not user or "responses" not in user:
        return []

    # Parcourir les réponses et récupérer les détails de chaque question et réponse choisie
    responses = user["responses"]
    detailed_responses = []

    for response in responses:
        question_id = response.get("question")
        question = question_collection.find_one({"id": question_id}, {"_id": 0})

        if question:
            # Récupérer les détails des réponses choisies
            chosen_responses_details = []
            for response_id in response.get("responsesChosen", []):
                matching_response = next(
                    (r for r in question["responsesPossible"] if r["id"] == response_id), None
                )
                if matching_response:
                    chosen_responses_details.append({
                        "id": response_id,
                        "label": matching_response["label"]
                    })

            # Récupérer les détails des engagements choisis
            engagements_chosen_details = []
            for engagement_id in response.get("engagementsChosen", []):
                matching_engagement = next(
                    (r for r in question["responsesPossible"] if r["id"] == engagement_id), None
                )
                if matching_engagement:
                    engagements_chosen_details.append({
                        "id": engagement_id,
                        "label": matching_engagement["label"]
                    })

            # Ajouter les détails à la liste
            detailed_responses.append({
                "question_id": question_id,
                "question_text": question.get("question"),
                "responses_chosen": chosen_responses_details,
                "engagements_chosen": engagements_chosen_details,
                "scores": response.get("scores", {})
            })

    return detailed_responses


def update_user_responses(email, question_id, responses_chosen, engagements_chosen):
    """
    Met à jour les réponses d'un utilisateur pour une question donnée et recalcule les scores.

    :param email: Email de l'utilisateur.
    :param question_id: ID de la question.
    :param responses_chosen: Liste des IDs des réponses choisies.
    :param engagements_chosen: Liste des IDs des engagements choisis.
    :return: True si la mise à jour a réussi, sinon False.
    """
    # Vérifier si l'utilisateur existe
    user = users_collection.find_one({"email": email})
    if not user:
        return {"error": "Utilisateur introuvable"}

    # Vérifier si la question existe
    question = question_collection.find_one({"id": question_id})
    if not question:
        return {"error": "Question introuvable"}

    # Calcul des nouveaux scores
    new_score_esg = 0.0
    new_score_engagement = 0.0

    # Ajouter les scores des réponses choisies
    for response_id in responses_chosen:
        response = next((r for r in question["responsesPossible"] if r["id"] == response_id), None)
        if response:
            new_score_esg += response.get("scoreESG", 0.0)
            new_score_engagement += response.get("scoreEngagement", 0.0)

    # Ajouter les scores des engagements choisis
    for engagement_id in engagements_chosen:
        engagement = next((r for r in question["responsesPossible"] if r["id"] == engagement_id), None)
        if engagement:
            new_score_esg += engagement.get("scoreESG", 0.0)
            new_score_engagement += engagement.get("scoreEngagement", 0.0)

    # Mettre à jour les réponses dans la base de données
    result = users_collection.update_one(
        {"email": email, "responses.question": question_id},
        {
            "$set": {
                "responses.$.responsesChosen": responses_chosen,
                "responses.$.engagementsChosen": engagements_chosen,
                "responses.$.scores": {
                    "scoreESG": round(new_score_esg, 2),
                    "scoreEngagement": round(new_score_engagement, 2),
                },
            }
        }
    )

    # Si aucune réponse existante pour cette question, ajouter une nouvelle entrée
    if result.matched_count == 0:
        users_collection.update_one(
            {"email": email},
            {
                "$push": {
                    "responses": {
                        "question": question_id,
                        "responsesChosen": responses_chosen,
                        "engagementsChosen": engagements_chosen,
                        "scores": {
                            "scoreESG": round(new_score_esg, 2),
                            "scoreEngagement": round(new_score_engagement, 2),
                        },
                    }
                }
            }
        )

    return {"message": "Réponses mises à jour avec succès"}
