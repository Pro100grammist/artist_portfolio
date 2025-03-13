from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    ProfileView,
    CustomPasswordChangeView,
    RegisterView,
    update_profile,
    update_avatar,
)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path(
        "password_change/", CustomPasswordChangeView.as_view(), name="password_change"
    ),
    path("profile/update/", update_profile, name="update_profile"),
    path("profile/update-avatar/", update_avatar, name="update_avatar"),
]
