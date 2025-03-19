from django.shortcuts import render

from rest_framework import generics, permissions, viewsets

from .models import QuizCollection, QuizMulipleChoice, QuizTrueFalse, QuizCollectionAnswer
from .serializers import QuizCollectionSerializer, QuizMultipleChoiceSerializer, QuizTrueFalseSerializer, UserSerializer, QuizCollectionAnswerSerializer
from .permissions import IsOwnerOrReadOnly, IsOwnerOrSharedReadOnly, IsOwner
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework_simplejwt.tokens import RefreshToken



from django.contrib.auth.models import User

# views to see user and it's details
# UserList and UserDetail will be deleted, these are just artifacts from the previous version
# of the project
class UserList(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    http_method_names = ['get']
    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)
    
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = UserSerializer

# API endpoint to authenticate user
# Is ideally the main entry point to the application
# or if the user already has an account, they can login or use a token
# to access other endpoints
class RegisterUserView(generics.CreateAPIView):
    """API endpoint to register a new user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return Response({"error": "You are already registered and authenticated."}, status=400)

        response = super().create(request, *args, **kwargs)
        return Response({"user": response.data}, status=201)

# Views for creation and get of multiple choice questions
class QuizMultipleChoiceViewSet(viewsets.ModelViewSet):
    """ ViewSet for handling multiple-choice questions """
    serializer_class = QuizMultipleChoiceSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """ Only return questions owned by the logged-in user """
        return QuizMulipleChoice.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """ Automatically assign owner and optionally add to a collection """
        collection_id = self.request.data.get('collection_id')
        question = serializer.save(owner=self.request.user)

        if collection_id:
            try:
                collection = QuizCollection.objects.get(id=collection_id, owner=self.request.user)
                collection.multiQuestions.add(question)
            except QuizCollection.DoesNotExist:
                pass  # Could raise a ValidationError instead

# Views for creation and get of true false questions
class QuizTrueFalseViewSet(viewsets.ModelViewSet):
    """ ViewSet for handling true/false questions """
    serializer_class = QuizTrueFalseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """ Only return questions owned by the logged-in user """
        return QuizTrueFalse.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        """ Automatically assign owner and optionally add to a collection """
        collection_id = self.request.data.get('collection_id')
        question = serializer.save(owner=self.request.user)

        if collection_id:
            try:
                collection = QuizCollection.objects.get(id=collection_id, owner=self.request.user)
                collection.trueFalseQuestions.add(question)
            except QuizCollection.DoesNotExist:
                pass  # Could raise a ValidationError instead

# Views for creation and get of collection, which house questions
class QuizCollectionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizCollectionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSharedReadOnly]

    def get_queryset(self):
        queryset = QuizCollection.objects.prefetch_related("trueFalseQuestions", "multiQuestions", "shared_with", "answered")

        filter_type = self.request.query_params.get("filter", "owned")

        if filter_type == "shared":
            return queryset.filter(shared_with=self.request.user).exclude(answered=self.request.user)
        return queryset.filter(owner=self.request.user)
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class QuizCollectionAnswerViewSet(viewsets.ModelViewSet):
    serializer_class = QuizCollectionAnswerSerializer
    #authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSharedReadOnly]

    def get_queryset(self):
        return QuizCollectionAnswer.objects.filter(
            Q(owner=self.request.user) | Q(shared_with=self.request.user)
        )
    def perform_create(self, serializer):
        collection = serializer.validated_data['collectionID']

        # Ensure only users in `shared_with` can create an answer
        if self.request.user not in collection.shared_with.all():
            raise PermissionDenied("You do not have permission to take this quiz.")

        # Assign the owner as the quiz collection owner
        answer = serializer.save(owner=collection.owner)

        # Automatically add the current user to `shared_with` so they can access their answer later
        answer.shared_with.add(self.request.user)



class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"message": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)