
from backend_pfe.db import db
from pymongo import MongoClient
from responsesTemplate.db import get_client_response_for_question, get_clients_responses
from questionsTemplate.db import get_all_questions
from bson import json_util

templates_collections = db['questionnaires']

### cette methode va recupere les infos du templates qui nous interresse pour le client en particulié
def filter_Questions(company_id):
    have_workers = False
    have_product = False
    have_owner = False
    have_location= False

    questions = json_util.loads(get_all_questions())

    id_question_worker = None
    id_question_facility = None
    id_question_produit = None
    id_question_owned_facility = None

    for question in questions:
        if question.get('filtre') == 'WORKERS':
            id_question_worker = question.get('_id')
        elif question.get('filtre') == 'FACILITY':
            id_question_facility = question.get('_id')
        elif question.get('filtre') == 'PRODUIT':
            id_question_produit = question.get('_id')
        elif question.get('filtre') == 'OWNED FACILITY':
            id_question_owned_facility = question.get('_id')
    
	
    ## recuperer si la company a des WORKERS
    worker_response = None
    if id_question_worker:
        worker_response = get_client_response_for_question(company_id, id_question_worker)
        if worker_response and int(worker_response) > 0:
            have_workers= True

    ## recuperer si la company a des PRODUIT
    produit_response = None
    if id_question_produit:
        produit_response = get_client_response_for_question(company_id, id_question_produit)
        if produit_response  in ["oui", "yes"]:
            have_product = True

    ## recuperer si la company a des OWNED FACILITY 
    owner_response = None
    if id_question_owned_facility:
        owner_response = get_client_response_for_question(company_id, id_question_owned_facility)
        if owner_response  in ["oui", "yes"]:
            have_owner = True

    ## recuperer si la company a des FACILITY 
    location_response = None
    if id_question_facility:
        location_response = get_client_response_for_question(company_id, id_question_facility)
        if location_response  in ["oui", "yes"]:
            have_location = True

    return {
        "have_workers": have_workers,
        "have_product": have_product,
        "have_owner": have_owner,
        "have_location": have_location
    }


