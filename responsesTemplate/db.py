from backend_pfe.db import db
from pymongo import MongoClient
from bson import json_util
from bson import ObjectId

from questionsTemplate.db import get_question_by_id

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
    result =[]

    for r in responses:
        question_id = r.get("question_id")
        question = get_question_by_id(question_id)
        response_data = {
            "answer": r.get("answer"),
            "question": json_util.loads(question) if question else None 
        }
        result.append(response_data)

    return json_util.dumps(result)


def get_client_response_for_question(company_id, question_id):
    response = db['template_responses'].find_one({"company_id": company_id, "question_id": question_id})
    if response:
        return response.get('answer') 
    else:
        return None