
from backend_pfe.db import db
from pymongo import MongoClient
from responsesTemplate.db import get_client_response_for_question, get_clients_responses
from questionsTemplate.db import get_all_questions
from bson import json_util

from users.db import find_user_by_email

templates_collections = db['questions']

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
    all_questions = json_util.loads(get_all_questions())
    if not all_questions:
        return {"error": "No questions found"}


    survey = {
        "company_id": company.get("_id"),
        "company_email": company.get("email"),
        "questions": []
    }


    for question in all_questions:
        # filtres de la company
        question_filters = question.get("templates",[])

        # verifier si la question est applicable 
        if any(f in filters for f in question_filters):
            ## oui => editable
            survey["questions"].append({
                "questionId": question.get("_id"),
                "question": question.get("question"),
                "type": question.get("type"),
                "responsesPossible": question.get("responsesPossible", []),
                "status": "editable",
                "preFilledResponse": None
            })
        else:
            ## non => preFilled
            survey["questions"].append({
                "questionId": question.get("_id"),
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
        question = response.get("question")
        engagements_chosen = response.get("engagementsChosen", [])

        if engagements_chosen:
            engagements.append({
                "question": question,
                "engagementsChosen": engagements_chosen
            })

    
    return {"engagements": engagements}  