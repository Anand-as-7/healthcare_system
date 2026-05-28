from django import forms
from .models import *
from django.utils import timezone


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Login
        fields = ['email', 'password']

class UserRegisterForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect(attrs={'class': 'form-check-input'}))   
    class Meta:
        model = User
        fields = ['name', 'address', 'gender', 'age','district', 'contactnumber']   

class HospitalRegisterForm(forms.ModelForm):
   
    class Meta:
        model = Hospital
        fields = ['hospital_name', 'address', 'district', 'city','contact']   

class DoctorRegisterForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES,widget=forms.RadioSelect(attrs={'class': 'form-check-input'})) 
   
    class Meta:
        model = Doctor
        fields = ['doctor_name', 'photo', 'gender', 'dob','specialization','experience','consultation_fee','contact']   
        widgets = {'dob': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),}


class AppointmentForm(forms.ModelForm):
   
    class Meta:
        model = Appointment
        fields = ['date', 'time']   
        widgets = {'date': forms.DateInput(attrs={'type': 'date','class': 'form-control'}),}
        widgets = {'time': forms.DateInput(attrs={'type': 'time','class': 'form-control'}),}



class TimeslotForm(forms.ModelForm):
    MODE_CHOICES = [
        ("single", "Single day"),
        ("recurring", "Repeat for a period"),
    ]

    WEEKDAY_CHOICES = [
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday"),
    ]

    mode = forms.ChoiceField(
        choices=MODE_CHOICES,
        widget=forms.RadioSelect,
        initial="single",
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        help_text="First day to apply the schedule",
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        help_text="Last day to apply the schedule",
    )
    weekdays = forms.MultipleChoiceField(
        required=False,
        choices=WEEKDAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        help_text="Pick at least one weekday",
    )

    class Meta:
        model = slot
        fields = ["slot_date", "starttime", "endtime", "break_start", "break_end"]
        widgets = {
            "slot_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "starttime": forms.TimeInput(format="%H:%M", attrs={"type": "text", "class": "form-control timepicker", "placeholder": "Select time"}),
            "endtime": forms.TimeInput(format="%H:%M", attrs={"type": "text", "class": "form-control timepicker", "placeholder": "Select time"}),
            "break_start": forms.TimeInput(format="%H:%M", attrs={"type": "text", "class": "form-control timepicker", "placeholder": "Select time"}),
            "break_end": forms.TimeInput(format="%H:%M", attrs={"type": "text", "class": "form-control timepicker", "placeholder": "Select time"}),
        }

 
def clean(self):
    cleaned = super().clean()
    today = timezone.localdate()          
 
    mode        = cleaned.get("mode")
    slot_date   = cleaned.get("slot_date")
    start_date  = cleaned.get("start_date")
    end_date    = cleaned.get("end_date")
    weekdays    = cleaned.get("weekdays") or []
    starttime   = cleaned.get("starttime")
    endtime     = cleaned.get("endtime")
    break_start = cleaned.get("break_start")
    break_end   = cleaned.get("break_end")
 
    # ── Time validations (unchanged) ────────────────────────
    if starttime and endtime and starttime >= endtime:
        self.add_error("endtime", "End time must be after start time.")
 
    if break_start and break_end:
        if break_start >= break_end:
            self.add_error("break_end", "Break end must be after break start.")
        if starttime and break_start <= starttime:
            self.add_error("break_start", "Break must be within the working window.")
        if endtime and break_end >= endtime:
            self.add_error("break_end", "Break must end before the working window ends.")
 
    # ── Mode validations (past-date checks added) ───────────
    if mode == "single":
        if not slot_date:
            self.add_error("slot_date", "Choose a date for the slot.")
        elif slot_date < today:                               # ← NEW
            self.add_error("slot_date", "Slot date cannot be in the past.")
 
    elif mode == "recurring":
        if not start_date or not end_date:
            self.add_error("start_date", "Select both start and end dates.")
        else:
            if start_date < today:                            # ← NEW
                self.add_error("start_date", "Start date cannot be in the past.")
            if end_date < today:                              # ← NEW
                self.add_error("end_date", "End date cannot be in the past.")
            if end_date < start_date:
                self.add_error("end_date", "End date must be on or after start date.")
 
        if not weekdays:
            self.add_error("weekdays", "Pick at least one weekday.")
        cleaned["weekdays"] = [int(day) for day in weekdays]
 
    else:
        self.add_error("mode", "Select a valid scheduling option.")
 
    return cleaned
