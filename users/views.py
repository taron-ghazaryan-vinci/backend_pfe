from rest_framework.views import APIView
from rest_framework.response import Response
from .db import create_user, find_user_by_email, check_password, set_user_template_true

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class RegisterView(APIView):
    def post(self, request):
        data = request.data

        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if field not in data:
                return Response(
                    {"error": f"Le champ '{field}' est obligatoire."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Vérificationde l'email
        if find_user_by_email(data['email']):
            return Response(
                {"error": "Email déjà utilisé"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Création de l'utilisateur
        try:
            create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role=data['role']
            )
            return Response(
                {"message": "Utilisateur créé avec succès"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Gestion des erreurs imprévues
            return Response(
                {"error": "Une erreur est survenue lors de la création de l'utilisateur.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            "userId": user.get('id'),
            "username": user.get('username'),
            "email": user.get('email'),
            "role": user.get('role'),
            "template" : user.get('template')
        }

        return Response({"message": "Connexion réussie", "user": user_data}, status=200)

class SetTemplateTrueView(APIView):
    def patch(self, request, custom_id):
        """
        Mettre le champ 'template' d'un utilisateur à True par ID personnalisé.
        """
        updated = set_user_template_true(custom_id)

        if updated:
            return Response({"message": "Template mis à jour à True avec succès"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Utilisateur non trouvé ou aucune mise à jour effectuée"}, status=status.HTTP_404_NOT_FOUND)
