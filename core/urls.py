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

]
    

