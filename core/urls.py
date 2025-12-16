from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # or whatever your main view is
    path("select-role/", views.select_role, name="select_role"),  # choose Mentor/Mentee
    path("signup/", views.signup, name="signup"),   # signup form
    path("mentors/", views.mentor_list, name="mentor_list"),  # mentor list
    path("logout/", views.logout_view, name="logout_custom"),  # logut view
    path("dashboard/", views.dashboard, name="dashboard"),  # user dashboard
    path("mentors/<int:mentor_id>/", views.mentor_detail, name="mentor_detail"),
    path(
        "mentors/<int:mentor_id>/request-session/",
        views.request_session,
        name="request_session",
    ),
    path("my-sessions/", views.my_sessions, name="my_sessions"),
    path(
        "sessions/<int:session_id>/status/<str:new_status>/",
        views.update_session_status,
        name="update_session_status",
    ),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("sessions/<int:session_id>/review/", views.leave_review, name="leave_review"),
    path("availability/", views.edit_availability, name="edit_availability"),
    path("inbox/", views.inbox, name="inbox"),
    path("messages/with/<int:profile_id>/", views.conversation, name="conversation"),
    path("sessions/<int:session_id>/cancel/", views.cancel_session, name="cancel_session"),
    path("sessions/<int:session_id>/reschedule/", views.reschedule_session, name="reschedule_session"),
    path("mentors/<int:mentor_id>/request-session/", views.request_session, name="request_session"),
    # Feed + posts
    path("feed/", views.feed, name="feed"),
    path("posts/new/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/edit/", views.edit_post, name="edit_post"),
    path("posts/<int:post_id>/delete/", views.delete_post, name="delete_post"),
    path("posts/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),

    # Connections
    path(
        "mentors/<int:mentor_id>/connect/",
        views.send_connection_request,
        name="send_connection_request",
    ),
    path(
        "connections/<int:connection_id>/<str:action>/",
        views.respond_connection_request,
        name="respond_connection_request",
    ),
    #public profiles
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    
    path("availability/<int:availability_id>/delete/", views.delete_availability, name="delete_availability"),
    path("feed/", views.feed, name="feed"),
    path("posts/new/", views.create_post, name="create_post"),
    path("posts/<int:post_id>/like/", views.toggle_like, name="toggle_like"),
    path("posts/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("mentors/<int:mentor_id>/follow/", views.follow_mentor, name="follow_mentor"),
    path("mentors/<int:mentor_id>/unfollow/", views.unfollow_mentor, name="unfollow_mentor"),
    path("mentors/<int:mentor_id>/follow/", views.toggle_follow, name="toggle_follow"),
    path("following/", views.my_follows, name="my_follows"),
    path("profiles/<int:profile_id>/", views.profile_public, name="profile_public"),
    path("conversation/<int:profile_id>/", views.conversation, name="conversation"),
    path("follow/<int:mentor_id>/", views.toggle_follow, name="toggle_follow"),

#path for online scheduler
   path("schedule/<int:mentor_id>/", views.schedule, name="schedule"),



]


