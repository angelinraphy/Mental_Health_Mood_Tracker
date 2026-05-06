from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from .models import User, Role, MoodEntry, Prescription
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the long help text instructions from below the fields
        for field in self.fields.values():
            field.help_text = ''

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        messages.error(self.request, "Invalid credentials")
        return super().form_invalid(form)

def home(request):
    if not request.user.is_authenticated:
        return render(request, 'core/landing.html')
        
    user = request.user
    if user.role == Role.PATIENT:
        return redirect('patient_dashboard')
    elif user.role == Role.DOCTOR:
        return redirect('doctor_dashboard')
    elif user.role == Role.CAREGIVER:
        return redirect('caregiver_dashboard')
    elif user.role == Role.RESEARCHER:
        return redirect('researcher_dashboard')
    elif user.role == Role.ADMIN:
        return redirect('admin_dashboard')
    return redirect('login')

# --- Patient Mood CRUD ---
from .forms import MoodEntryForm, PrescriptionForm

@method_decorator(login_required, name='dispatch')
class MoodCreateView(CreateView):
    model = MoodEntry
    form_class = MoodEntryForm
    template_name = 'core/mood_form.html'
    success_url = reverse_lazy('patient_dashboard')

    def form_valid(self, form):
        form.instance.patient = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class MoodUpdateView(UpdateView):
    model = MoodEntry
    form_class = MoodEntryForm
    template_name = 'core/mood_form.html'
    success_url = reverse_lazy('patient_dashboard')

    def get_queryset(self):
        return MoodEntry.objects.filter(patient=self.request.user)

@method_decorator(login_required, name='dispatch')
class MoodDeleteView(DeleteView):
    model = MoodEntry
    template_name = 'core/mood_confirm_delete.html'

    def get_success_url(self):
        role = self.request.user.role
        if role == Role.DOCTOR:
            return reverse_lazy('doctor_dashboard')
        return reverse_lazy('patient_dashboard')

    def get_queryset(self):
        if self.request.user.role in [Role.DOCTOR, Role.ADMIN]:
            return MoodEntry.objects.all()
        return MoodEntry.objects.filter(patient=self.request.user)

# --- Dashboards ---
@login_required
def patient_dashboard(request):
    if request.user.role != Role.PATIENT:
        return redirect('home')
    entries = MoodEntry.objects.filter(patient=request.user).order_by('-date')
    prescriptions = Prescription.objects.filter(patient=request.user).order_by('-date_prescribed')
    return render(request, 'core/patient_dashboard.html', {'entries': entries, 'prescriptions': prescriptions})

@login_required
def caregiver_dashboard(request):
    if request.user.role != Role.CAREGIVER:
        return redirect('home')
    entries = MoodEntry.objects.all().order_by('-date')
    return render(request, 'core/caregiver_dashboard.html', {'entries': entries})

@login_required
def doctor_dashboard(request):
    if request.user.role != Role.DOCTOR:
        return redirect('home')
    # Can be customized with medical metrics in the future
    entries = MoodEntry.objects.all().order_by('-date')
    return render(request, 'core/doctor_dashboard.html', {'entries': entries})

@login_required
def admin_dashboard(request):
    if request.user.role != Role.ADMIN:
        return redirect('home')
    users = User.objects.all()
    return render(request, 'core/admin_dashboard.html', {'users': users})

@login_required
def researcher_dashboard(request):
    if request.user.role != Role.RESEARCHER:
        return redirect('home')
    entries = MoodEntry.objects.all()
    return render(request, 'core/researcher_dashboard.html', {'entries': entries})

@method_decorator(login_required, name='dispatch')
class UserDeleteView(DeleteView):
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('admin_dashboard')

    def get_queryset(self):
        if self.request.user.role == Role.ADMIN or self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.none()

@method_decorator(login_required, name='dispatch')
class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'core/prescribe_medicine.html'
    success_url = reverse_lazy('doctor_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != Role.DOCTOR:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.doctor = self.request.user
        form.instance.patient_id = self.kwargs['patient_id']
        messages.success(self.request, "Prescription successfully added.")
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(User, id=self.kwargs['patient_id'])
        return context
