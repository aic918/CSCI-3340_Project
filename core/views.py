# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Session, Review
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .forms import SessionRequestForm, ProfileForm, ReviewForm



def home(request):
    return render(request, 'core/home.html')

def logout_view(request):
    logout(request)        # clears the session
    return redirect("home")

# Mentor list view
# Mentor list view
def mentor_list(request):
    query = request.GET.get("q", "").strip()

    mentors = Profile.objects.filter(role="MENTOR")

    if query:
        mentors = mentors.filter(
            Q(user__username__icontains=query) |
            Q(bio__icontains=query) |
            Q(skills__icontains=query)
        )

    # NEW: annotate average rating for each mentor
    mentors = mentors.annotate(
        avg_rating=Avg("sessions_as_mentor__review__rating")
    )

    context = {
        "mentors": mentors,
        "query": query,
    }
    return render(request, "core/mentor_list.html", context)


@login_required
def mentor_detail(request, mentor_id):
    mentor = get_object_or_404(Profile, id=mentor_id, role="MENTOR")
    reviews = Review.objects.filter(session__mentor=mentor)
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(
        request,
        "core/mentor_detail.html",
        {
            "mentor": mentor,
            "avg_rating": avg_rating,
            "reviews": reviews,
        },
    )    

@login_required
def request_session(request, mentor_id):
    mentor = get_object_or_404(Profile, id=mentor_id, role="MENTOR")

    # Only mentees can request sessions
    if request.user.profile.role != "MENTEE":
        return redirect("mentor_detail", mentor_id=mentor.id)

    if request.method == "POST":
        form = SessionRequestForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.mentor = mentor
            session.mentee = request.user.profile
            session.status = "PENDING"
            session.save()
            # Later we can redirect to "my sessions" page
            return redirect("mentor_detail", mentor_id=mentor.id)
    else:
        form = SessionRequestForm()

    context = {
        "mentor": mentor,
        "form": form,
    }
    return render(request, "core/request_session.html", context)


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
    user = request.user

    # Make sure the user always has a Profile
    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={"role": "MENTEE"}  # default role if they had none
    )

    # If profile was just created, or role is weird, send them to role selection
    if created or profile.role not in ["MENTOR", "MENTEE"]:
        return redirect("select_role")

    # For now both roles just go to mentor list,
    # but you can later split into different dashboards
    return redirect("mentor_list")

@login_required
def my_sessions(request):
    profile = request.user.profile

    if profile.role == "MENTOR":
        sessions = Session.objects.filter(mentor=profile).order_by("scheduled_at")
        role_label = "Sessions where you are the mentor"
    else:  # MENTEE (or anything else)
        sessions = Session.objects.filter(mentee=profile).order_by("scheduled_at")
        role_label = "Sessions you requested"

    context = {
        "sessions": sessions,
        "role_label": role_label,
    }
    return render(request, "core/my_sessions.html", context)

@login_required
def edit_profile(request):
    # Make sure the user has a Profile
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "MENTEE"}  # default if they somehow had none
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("my_sessions")  # or 'mentor_list' / 'dashboard' if you prefer
    else:
        form = ProfileForm(instance=profile)

    # We can show slightly different text depending on role
    is_mentor = profile.role == "MENTOR"

    return render(
        request,
        "core/edit_profile.html",
        {"form": form, "is_mentor": is_mentor},
    )


@login_required
def update_session_status(request, session_id, new_status):
    session = get_object_or_404(Session, id=session_id)

    # Only the mentor for this session can update the status
    if request.user.profile != session.mentor:
        return redirect("my_sessions")

    # Only allow certain status changes
    allowed_statuses = ["CONFIRMED", "CANCELLED", "COMPLETED"]
    if new_status not in allowed_statuses:
        return redirect("my_sessions")

    if request.method == "POST":
        session.status = new_status
        session.save()

    return redirect("my_sessions")

@login_required
def leave_review(request, session_id):
    # 1) Get the session or 404
    session = get_object_or_404(Session, id=session_id)

    # 2) Only the mentee can review this session
    if request.user.profile != session.mentee:
        return redirect("dashboard")

    # 3) Only allow reviews for COMPLETED sessions
    if session.status != "COMPLETED":
        return redirect("dashboard")

    # 4) One review per session (Review has OneToOneField to Session)
    if hasattr(session, "review"):
        return redirect("dashboard")

    # 5) Handle form
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.session = session
            review.save()
            return redirect("my_sessions")
    else:
        form = ReviewForm()

    return render(
        request,
        "core/leave_review.html",
        {"session": session, "form": form},
    )
