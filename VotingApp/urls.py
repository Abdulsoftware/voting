from django.urls import path
from django.shortcuts import render  
from django.conf import settings
from django.conf.urls.static import static
from .views import login_view, vote_view, logout_view, home_view, dashboard_view, results_view, candidate_profile_view

urlpatterns = [
    path('', home_view, name='home'),  # Home page
    path('login/', login_view, name='login'),  
    path('dashboard/', dashboard_view, name='dashboard'),  # NEW: Dashboard
    path('vote/', vote_view, name='vote'),  
    path('results/', results_view, name='results'),  # NEW: Results page
    path('candidate/<int:candidate_id>/', candidate_profile_view, name='candidate_profile'),  # NEW: Candidate profile
    path('logout/', logout_view, name='logout'),  
    path('success/', lambda request: render(request, "VotingApp/success.html"), name='success'),  # Success page
]

# Serve candidate images during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
