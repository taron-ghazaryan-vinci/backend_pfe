import uuid

from backend_pfe.db import db
import bcrypt
from pymongo import MongoClient

from questionsTemplate.db import question_is_valid

# Référence à la collection MongoDB
users_collection = db['users']
question_collection = db['questions']


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
        "responses": [],
        "boolean_esg": False,
        "rapport" : False,
        "etat_rapport": None,
        "etat_esg" : None
    }
    return users_collection.insert_one(user).inserted_id

def update_etat_rapport(user_id, new_etat_rapport):
    """
    Mettre à jour le champ 'etat_rapport' d'un utilisateur avec une nouvelle valeur.
    """
    try:
        result = users_collection.update_one(
            {"id": user_id},  # Rechercher l'utilisateur par ID
            {"$set": {"etat_rapport": new_etat_rapport}}  # Mettre à jour 'etat_rapport'
        )
        return result.matched_count > 0  # Retourne True si la mise à jour a été effectuée
    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour de l'état du rapport : {str(e)}")

def update_etat_esg(user_id, new_etat_esg):
    """
    Mettre à jour le champ 'etat_esg' d'un utilisateur avec une nouvelle valeur.
    """
    try:
        result = users_collection.update_one(
            {"id": user_id},  # Rechercher l'utilisateur par ID
            {"$set": {"etat_esg": new_etat_esg}}  # Mettre à jour 'etat_esg'
        )
        return result.matched_count > 0  # Retourne True si la mise à jour a été effectuée
    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour de l'état ESG : {str(e)}")


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

def set_boolean_esg_true(user_id):
    """
    Mettre à jour le champ 'boolean_esg' d'un utilisateur à True.
    """
    result = users_collection.update_one(
        {"id": user_id},
        {"$set": {"boolean_esg": True}}
    )
    return result.modified_count > 0  # Retourne True si une modification a été effectuée


def set_rapport_true(user_id):
    """
    Mettre à jour le champ 'rapport' d'un utilisateur à True.
    """
    try:
        result = users_collection.update_one(
            {"id": user_id},
            {"$set": {"rapport": True}}
        )
        return result.matched_count > 0
    except Exception as e:
        raise Exception(f"Erreur lors de la mise à jour : {str(e)}")



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
            # Récupérer les détails des réponses choisies (sans scores)
            chosen_responses_details = []
            for chosen_response in response.get("responsesChosen", []):
                matching_response = next(
                    (r for r in question["responsesPossible"] if r["id"] == chosen_response["id"]), None
                )
                if matching_response:
                    chosen_responses_details.append({
                        "id": chosen_response["id"],
                        "label": matching_response["label"],
                        "comment": chosen_response.get("comment")
                    })

            # Récupérer les détails des engagements choisis (sans scores)
            engagements_chosen_details = []
            for chosen_engagement in response.get("engagementsChosen", []):
                matching_engagement = next(
                    (r for r in question["responsesPossible"] if r["id"] == chosen_engagement["id"]), None
                )
                if matching_engagement:
                    engagements_chosen_details.append({
                        "id": chosen_engagement["id"],
                        "label": matching_engagement["label"],
                        "comment": chosen_engagement.get("comment")
                    })

            # Ajouter les détails à la liste
            detailed_responses.append({
                "question_id": question_id,
                "question_text": question.get("question"),
                "responses_chosen": chosen_responses_details,
                "engagements_chosen": engagements_chosen_details,
                "scores": response.get("scores", {})  # Inclure uniquement les scores ici
            })

    return detailed_responses





def get_user_by_id(user_id):
    """
    Récupérer un utilisateur par son ID.
    """
    user = users_collection.find_one({"id": user_id}, {"_id": 0})  # Exclure le champ _id de MongoDB
    return user




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


