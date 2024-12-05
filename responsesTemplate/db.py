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
    return list(db['template_responses'].find({"company_id": company_id}))


