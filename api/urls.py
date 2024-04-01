from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('account', views.AccountViewSet, basename='Account')
router.register('transaction', views.TransactionViewSet, basename='Transaction')

urlpatterns = router.urls
