# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'core/home.html')

def logout_view(request):
    logout(request)        # clears the session
    return redirect("home")

# Mentor list view
def mentor_list(request):
    mentors = Profile.objects.filter(role="MENTOR")
    return render(request, "core/mentor_list.html", {"mentors": mentors})

# Role selection view
def select_role(request):
    # If already logged in, go to the dashboard instead of signup choices
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "core/select_role.html")


# Role selection view that forces role choice
def signup(request):
    # Read role from query string (?role=MENTOR or ?role=MENTEE)
    role = request.GET.get("role")

    # If role is missing or invalid, send them back to choose
    if role not in ["MENTOR", "MENTEE"]:
        return redirect("select_role")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # creates the User
            profile = user.profile  # Profile is created automatically by the signal
            profile.role = role     # set to MENTOR or MENTEE
            profile.save()

            login(request, user)    # log them in
            return redirect("dashboard") # or 'mentor_list' / dashboard later
    else:
        form = UserCreationForm()

    return render(request, "core/signup.html", {"form": form, "role": role})

@login_required
def dashboard(request):
    profile = request.user.profile

    # For now, both roles just see the mentor list.
    # Later you can customize: mentor_dashboard vs mentee_dashboard.
    if profile.role == "MENTOR":
        return redirect("mentor_list")
    elif profile.role == "MENTEE":
        return redirect("mentor_list")
    else:
        return redirect("home")