def remove_id_from_responses_chosen(user_id, question_id, response_id_to_remove):
    """
    Supprime un ID spécifique dans responsesChosen pour une question donnée
    et met à jour le scoreESG.

    :param user_id: ID de l'utilisateur
    :param question_id: ID de la question
    :param response_id_to_remove: ID de la réponse à supprimer
    :return: Message de succès ou d'erreur
    """
    try:
        # Trouver l'utilisateur
        user = users_collection.find_one({"id": user_id})
        if not user:
            return {"status": "error", "message": "Utilisateur non trouvé."}

        updated = False  # Flag pour détecter une modification
        for response in user.get("responses", []):
            # Vérifie si la réponse correspond à la question
            if response.get("question") == question_id:
                # Supprimer l'ID dans responsesChosen
                original_length = len(response.get("responsesChosen", []))
                response["responsesChosen"] = [
                    item for item in response.get("responsesChosen", []) if item.get("id") != response_id_to_remove
                ]
                if len(response["responsesChosen"]) != original_length:
                    updated = True

                    # Mettre à jour scoreESG en fonction des réponses restantes
                    question = question_collection.find_one({"id": question_id})
                    if question:
                        responses_possible = {r["id"]: r for r in question.get("responsesPossible", [])}
                        remaining_scores = [
                            responses_possible[res["id"]]["scoreESG"]
                            for res in response["responsesChosen"]
                            if res["id"] in responses_possible
                        ]
                        # Calcul du nouveau scoreESG
                        response["scores"]["scoreESG"] = round(sum(remaining_scores), 2)

        # Mettre à jour l'utilisateur dans la base de données uniquement si une modification a été effectuée
        if updated:
            users_collection.update_one(
                {"id": user_id},
                {"$set": {"responses": user["responses"]}}
            )
            return {
                "status": "success",
                "message": f"L'ID {response_id_to_remove} a été supprimé avec succès de responsesChosen pour la question {question_id}."
            }
        else:
            return {
                "status": "error",
                "message": f"L'ID {response_id_to_remove} n'existe pas dans responsesChosen pour la question {question_id}."
            }
    except Exception as e:
        return {"status": "error", "message": f"Une erreur s'est produite : {str(e)}"}





def remove_id_from_engagements_chosen(user_id, question_id, engagement_id_to_remove):
    """
    Supprime un ID spécifique dans engagementChosen d'un utilisateur et met à jour le scoreEngagement.

    :param user_id: ID de l'utilisateur
    :param question_id: ID de la question correspondante
    :param engagement_id_to_remove: ID à supprimer de engagementChosen
    :return: Message de succès ou d'erreur
    """
    try:
        # Rechercher l'utilisateur par ID
        user = users_collection.find_one({"id": user_id})
        if not user:
            return {"status": "error", "message": "Utilisateur non trouvé."}

        # Trouver la réponse correspondant à la question_id
        response_to_update = next(
            (response for response in user.get("responses", []) if response.get("question") == question_id), None
        )
        if not response_to_update:
            return {"status": "error", "message": f"Aucune réponse trouvée pour la question {question_id}."}

        # Supprimer l'ID dans engagementChosen
        response_to_update["engagementsChosen"] = [
            item for item in response_to_update.get("engagementsChosen", []) if item.get("id") != engagement_id_to_remove
        ]

        # Recalculer le scoreEngagement
        question = question_collection.find_one({"id": question_id})
        if not question:
            return {"status": "error", "message": f"Question avec ID {question_id} non trouvée."}

        remaining_engagements = response_to_update["engagementsChosen"]
        updated_score_engagement = sum(
            next((engagement["scoreEngagement"] for engagement in question["responsesPossible"] if engagement["id"] == chosen["id"]), 0)
            for chosen in remaining_engagements
        )

        # Mettre à jour le scoreEngagement dans la réponse
        response_to_update["scores"]["scoreEngagement"] = round(updated_score_engagement, 2)

        # Mettre à jour la base de données
        users_collection.update_one(
            {"id": user_id},
            {"$set": {"responses": user["responses"]}}
        )

        return {"status": "success", "message": f"L'ID {engagement_id_to_remove} a été supprimé avec succès de engagementsChosen."}
    except Exception as e:
        return {"status": "error", "message": f"Une erreur s'est produite : {str(e)}"}
