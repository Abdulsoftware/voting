from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages  # For user feedback
from .models import Voter, Position, Candidate, Vote

def login_view(request):
    if request.method == "POST":
        matric_number = request.POST.get("matric_number")
        department = request.POST.get("department")
        password = request.POST.get("password")

        try:
            voter = Voter.objects.get(matric_number=matric_number, department=department)
            if voter.check_password(password):
                request.session["voter_id"] = voter.id  # Store voter ID in session
                return redirect("dashboard")  # Redirect to dashboard instead of vote
            else:
                messages.error(request, "Invalid password. Please try again.")
        except Voter.DoesNotExist:
            messages.error(request, "Invalid login credentials. Check your matric number and department.")

    return render(request, "VotingApp/login.html")

def dashboard_view(request):
    if "voter_id" not in request.session:
        messages.error(request, "You must log in to access the dashboard.")
        return redirect("login")

    voter = Voter.objects.get(id=request.session["voter_id"])
    has_voted = Vote.objects.filter(voter=voter).exists()
    
    # Get election statistics
    total_voters = Voter.objects.count()
    total_votes_cast = Vote.objects.values('voter').distinct().count()
    turnout_percentage = (total_votes_cast / total_voters * 100) if total_voters > 0 else 0
    
    context = {
        'voter': voter,
        'has_voted': has_voted,
        'total_voters': total_voters,
        'total_votes_cast': total_votes_cast,
        'turnout_percentage': round(turnout_percentage, 1),
        'positions': Position.objects.all(),
    }
    
    return render(request, "VotingApp/dashboard.html", context)

def vote_view(request):
    if "voter_id" not in request.session:
        messages.error(request, "You must log in to vote.")
        return redirect("login")

    voter = Voter.objects.get(id=request.session["voter_id"])

    # Prevent multiple votes
    if Vote.objects.filter(voter=voter).exists():
        messages.error(request, "You have already voted!")
        return redirect("success")  # Redirect to success page after voting

    if request.method == "POST":
        for position in Position.objects.all():
            candidate_id = request.POST.get(str(position.id))
            if candidate_id:
                candidate = Candidate.objects.get(id=candidate_id)
                Vote.objects.create(voter=voter, candidate=candidate)  # Store vote

        messages.success(request, "Your vote has been successfully recorded.")
        return redirect("success")  

    positions = Position.objects.prefetch_related("candidates").all()
    return render(request, "VotingApp/vote.html", {"positions": positions})

def results_view(request):
    # Get election results
    positions = Position.objects.prefetch_related('candidates').all()
    results = {}
    
    for position in positions:
        candidates = position.candidates.all()
        position_results = []
        total_votes = 0
        
        for candidate in candidates:
            vote_count = Vote.objects.filter(candidate=candidate).count()
            total_votes += vote_count
            position_results.append({
                'candidate': candidate,
                'votes': vote_count,
                'percentage': 0  # Will be calculated below
            })
        
        # Calculate percentages
        for result in position_results:
            if total_votes > 0:
                result['percentage'] = round((result['votes'] / total_votes) * 100, 1)
        
        # Sort by vote count (highest first)
        position_results.sort(key=lambda x: x['votes'], reverse=True)
        
        results[position] = {
            'candidates': position_results,
            'total_votes': total_votes
        }
    
    context = {
        'results': results,
        'total_voters': Voter.objects.count(),
        'total_votes_cast': Vote.objects.values('voter').distinct().count(),
    }
    
    return render(request, "VotingApp/results.html", context)

def candidate_profile_view(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    # Get candidate's vote count
    vote_count = Vote.objects.filter(candidate=candidate).count()
    
    # Get total votes for this position
    total_position_votes = Vote.objects.filter(candidate__position=candidate.position).count()
    vote_percentage = (vote_count / total_position_votes * 100) if total_position_votes > 0 else 0
    
    context = {
        'candidate': candidate,
        'vote_count': vote_count,
        'vote_percentage': round(vote_percentage, 1),
        'total_position_votes': total_position_votes,
    }
    
    return render(request, "VotingApp/candidate_profile.html", context)

def logout_view(request):
    request.session.flush()  # Clear session on logout
    messages.success(request, "You have been logged out.")
    return redirect("login")  # Redirect to login page

# Example voter creation (for testing only, remove in production)
def create_voter():
    voter = Voter(matric_number="12345", department="Computer Science")
    voter.set_password("password123")
    voter.save()

def home_view(request):
    return render(request, "VotingApp/home.html")  # Ensure home.html exists
