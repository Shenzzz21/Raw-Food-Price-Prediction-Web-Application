from django.urls import path
from . import views

urlpatterns = [
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),
    path('get_feedbacks/', views.get_feedbacks, name='get_feedbacks'),
    path('search_feedbacks/', views.search_feedbacks, name='search_feedbacks'),
    path('delete_feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),
]