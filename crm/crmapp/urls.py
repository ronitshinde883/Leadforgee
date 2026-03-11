from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views.test_views import home, hello
from .views.auth_views import (
    LoginView,
    RegisterOwnerView,
    RegisterEmployeeView,
    MeView,
    LogoutView,
    CompanyUsersView,
    UpdateUserRoleView,
    ChangePasswordView,
    RemoveCompanyUserView,
    # delete_user,
    # reactivate_user,
)

from .views.company_views import CompanyAPIView

from .views.contacts_view import (
    create_contact,
    get_all_contacts,
    get_contact_by_id,
    update_contact,
    delete_contact,
    reactivate_contact,
)

from .views.lead_view import LeadViewSet

from .views.task_view import TaskViewSet

from .views.deals_views import (
    create_deal,
    update_deal, 
    get_all_deals,
    get_deal_by_id,
    delete_deal,
    reactivate_deal
)

from .views.activity_view import (
    ActivityLogView
)

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename="leads")
router.register(r'tasks', TaskViewSet, basename="tasks")

urlpatterns = [
    # TESTING URLS (TEMPORARY)
    path("user/", home, name="user_home"),
    path("test", hello, name="hello"),
    path("", include(router.urls)),
    path("company/", CompanyAPIView.as_view()),

    # AUTH URLS
    path("auth/register", RegisterOwnerView.as_view()),
    path("auth/register-employee",RegisterEmployeeView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("auth/me", MeView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("auth/<str:user_id>/delete", RemoveCompanyUserView.as_view()),
    # path("auth/<str:user_id>/reactivate", reactivate_user, name="reactivate_user"),   # DEV ONLY
    path("auth/change-password", ChangePasswordView.as_view()),

    # COMPANY URLS
    path("company/users", CompanyUsersView.as_view()),
    path("company/user/<str:id>/role", UpdateUserRoleView.as_view()),

    # ACTIVITY URLS
    path("activity", ActivityLogView.as_view()),
]
