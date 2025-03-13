from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

from orders.models import Order
from .models import UserProfile, UserOTP
from .forms import UserRegistrationForm
from .forms import UserProfileUpdateForm, CustomAuthenticationForm
from .utils import generate_qr_code

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter  # Google OAuth for social media login


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        user = form.save(commit=False)  # Create a user object without saving to the database
        user.set_password(form.cleaned_data["password"])  # Set an encrypted password
        user.save()
        messages.success(self.request, "Registration was successful!")
        login(self.request, user)  # Automatic login after registration
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        # Get/create a user profile
        context = super().get_context_data(**kwargs)  
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)

        # Get a list of user orders sorted by date
        orders = (Order.objects.filter(user=self.request.user).order_by("-created_at") or None)

        # Taking over or creating an OTP-appliance
        otp_device, _ = UserOTP.objects.get_or_create(user=self.request.user)

        # Generate a QR code for two-factor authentication
        qr_code = generate_qr_code(otp_device.config_url) if otp_device else None
        context.update(
            {
                "form": UserProfileUpdateForm(instance=profile, user=self.request.user),
                "qr_code": qr_code,
                "orders": orders,
            }
        )
        return context


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    next_page = reverse_lazy("home")

    def get_success_url(self):
        if self.request.user.is_superuser:
            return resolve_url("/admin/")  # Redirecting a superuser to the admin panel
        if "next" in self.request.GET:
            return self.request.GET["next"]
        return super().get_success_url()


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("home")


class CustomPasswordChangeView(PasswordChangeView):
    template_name = "users/password_change.html"
    success_url = reverse_lazy(
        "profile"
    )


@login_required
def update_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserProfileUpdateForm(
            request.POST, request.FILES, instance=profile, user=request.user
        )

        if form.is_valid():
            profile = form.save(commit=False)
            user = request.user
            user.username = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()

            profile.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("users:profile")

    else:
        form = UserProfileUpdateForm(instance=profile, user=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def update_avatar(request):
    if request.method == "POST" and request.FILES.get("avatar"):
        profile = get_object_or_404(UserProfile, user=request.user)
        profile.avatar = request.FILES["avatar"]
        profile.save()
        return JsonResponse({"success": True, "avatar_url": profile.avatar.url})
    return JsonResponse({"success": False, "error": "Invalid request"})
