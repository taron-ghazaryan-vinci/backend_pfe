from .db import (create_user, find_user_by_email, check_password, set_user_template_true,
                 get_user_responses_by_email, get_all_users, get_user_by_id,
                 update_user_responses, set_boolean_esg_true, remove_id_from_responses_chosen,
                 set_rapport_true, update_etat_rapport, update_etat_esg, remove_id_from_engagements_chosen,
                 add_id_to_responses_chosen, add_id_to_engagements_chosen)

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
            "template" : user.get('template'),
            "templates" : user.get('templates'),
            "responses" : user.get('responses'),
            "boolean_esg" : user.get('boolean_esg'),
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

class SetRapportTrueView(APIView):
    def patch(self, request, user_id):
        """
        Endpoint pour mettre à jour le champ 'rapport' à True.
        """
        try:
            success = set_rapport_true(user_id)
            if not success:
                return Response(
                    {"error": "Utilisateur non trouvé ou mise à jour échouée."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"message": "Champ 'rapport' mis à jour avec succès."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateEtatRapportView(APIView):
    def patch(self, request, user_id):
        """
        Endpoint pour mettre à jour le champ 'etat_rapport' d'un utilisateur.
        """
        try:
            new_etat_rapport = request.data.get("etat_rapport")
            if not new_etat_rapport:
                return Response(
                    {"error": "Le champ 'etat_rapport' est requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = update_etat_rapport(user_id, new_etat_rapport)
            if not success:
                return Response(
                    {"error": "Utilisateur non trouvé ou mise à jour échouée."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Champ 'etat_rapport' mis à jour avec succès."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UpdateEtatESGView(APIView):
    def patch(self, request, user_id):
        """
        Endpoint pour mettre à jour le champ 'etat_esg' d'un utilisateur.
        """
        try:
            new_etat_esg = request.data.get("etat_esg")
            if not new_etat_esg:
                return Response(
                    {"error": "Le champ 'etat_esg' est requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            success = update_etat_esg(user_id, new_etat_esg)
            if not success:
                return Response(
                    {"error": "Utilisateur non trouvé ou mise à jour échouée."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Champ 'etat_esg' mis à jour avec succès."},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class SetBooleanESGView(APIView):
    def patch(self, request, user_id):
        """
        Endpoint pour mettre à jour le champ 'boolean_esg' d'un utilisateur à True.
        """
        try:
            success = set_boolean_esg_true(user_id)
            if not success:
                return Response(
                    {"error": "Utilisateur non trouvé ou mise à jour échouée"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"message": "Champ 'boolean_esg' mis à jour avec succès"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetAllUsersView(APIView):
    def get(self, request):
        """
        Endpoint pour récupérer tous les utilisateurs.
        """
        try:
            users = get_all_users()
            return Response(
                {"users": users},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetUserByIdView(APIView):
    def get(self, request, user_id):
        """
        Endpoint pour récupérer un utilisateur par son ID.
        """
        try:
            user = get_user_by_id(user_id)
            if not user:
                return Response(
                    {"error": "Utilisateur non trouvé"},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"user": user},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetUserResponsesView(APIView):
    def get(self, request, email):
        """
        Endpoint pour récupérer les réponses détaillées d'un utilisateur à partir de son email.
        """
        try:
            responses = get_user_responses_by_email(email)

            if not responses:
                return Response(
                    {"message": "Aucune réponse trouvée pour cet utilisateur."},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({"responses": responses}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class UpdateUserResponsesView(APIView):
    def patch(self, request):
        """
        Endpoint pour mettre à jour les réponses d'un utilisateur.
        """
        data = request.data

        # Récupérer les données nécessaires
        email = data.get("email")
        question_id = data.get("question_id")
        responses_chosen = data.get("responses_chosen", [])
        engagements_chosen = data.get("engagements_chosen", [])

        if not email or not question_id:
            return Response(
                {"error": "Email et question_id sont requis"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Appeler la méthode pour mettre à jour les réponses
        result = update_user_responses(email, question_id, responses_chosen, engagements_chosen)

        if "error" in result:
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)


class RemoveUserResponseIdView(APIView):
    def patch(self, request):
        """
        Endpoint pour supprimer un ID de responsesChosen pour une question spécifique et mettre à jour le scoreESG.
        """
        try:
            data = request.data
            user_id = data.get("user_id")
            question_id = data.get("question_id")
            response_id_to_remove = data.get("response_id")

            if not user_id or not question_id or not response_id_to_remove:
                return Response(
                    {"error": "Les champs user_id, question_id et response_id sont requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = remove_id_from_responses_chosen(user_id, question_id, response_id_to_remove)

            if result["status"] == "error":
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RemoveUserEngagementIdView(APIView):
    def patch(self, request):
        """
        Endpoint pour supprimer un ID de engagementsChosen d'un utilisateur.
        """
        try:
            data = request.data
            user_id = data.get("user_id")
            question_id = data.get("question_id")
            engagement_id_to_remove = data.get("engagement_id")

            if not user_id or not question_id or not engagement_id_to_remove:
                return Response(
                    {"error": "Les champs user_id, question_id et engagement_id sont requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = remove_id_from_engagements_chosen(user_id, question_id, engagement_id_to_remove)

            if result["status"] == "error":
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddUserResponseIdView(APIView):
    def patch(self, request):
        """
        Endpoint pour ajouter un ID à responsesChosen d'un utilisateur.
        """
        try:
            data = request.data
            user_id = data.get("user_id")
            question_id = data.get("question_id")
            response_id_to_add = data.get("response_id")

            if not user_id or not question_id or not response_id_to_add:
                return Response(
                    {"error": "Les champs user_id, question_id et response_id sont requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = add_id_to_responses_chosen(user_id, question_id, response_id_to_add)

            if result["status"] == "error":
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddUserEngagementIdView(APIView):
    def patch(self, request):
        """
        Endpoint pour ajouter un ID à engagementsChosen d'un utilisateur.
        """
        try:
            data = request.data
            user_id = data.get("user_id")
            question_id = data.get("question_id")
            engagement_id_to_add = data.get("engagement_id")

            if not user_id or not question_id or not engagement_id_to_add:
                return Response(
                    {"error": "Les champs user_id, question_id et engagement_id sont requis."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            result = add_id_to_engagements_chosen(user_id, question_id, engagement_id_to_add)

            if result["status"] == "error":
                return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": result["message"]}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Une erreur est survenue : {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
