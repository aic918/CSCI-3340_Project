# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Session, Review, Availability, Message, Connection, Post, PostLike, PostComment, Follow
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from .forms import SessionRequestForm, ProfileForm, ReviewForm, AvailabilityForm, MessageForm, RescheduleForm, CommentForm
from django import forms
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_availability(request, availability_id):
    """
    Delete a single availability entry for the logged-in mentor.
    """
    profile = request.user.profile

    # Only allow deleting your own availability
    availability = get_object_or_404(
        Availability,
        id=availability_id,
        mentor=profile,
    )

    availability.delete()
    return redirect("edit_availability")


def _connection_between(p1, p2):
    """
    Return existing Connection object (any direction), or None.
    """
    return Connection.objects.filter(
        Q(from_profile=p1, to_profile=p2) |
        Q(from_profile=p2, to_profile=p1)
    ).first()


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
            Q(skills__icontains=query) |
            Q(public_id__iexact=query)
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

    # Reviews + average rating
    reviews = Review.objects.filter(session__mentor=mentor)
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    # Availability for this mentor
    availabilities = (
        Availability.objects
        .filter(mentor=mentor)
        .order_by("day_of_week", "start_time")
    )

    # Is current user (if mentee) following this mentor?
    is_following = False
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        me = request.user.profile
        if me.role == "MENTEE":
            is_following = Follow.objects.filter(
                follower=me,
                mentor=mentor,
            ).exists()

    return render(
        request,
        "core/mentor_detail.html",
        {
            "mentor": mentor,
            "avg_rating": avg_rating,
            "reviews": reviews,
            "availabilities": availabilities,
            "is_following": is_following,
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

    profile, created = Profile.objects.get_or_create(
        user=user,
        defaults={"role": "MENTEE"}
    )

    if created or profile.role not in ["MENTOR", "MENTEE"]:
        return redirect("select_role")

    if profile.role == "MENTOR":
        sessions = Session.objects.filter(mentor=profile)
        total_sessions = sessions.count()
        completed = sessions.filter(status="COMPLETED").count()
        pending = sessions.filter(status="PENDING").count()
        avg_rating = Review.objects.filter(session__mentor=profile).aggregate(Avg("rating"))["rating__avg"]

        context = {
            "profile": profile,
            "is_mentor": True,
            "total_sessions": total_sessions,
            "completed": completed,
            "pending": pending,
            "avg_rating": avg_rating,
        }
    else:
        sessions = Session.objects.filter(mentee=profile)
        total_sessions = sessions.count()
        completed = sessions.filter(status="COMPLETED").count()
        pending = sessions.filter(status="PENDING").count()

        context = {
            "profile": profile,
            "is_mentor": False,
            "total_sessions": total_sessions,
            "completed": completed,
            "pending": pending,
        }

    return render(request, "core/dashboard.html", context)


@login_required
def my_sessions(request):
    profile = request.user.profile

    if profile.role == "MENTOR":
        # Mentors can see all sessions (including cancelled) for history
        sessions = Session.objects.filter(mentor=profile).order_by("scheduled_at")
        role_label = "Sessions where you are the mentor"
    else:  # MENTEE
        # Mentees only see non-cancelled sessions
        sessions = (
            Session.objects
            .filter(mentee=profile)
            .exclude(status="CANCELLED")
            .order_by("scheduled_at")
        )
        role_label = "Sessions you requested"

    context = {
        "sessions": sessions,
        "role_label": role_label,
    }
    return render(request, "core/my_sessions.html", context)

@login_required
def profile_view(request):
    """
    Show a LinkedIn/Instagram-style profile page for the currently logged-in user.
    """
    profile = request.user.profile
    is_mentor = (profile.role == "MENTOR")

    # Stats
    if is_mentor:
        sessions_as_mentor = Session.objects.filter(mentor=profile)
        total_sessions = sessions_as_mentor.count()
        completed = sessions_as_mentor.filter(status="COMPLETED").count()
        pending = sessions_as_mentor.filter(status="PENDING").count()
        avg_rating = (
            Review.objects
            .filter(session__mentor=profile)
            .aggregate(Avg("rating"))["rating__avg"]
        )
        # mentors don't follow anyone for now
        followed_mentors = []
        follow_count = 0
    else:
        sessions_as_mentee = Session.objects.filter(mentee=profile)
        total_sessions = sessions_as_mentee.count()
        completed = sessions_as_mentee.filter(status="COMPLETED").count()
        pending = sessions_as_mentee.filter(status="PENDING").count()
        avg_rating = None

        # mentee: who am I following?
        followed_mentors = (
            Follow.objects
            .filter(follower=profile)
            .select_related("mentor__user")
            .order_by("mentor__user__username")
        )
        follow_count = followed_mentors.count()

    # Availability – only mentors publish availability
    if is_mentor:
        availabilities = (
            Availability.objects
            .filter(mentor=profile)
            .order_by("day_of_week", "start_time")
        )
    else:
        availabilities = []

    # Posts – only mentors will actually have any, but showing for consistency
    posts = Post.objects.filter(author=profile).order_by("-created_at")

    context = {
        "profile_obj": profile,
        "is_mentor": is_mentor,
        "total_sessions": total_sessions,
        "completed": completed,
        "pending": pending,
        "avg_rating": avg_rating,
        "availabilities": availabilities,
        "posts": posts,

        # NEW for mentee “following” UI
        "followed_mentors": followed_mentors,
        "follow_count": follow_count,
    }
    return render(request, "core/profile.html", context)

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "MENTEE"}  # default if they somehow had none
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            # 🔒 Mentees can never have an hourly rate
            if profile.role != "MENTOR":
                profile.hourly_rate = None

            profile.save()
            return redirect("profile")  # after editing, go back to profile page
    else:
        form = ProfileForm(instance=profile)

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

@login_required
def edit_availability(request):
    profile = request.user.profile
    if profile.role != "MENTOR":
        return redirect("dashboard")

    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data["day_of_week"]   # this is a list, e.g. ["MONDAY", "WEDNESDAY"]
            start = form.cleaned_data["start_time"]
            end = form.cleaned_data["end_time"]

            # Create one Availability row per selected day
            for day in days:
                Availability.objects.create(
                    mentor=profile,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                )

            return redirect("edit_availability")
    else:
        form = AvailabilityForm()

    # Existing availabilities (unchanged)
    availabilities = profile.availabilities.all().order_by("day_of_week", "start_time")

    return render(
        request,
        "core/edit_availability.html",
        {
            "form": form,
            "availabilities": availabilities,
        },
    )


@login_required
def inbox(request):
    profile = request.user.profile

    # All messages involving this profile
    msgs = Message.objects.filter(
        Q(sender=profile) | Q(recipient=profile)
    ).select_related("sender", "recipient").order_by("-sent_at")

    # Very simple: just show a flat list for now
    return render(request, "core/inbox.html", {"messages": msgs})


@login_required
def conversation(request, profile_id):
    profile = request.user.profile
    other = get_object_or_404(Profile, id=profile_id)

    messages = Message.objects.filter(
        Q(sender=profile, recipient=other) |
        Q(sender=other, recipient=profile)
    ).order_by("sent_at")

    # Mark messages from 'other' as read
    Message.objects.filter(sender=other, recipient=profile, is_read=False).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = profile
            msg.recipient = other
            msg.save()
            return redirect("conversation", profile_id=other.id)
    else:
        form = MessageForm()

    return render(
        request,
        "core/conversation.html",
        {"other": other, "messages": messages, "form": form},
    )

@login_required
def cancel_session(request, session_id):
    """Mentee cancels their own session (pending or confirmed)."""
    session = get_object_or_404(Session, id=session_id)
    profile = request.user.profile

    # Only the mentee can cancel, and only if it's still upcoming
    if profile != session.mentee or session.status not in ["PENDING", "CONFIRMED"]:
        return redirect("my_sessions")

    if request.method == "POST":
        session.status = "CANCELLED"
        session.save()

    return redirect("my_sessions")


@login_required
def reschedule_session(request, session_id):
    """Mentor reschedules a session."""
    session = get_object_or_404(Session, id=session_id)
    profile = request.user.profile

    # Only the mentor for this session can reschedule
    if profile != session.mentor:
        return redirect("my_sessions")

    if request.method == "POST":
        form = RescheduleForm(request.POST, instance=session)
        if form.is_valid():
            updated = form.save(commit=False)
            # When rescheduled, you can keep it CONFIRMED or move back to PENDING.
            # Here we'll keep the current status:
            # updated.status = "PENDING"
            updated.save()
            return redirect("my_sessions")
    else:
        form = RescheduleForm(instance=session)

    return render(
        request,
        "core/reschedule_session.html",
        {"form": form, "session": session},
    )

@login_required
def feed(request):
    """
    Show a feed of mentor posts.
    - Mentees: only posts from mentors they follow.
    - Mentors: all posts.
    """
    profile = request.user.profile

    if profile.role == "MENTEE":
        followed_ids = Follow.objects.filter(
            follower=profile
        ).values_list("mentor_id", flat=True)

        posts = Post.objects.filter(author_id__in=followed_ids)
    else:
        # mentors (or any other role) see all posts
        posts = Post.objects.all()

    posts = (
        posts
        .select_related("author", "author__user")
        .prefetch_related(
            "likes",
            "comments",
            "comments__author",
            "comments__author__user",
        )
        .order_by("-created_at")
    )

    liked_post_ids = set(
        PostLike.objects
        .filter(user=profile, post__in=posts)
        .values_list("post_id", flat=True)
    )

    comment_form = CommentForm()

    return render(
        request,
        "core/feed.html",
        {
            "posts": posts,
            "liked_post_ids": liked_post_ids,
            "comment_form": comment_form,
        },
    )


# core/views.py (near the bottom)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Share an update, tip, or opportunity..."
                }
            ),
        }



