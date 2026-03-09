from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views.test_views import home, hello
from .views.auth_views import (
    LoginView,
    RegisterOwnerView,
    register_employee,
    login_user,
    get_current_user,
    logout_user,
    delete_user,
    reactivate_user,
    change_roles,
    change_password,
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
    path(
        "auth/register-employee/<str:company_code>",
        register_employee,
        name="register_employee",
    ),
    path("auth/login", LoginView.as_view()),
    path("auth/me", get_current_user, name="get_current_user"),
    path("auth/logout", logout_user, name="logout_user"),
    path("auth/<str:user_id>/delete", delete_user, name="delete_user"),
    path("auth/<str:user_id>/reactivate", reactivate_user, name="reactivate_user"),   # DEV ONLY
    path("auth/<str:user_id>/change-role", change_roles, name="change_roles"),
    path("auth/change-password", change_password, name="change-pass")

]
