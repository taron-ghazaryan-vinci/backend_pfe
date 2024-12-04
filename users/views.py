from rest_framework.views import APIView
from rest_framework.response import Response
from .db import create_user, find_user_by_email, check_password

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        if find_user_by_email(data['email']):
            return Response({"error": "Email déjà utilisé"}, status=400)
        create_user(data['username'], data['email'], data['password'])
        return Response({"message": "Utilisateur créé"}, status=201)


class LoginView(APIView):
    def post(self, request):
        data = request.data
        user = find_user_by_email(data['email'])
        if not user:
            return Response({"error": "Utilisateur non trouvé"}, status=404)

        if not check_password(user['password'], data['password']):
            return Response({"error": "Mot de passe incorrect"}, status=401)

        # Préparer les données utilisateur à retourner (exclure le mot de passe)
        user_data = {
            "username": user.get('username'),
            "email": user.get('email'),
            "role": user.get('role')  # Par défaut, rôle "user" si non spécifié
        }

        return Response({"message": "Connexion réussie", "user": user_data}, status=200)
