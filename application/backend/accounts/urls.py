from django.urls import path
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import RegisterView, CurrentUserView

from .views import RegisterView


urlpatterns = [
    # User registration
    path('register/', RegisterView.as_view(), name='register'),

    # JWT authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(
        'token/blacklist/',
        TokenBlacklistView.as_view(permission_classes=[IsAuthenticated]),
        name='token_blacklist',
    ),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]