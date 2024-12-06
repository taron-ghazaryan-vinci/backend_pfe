from backend_pfe.db import db
from pymongo import MongoClient

templates_collections = db['template_responses']

def submit_client_response(answer,company_id,question_id):
    answer_question = {
        "question_id": question_id,
        "company_id": company_id,
        "answer": answer,

    }
    return templates_collections.insert_one(answer_question).inserted_id

def get_clients_responses(company_id):
    responses = list(db['template_responses'].find({"company_id": company_id}))
    return json_util.dumps(responses)


def get_client_response_for_question(company_id, question_id):
    response = db['template_responses'].find_one({"company_id": company_id, "question_id": question_id})
    if response:
        return response.get('answer') 
    else:
        return None