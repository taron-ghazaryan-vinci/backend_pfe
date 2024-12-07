import uuid

from backend_pfe.db import db


# Référence à la collection MongoDB
questions_collection = db['questions']

from pymongo import MongoClient


import uuid

def create_multiple_choice_question(enjeu, question_text, templates, responses):
    """
    Créer une question de type choixMultiple avec un ID unique.
    """
    question_id = str(uuid.uuid4())  # Générer un ID unique

    question = {
        "id": question_id,
        "enjeu": enjeu,
        "question": question_text,
        "templates": templates,
        "type": "choixMultiples",
        "responsesPossible": [
            {"id": str(i + 1), "label": response, "scoreESG": None, "scoreEngagement": None}
            for i, response in enumerate(responses)
        ]
    }

    questions_collection.insert_one(question)
    return question_id



def create_open_question(enjeu, question_text, templates):
    """
    Créer une question de type ouverte avec un ID unique.
    """
    question_id = str(uuid.uuid4())  # Générer un ID unique

    question = {
        "id": question_id,
        "enjeu": enjeu,
        "question": question_text,
        "templates": templates,
        "type": "ouverte",
        "responsesPossible": []
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







