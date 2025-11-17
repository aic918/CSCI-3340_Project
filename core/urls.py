from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # or whatever your main view is
    path("select-role/", views.select_role, name="select_role"),  # choose Mentor/Mentee
    path("signup/", views.signup, name="signup"),   # signup form
    path("mentors/", views.mentor_list, name="mentor_list"),  # mentor list
    path("logout/", views.logout_view, name="logout_custom"),  # logut view
    path("dashboard/", views.dashboard, name="dashboard"),  # user dashboard
]

