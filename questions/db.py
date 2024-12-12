import uuid

from backend_pfe.db import db


# Référence à la collection MongoDB
questions_collection = db['questions']

from pymongo import MongoClient


import uuid

def create_multiple_choice_question(enjeu, question_text, templates, responses, esg):
    """
    Créer une question de type choixMultiple avec un ID unique.
    """
    question_id = str(uuid.uuid4())  # Générer un ID unique

    # Construction des réponses avec leurs labels et scores
    responses_possible = [
        {
            "id": str(i + 1),
            "label": response.get('label'),
            "scoreESG": response.get('scoreESG', 0.0),  # Par défaut, scoreESG = 0.0 si non fourni
            "scoreEngagement": response.get('scoreEngagement', 0.0)  # Par défaut, scoreEngagement = 0.0 si non fourni
        }
        for i, response in enumerate(responses)
    ]

    # Calcul du scoreTotal : somme des scoresESG des réponses possibles divisé par 2
    score_total = sum(response.get('scoreESG', 0.0) for response in responses_possible) / 2

    question = {
        "id": question_id,
        "enjeu": enjeu,
        "question": question_text,
        "templates": templates,
        "type": "choixMultiples",
        "responsesPossible": responses_possible,
        "ESG": esg,
        "scoreTotal": score_total,
    }

    questions_collection.insert_one(question)
    return question_id




def create_open_question(enjeu, question_text, templates, esg):
    """
    Créer une question de type ouverte avec un ID unique.
    Une seule réponse possible est prévue, initialement vide.
    Les scores ESG et Engagement sont initialisés à 0.00.
    Le scoreTotal est fixé à 0.00 par défaut pour les questions ouvertes.
    """
    question_id = str(uuid.uuid4())  # Générer un ID unique

    question = {
        "id": question_id,
        "enjeu": enjeu,
        "question": question_text,
        "templates": templates,
        "type": "vide",
        "responsesPossible": [
            {
                "id": "1",
                "label": "",  # Réponse initialement vide
                "scoreESG": 0.00,
                "scoreEngagement": 0.00
            }
        ],
        "ESG": esg,
        "scoreTotal": 0.00
    }

    questions_collection.insert_one(question)
    return question_id



def delete_question_by_id(question_id):
    """
    Supprime une question de la collection en fonction de son ID.
    :param question_id: L'ID de la question à supprimer.
    :return: True si une question a été supprimée, sinon False.
    """
    result = questions_collection.delete_one({"id": question_id})
    return result.deleted_count > 0  # Retourne True si une suppression a été effectuée


def update_question(question_id, updates):
    """
    Met à jour une question existante en fonction de son ID.
    :param question_id: L'ID de la question à mettre à jour.
    :param updates: Un dictionnaire contenant les champs à mettre à jour.
    :return: True si une mise à jour a été effectuée, sinon False.
    """
    result = questions_collection.update_one(
        {"id": question_id},
        {"$set": updates}
    )
    return result.modified_count > 0

def get_all_questions():
    """
    Récupère toutes les questions depuis la base de données.
    :return: Une liste de toutes les questions.
    """
    return list(questions_collection.find())

def get_question_by_id(question_id):
    """
    Récupérer une question en fonction de son ID.
    """
    question = questions_collection.find_one({"id": question_id})
    if question:
        question["_id"] = str(question["_id"])  # Convertir ObjectId en chaîne pour le JSON
    return question








