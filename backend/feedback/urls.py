from django.urls import path
from .views import submit_feedback, get_feedbacks, search_feedbacks

urlpatterns = [
    path('submit_feedback/', submit_feedback, name='submit_feedback'),
    path('get_feedbacks/', get_feedbacks, name='get_feedbacks'),
    path('search_feedbacks/', search_feedbacks, name='search_feedbacks'),  # Endpoint to search feedbacks
    # path('get_user_id/', get_user_id, name='get_user_id'),

]
