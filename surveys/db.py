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
        question_filters = question.get("templates",[])

        # verifier si la question est applicable 
        if any(f in filters for f in question_filters):
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


def calculate_score_for_issue(company_email, issue_name):
    """
    Calcule les scores ESG et Engagement pour un enjeu donné, en ignorant les questions sans score.
    """
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}

    questions = db.questions.find({"enjeu": issue_name})
    print(questions)

    total_score_esg = 0
    total_score_engagement = 0
    max_score = 0

    for question in questions:
        question_id = question["id"]

        # Vérifier si la question a un score total
        if "scoreTotal" not in question or question["scoreTotal"] == 0:
            continue  # Ignorer cette question

        # Ajouter le score total de la question au maximum de l'enjeu
        max_score += question["scoreTotal"]

        # Récupérer les réponses de l'utilisateur pour cette question
        user_response = next((resp for resp in company["responses"] if
                              resp["question"] == question_id), None)
        if user_response:
            # Scores ESG des réponses choisies
            total_score_esg += sum(
                next((resp["scoreESG"] for resp in
                      question.get("responsesPossible", []) if
                      resp["id"] == chosen_id), 0)
                for chosen_id in user_response.get("responsesChosen", [])
            ) / 2
            # Scores Engagement des engagements pris
            total_score_engagement += sum(
                next((resp["scoreEngagement"] for resp in
                      question.get("responsesPossible", []) if
                      resp["id"] == chosen_id), 0)
                for chosen_id in user_response.get("engagementsChosen", [])
            ) / 2

    # Facteur de normalisation pour ajuster sur 5
    normalization_factor = 5 / max_score if max_score > 0 else 1

    # Normaliser les scores obtenus
    normalized_esg = total_score_esg * normalization_factor
    normalized_engagement = total_score_engagement * normalization_factor

    return {
        "issue": issue_name,
        "normalized_score_esg": normalized_esg,
        "normalized_score_engagement": normalized_engagement,
        "max_score": 5  # L'enjeu est toujours sur 5
    }

def calculate_scores_for_module(company_email, module):
    """
    Calcule les scores ESG et Engagement pour un module, en normalisant chaque enjeu sur 5.
    """
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}

    issues = db.questions.distinct("enjeu", {"ESG": module})
    total_esg = 0
    total_engagement = 0

    for issue in issues:
        issue_scores = calculate_score_for_issue(company_email, issue)
        total_esg += issue_scores["normalized_score_esg"]
        total_engagement += issue_scores["normalized_score_engagement"]

    return {
        "module": module,
        "total_score_esg": total_esg,  # Somme des scores ESG normalisés pour les 6 enjeux
        "total_score_engagement": total_engagement,  # Somme des scores Engagement normalisés pour les 6 enjeux
        "max_score": 30  # Chaque module est sur 30 (6 x 5)
    }

def calculate_global_score(company_email):
    """
    Calcule le score global ESG et Engagement pour un utilisateur identifié par email.
    Renvoie les scores ESG, Engagement et global normalisés sur 90 sous forme de chaînes de caractères,
    ainsi que le pourcentage global.
    """
    company = find_user_by_email(company_email)
    if not company:
        return {"error": "Company not found"}

    modules = ["E", "S", "G"]
    total_esg = 0
    total_engagement = 0
    total_max_score = 90  # 3 modules x 30

    for module in modules:
        module_scores = calculate_scores_for_module(company_email, module)
        total_esg += module_scores["total_score_esg"]
        total_engagement += module_scores["total_score_engagement"]

    total_score_global = total_esg + total_engagement
    global_score_on_90 = (total_score_global / 180) * 90
    score_percentage = (global_score_on_90 / total_max_score) * 100

    # Conversion en chaînes de caractères
    total_score_esg_str = f"{total_esg:.2f}/90"
    total_score_engagement_str = f"{total_engagement:.2f}/90"
    total_score_global_str = f"{global_score_on_90:.2f}/90"
    score_percentage_str = f"{score_percentage:.2f}%"

    return {
        "total_score_esg": total_score_esg_str,
        "total_score_engagement": total_score_engagement_str,
        "total_score_global": total_score_global_str,
        "score_percentage": score_percentage_str
    }


