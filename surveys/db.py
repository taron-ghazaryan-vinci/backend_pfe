import json

from backend_pfe.db import db
from pymongo import MongoClient
from responsesTemplate.db import get_client_response_for_question, get_clients_responses
from questionsTemplate.db import get_all_questions, get_question_by_id
from bson import ObjectId, json_util

from users.db import find_user_by_email

questions_collections = db['questions']

### pour creer le questionnaire du client
def create_survey(company_email):

    ### on commence par récupere tout les filtres qui concerne la company
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}
    
    filters = company.get('templates', [])
    if not filters:
        return {"error": "No filters found for the company"}
    

    ### on va chercher dans la table question toutes les questions
    all_questions = get_all_questions()
    if not all_questions:
        return {"error": "No questions found"}


    survey = {
        "company_id": str(company.get("_id")),
        "company_email": company.get("email"),
        "questions": []
    }


    for question in all_questions:
        # filtres de la company
        question_filters = question.get("templates")

        # verifier si la question est applicable 
        if any(f in question_filters for f in filters):
            ## oui => editable
            survey["questions"].append({
                "questionId": str(question.get("_id")),
                "question": question.get("question"),
                "type": question.get("type"),
                "responsesPossible": question.get("responsesPossible", []),
                "status": "editable",
                "preFilledResponse": None
            })
        else:
            ## non => preFilled
            survey["questions"].append({
                "questionId": str(question.get("_id")),
                "question": question.get("question"),
                "type": question.get("type"),
                "responsesPossible": question.get("responsesPossible", []),
                "status": "preFilled",
                "preFilledResponse": "N/A"
            })

    ## return le questionnaire personalisé dynamique        
    return survey


def get_all_questions():
    questions = list(db['questions'].find())
    return questions


def get_engagements_clients(company_email):
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}
  
    client_responses = company.get('responses', [])
    if not client_responses:
        return {"error": "No responses found for the company"}

    engagements = []

    for response in client_responses:
        question_id = response.get("question")
        q = get_question_by_id(question_id)
        if not q:
            return {"error": "No question found for the id"}

        question = q.get("question")
        engagements_chosen_user = response.get("engagementsChosen", [])

        responses_possible = q.get("responsesPossible", [])
        engagements_chosen =[]

        for r in responses_possible:
            if r.get("id") in engagements_chosen_user:
                engagements_chosen.append(r)

        if engagements_chosen:
            engagements.append({
                "question": question,
                "engagementsChosen": engagements_chosen
            })

    
    return {"engagements": engagements}

def submit_one_question(company_email, question_id, responses, engagements):
    # Rechercher l'utilisateur par email
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}

    # Récupérer la question par son ID
    question = questions_collections.find_one({"id": question_id})
    if not question:
        return {"error": "Question introuvable"}

    # Calculer les scores pour les réponses choisies
    score_esg = 0
    score_engagement = 0

    # Parcourir les réponses possibles et calculer les scores
    for response_id in responses:
        response = next((r for r in question.get('responsesPossible', []) if r['id'] == response_id), None)
        if response:
            score_esg += response.get('scoreESG', 0)

    for engagement_id in engagements:
        engagement = next((r for r in question.get('responsesPossible', []) if r['id'] == engagement_id), None)
        if engagement:
            score_engagement += engagement.get('scoreEngagement', 0)

    # Obtenir ou initialiser la liste des réponses
    responses_list = company.get('responses', [])

    # Vérifier si une réponse existe déjà pour cette question
    existing_response = next((r for r in responses_list if r["question"] == question_id), None)
    if existing_response:
        # Mettre à jour les réponses existantes
        existing_response["responsesChosen"] = responses
        existing_response["engagementsChosen"] = engagements
        existing_response["scores"]["scoreESG"] = score_esg
        existing_response["scores"]["scoreEngagement"] = score_engagement
    else:
        # Ajouter une nouvelle réponse
        new_response = {
            "question": question_id,
            "responsesChosen": responses,
            "engagementsChosen": engagements,
            "scores": {
                "scoreESG": score_esg,
                "scoreEngagement": score_engagement
            }
        }
        responses_list.append(new_response)

    # Mettre à jour la liste des réponses dans MongoDB
    db.users.update_one(
        {"email": company_email},
        {"$set": {"responses": responses_list}}
    )

    return {"message": "Response submitted successfully"}


