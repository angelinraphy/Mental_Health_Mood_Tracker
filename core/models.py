from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError

class Role(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    PATIENT = 'patient', 'Patient'
    DOCTOR = 'doctor', 'Doctor'
    CAREGIVER = 'caregiver', 'Caregiver'
    RESEARCHER = 'researcher', 'Researcher'

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PATIENT,
    )
    date_of_birth = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.role == Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)



class MoodEntry(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_entries', limit_choices_to={'role': Role.PATIENT})
    mood_level = models.IntegerField(help_text="Mood level from 1-10")
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.username} - {self.mood_level} on {self.date}"

class Prescription(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions', limit_choices_to={'role': Role.PATIENT})
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescribed_medicines', limit_choices_to={'role': Role.DOCTOR})
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    date_prescribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.patient.username} by Dr. {self.doctor.username}"
