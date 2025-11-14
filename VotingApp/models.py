from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Voter(models.Model):
    matric_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=128)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_sha256$"):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.matric_number  # Display matric number in admin panel


class Position(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="candidates")
    image = models.ImageField(upload_to="candidate_pictures/", null=True, blank=True)  # Added image field
    matric = models.CharField(max_length=20,default="Unknown",null = True, blank = True,unique=True)
    state_of_origin = models.CharField(max_length=50,default="Unknown")
    course_of_study = models.CharField(max_length=100,default="Unknown")
    level = models.IntegerField(default=100)

    def __str__(self):
        return f"{self.name} ({self.position.name})"


class Vote(models.Model):
    voter = models.ForeignKey(Voter, on_delete=models.PROTECT)  # Prevent deletion of voters
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.voter.matric_number} voted for {self.candidate.name}"