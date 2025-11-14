from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Voter, Position, Candidate, Vote

class VoterAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False, help_text="Leave empty to keep current password")
    
    class Meta:
        model = Voter
        fields = ['matric_number', 'department', 'password']

class VoterAdmin(admin.ModelAdmin):
    form = VoterAdminForm
    list_display = ('matric_number', 'department', 'has_voted')
    search_fields = ('matric_number', 'department')
    list_filter = ('department',)
    
    def has_voted(self, obj):
        return Vote.objects.filter(voter=obj).exists()
    has_voted.boolean = True
    has_voted.short_description = 'Has Voted'
    
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.set_password(form.cleaned_data['password'])
        elif not change:  # New voter without password
            obj.set_password('default123')  # Set a default password
        super().save_model(request, obj, form, change)

class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'candidate_image', 'matric', 'state_of_origin', 'course_of_study', 'level')

    def candidate_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    
    candidate_image.allow_tags = True
    candidate_image.short_description = "Image"

admin.site.register(Voter, VoterAdmin)  # Register Voter with custom admin
admin.site.register(Position)
admin.site.register(Candidate, CandidateAdmin)  # Register Candidate with custom admin
admin.site.register(Vote)
