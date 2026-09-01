from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("plans/", views.subscription_plans, name="subscription_plans"),
    path(
        "checkout/<int:plan_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("my-subscription/", views.my_subscription, name="my_subscription"),
    path(
        "cancel-subscription/",
        views.cancel_subscription,
        name="cancel_subscription",
    ),
    path("history/", views.payment_history_list, name="payment_history_list"),
    path("invoice/<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path(
        "admin-dashboard/",
        views.admin_revenue_dashboard,
        name="admin_revenue_dashboard",
    ),
    path(
        "admin-manage-subscriptions/",
        views.admin_manage_subscriptions,
        name="admin_manage_subscriptions",
    ),
    path(
        "admin-manage-subscriptions/delete/<int:plan_id>/",
        views.delete_subscription_plan,
        name="delete_plan",
    ),
    path(
        "admin-manage-subscriptions/toggle/<int:plan_id>/",
        views.toggle_plan_status,
        name="toggle_plan",
    ),
]
