from pymongo import MongoClient

# Configuration MongoDB
client = MongoClient("mongodb+srv://steveneklou:gSEr1Q9abQ8MP1uF@db.4oyag.mongodb.net/?retryWrites=true&w=majority&appName=db",
                     tls=True,
                     tlsAllowInvalidCertificates=True
                     )
db = client["pfe"]
