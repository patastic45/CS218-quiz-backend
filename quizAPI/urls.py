from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView


# viewset urls
router = DefaultRouter()
router.register(r'quiz-collections', views.QuizCollectionViewSet, basename='quiz_collections')
router.register(r'multiple-choice-questions', views.QuizMultipleChoiceViewSet, basename='multiple-choice')
router.register(r'true-false-questions', views.QuizTrueFalseViewSet, basename='true-false')
router.register(r'user', views.UserList, basename='user')
router.register(r'quiz-collection-answers', views.QuizCollectionAnswerViewSet, basename='quiz_collection_answers')


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('', include(router.urls)),
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login (returns access & refresh tokens)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Get new access token using refresh token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Verify if a token is valid
    path('api/logout/', views.LogoutView.as_view(), name='logout'),  # Custom logout view


]