# billing/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'subscription-plans', views.SubscriptionPlanViewSet, basename='subscription-plans')
router.register(r'subscriptions', views.RestaurantSubscriptionViewSet, basename='subscriptions')
router.register(r'payment-methods', views.PaymentMethodViewSet, basename='payment-methods')
router.register(r'billing-records', views.BillingRecordViewSet, basename='billing-records')
router.register(r'invoices', views.BillingInvoiceViewSet, basename='invoices')

app_name = 'billing'

urlpatterns = [
    path('', include(router.urls)),
    path('restaurants/', views.RestaurantDropdownView.as_view(), name='restaurant-dropdown'),
    path('plans-dropdown/', views.SubscriptionPlanDropdownView.as_view(), name='plans-dropdown'),
]
