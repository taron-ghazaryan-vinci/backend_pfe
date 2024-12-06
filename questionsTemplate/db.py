from backend_pfe.db import db
from pymongo import MongoClient
from bson import ObjectId

templates_collections = db['template_questions']

def create_question(question,filtre):
    if not question_is_valid(question):
        raise ValueError("La question ne peut pas être vide ou contenir uniquement des espaces.")
   
    template_question = {
        "question": question,
        "filtre": filtre
    }
    return templates_collections.insert_one(template_question).inserted_id


def delete_question_by_id(question_id):
    id = conversion(question_id)
    return db['template_questions'].delete_one({"_id": id})

def get_question_by_id(question_id):
    id = conversion(question_id)
    return db['template_questions'].find_one({"_id": id })

def get_all_questions():
    return list(db['template_questions'].find())

def update_question_by_id(question_id,new_question):
    id = conversion(question_id)
    if not question_is_valid(new_question):
        raise ValueError("La question ne peut pas être vide ou contenir uniquement des espaces.")
    return db['template_questions'].update_one({"_id":id}, {"$set":{"question":new_question}})





### methode de vérification 


def question_is_valid(question ):
    if not question or question.strip() == "":
        return False
    return True


### conversion de id en ObjectId pour mongo 

def conversion(id):
    try:
        return ObjectId(id)
    except Exception as e:
        raise ValueError(f"L'ID fourni n'est pas valide : {str(e)}")
    