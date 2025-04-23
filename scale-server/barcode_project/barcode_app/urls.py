from django.urls import path
from .views import LoginView, RegisterView, AssignBarcodeView, GetUserDataView, MealListView, MealDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('assign_barcode/', AssignBarcodeView.as_view(), name='assign_barcode'),
    path('get_user_data/', GetUserDataView.as_view(), name='get_user_data'),
    path('meals/', MealListView.as_view(), name='meals'),
    path('meals/<int:pk>/', MealDetailView.as_view(), name='meal-detail'),
]