@login_required
def create_post(request):
    profile = request.user.profile

    # Only mentors can create posts
    if profile.role != "MENTOR":
        return redirect("feed")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = profile
            post.save()
            return redirect("feed")
    else:
        form = PostForm()

    return render(request, "core/create_post.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Only the author can edit
    if request.user.profile != post.author:
        return redirect("feed")

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("feed")
    else:
        form = PostForm(instance=post)

    return render(request, "core/edit_post.html", {"form": form, "post": post})


@login_required
def send_connection_request(request, mentor_id):
    """
    Mentee clicks 'Connect' on a mentor's profile.
    Creates a Connection in PENDING status if it doesn't exist yet.
    """
    mentee_profile = request.user.profile
    mentor_profile = get_object_or_404(Profile, id=mentor_id, role="MENTOR")

    # Only mentees can send connection requests
    if mentee_profile.role != "MENTEE":
        return redirect("mentor_detail", mentor_id=mentor_id)

    # Don't allow connecting to yourself
    if mentee_profile == mentor_profile:
        return redirect("mentor_detail", mentor_id=mentor_id)

    existing = _connection_between(mentee_profile, mentor_profile)
    if not existing:
        Connection.objects.create(
            from_profile=mentee_profile,
            to_profile=mentor_profile,
            status="PENDING",
        )

    # If there was already a connection, we just go back to mentor detail
    return redirect("mentor_detail", mentor_id=mentor_id)


@login_required
def respond_connection_request(request, connection_id, action):
    """
    Mentor clicks Accept / Decline on an incoming connection request.
    action is 'accept' or 'decline'.
    """
    connection = get_object_or_404(Connection, id=connection_id)

    # Only the 'to_profile' (mentor) can respond
    if request.user.profile != connection.to_profile:
        return redirect("dashboard")

    if request.method == "POST":
        if action == "accept":
            connection.status = "ACCEPTED"
        elif action == "decline":
            connection.status = "DECLINED"
        connection.save()

    return redirect("dashboard")

@login_required
@require_POST
def toggle_like(request, post_id):
    """
    Toggle like/unlike on a post for the current user.
    """
    profile = request.user.profile
    post = get_object_or_404(Post, id=post_id)

    like, created = PostLike.objects.get_or_create(post=post, user=profile)
    if not created:
        # Already liked -> unlike
        like.delete()

    # Go back to where user came from (feed/profile)
    return redirect(request.META.get("HTTP_REFERER", "feed"))


@login_required
@require_POST
def add_comment(request, post_id):
    """
    Add a comment to a post.
    """
    profile = request.user.profile
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = profile
        comment.save()

    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
def follow_mentor(request, mentor_id):
    """
    Mentee follows a mentor (one-way follow).
    """
    profile = request.user.profile
    mentor = get_object_or_404(Profile, id=mentor_id, role="MENTOR")

    # Only mentees can follow mentors, and you can't follow yourself
    if profile.role != "MENTEE" or profile == mentor:
        return redirect("mentor_detail", mentor_id=mentor.id)

    if request.method == "POST":
        Follow.objects.get_or_create(follower=profile, mentor=mentor)

    return redirect("mentor_detail", mentor_id=mentor.id)

@login_required
def unfollow_mentor(request, mentor_id):
    """
    Mentee unfollows a mentor.
    """
    profile = request.user.profile
    mentor = get_object_or_404(Profile, id=mentor_id, role="MENTOR")

    if profile.role != "MENTEE" or profile == mentor:
        return redirect("mentor_detail", mentor_id=mentor.id)

    if request.method == "POST":
        Follow.objects.filter(follower=profile, mentor=mentor).delete()

    return redirect("mentor_detail", mentor_id=mentor.id)

@login_required
def toggle_follow(request, mentor_id):
    """
    Mentee follows / unfollows a mentor.
    """
    profile = request.user.profile
    mentor = get_object_or_404(Profile, id=mentor_id, role="MENTOR")

    # Only mentees can follow mentors
    if profile.role != "MENTEE":
        return redirect("mentor_detail", mentor_id=mentor.id)

    if request.method == "POST":
        qs = Follow.objects.filter(follower=profile, mentor=mentor)

        if qs.exists():
            # Already following -> unfollow (delete ALL rows just in case)
            qs.delete()
        else:
            # Not following -> follow
            Follow.objects.create(follower=profile, mentor=mentor)

    return redirect("mentor_detail", mentor_id=mentor.id)


@login_required
def my_follows(request):
    """
    Show the list of mentors that the current mentee is following.
    """
    profile = request.user.profile

    # Only mentees should have a "following" list
    if profile.role != "MENTEE":
        return redirect("dashboard")

    follows = (
        Follow.objects
        .filter(follower=profile)
        .select_related("mentor", "mentor__user")
        .order_by("-created_at")
    )

    # You can either pass the Follow objects OR just a list of mentors
    mentors = [f.mentor for f in follows]

    return render(
        request,
        "core/my_follows.html",
        {
            "follows": follows,
            "mentors": mentors,
        },
    )

@login_required
def profile_public(request, profile_id):
    """
    View another user's profile (from posts, comments, etc.).
    Uses the same layout as your own profile, but hides 'Edit profile'
    and the following list when it's not you.
    """
    profile_obj = get_object_or_404(Profile, id=profile_id)
    is_mentor = (profile_obj.role == "MENTOR")

    # Stats
    if is_mentor:
        sessions_as_mentor = Session.objects.filter(mentor=profile_obj)
        total_sessions = sessions_as_mentor.count()
        completed = sessions_as_mentor.filter(status="COMPLETED").count()
        pending = sessions_as_mentor.filter(status="PENDING").count()
        avg_rating = (
            Review.objects
            .filter(session__mentor=profile_obj)
            .aggregate(Avg("rating"))["rating__avg"]
        )
    else:
        sessions_as_mentee = Session.objects.filter(mentee=profile_obj)
        total_sessions = sessions_as_mentee.count()
        completed = sessions_as_mentee.filter(status="COMPLETED").count()
        pending = sessions_as_mentee.filter(status="PENDING").count()
        avg_rating = None

    # Availability – only mentors publish availability
    if is_mentor:
        availabilities = (
            Availability.objects
            .filter(mentor=profile_obj)
            .order_by("day_of_week", "start_time")
        )
    else:
        availabilities = []

    # Posts by that user
    posts = Post.objects.filter(author=profile_obj).order_by("-created_at")

    # Following list is only meaningful when you are viewing your own mentee profile
    if (not is_mentor) and (request.user.profile == profile_obj):
        followed_mentors = (
            Follow.objects
            .filter(follower=profile_obj)
            .select_related("mentor__user")
            .order_by("mentor__user__username")
        )
        follow_count = followed_mentors.count()
    else:
        followed_mentors = []
        follow_count = 0

    context = {
        "profile_obj": profile_obj,
        "is_mentor": is_mentor,
        "total_sessions": total_sessions,
        "completed": completed,
        "pending": pending,
        "avg_rating": avg_rating,
        "availabilities": availabilities,
        "posts": posts,
        "followed_mentors": followed_mentors,
        "follow_count": follow_count,
    }
    return render(request, "core/profile.html", context)
