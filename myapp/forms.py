from django import forms
from .models import *
from django.utils import timezone
import re


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



class PaymentForm(forms.ModelForm):
    def clean_person_name(self):
        name = (self.cleaned_data.get("person_name") or "").strip()
        if not re.fullmatch(r"[A-Za-z ]+", name):
            raise forms.ValidationError("Cardholder name must contain letters only.")
        if len(name.replace(" ", "")) < 2:
            raise forms.ValidationError("Cardholder name is too short.")
        return " ".join(name.split())

    def clean_card_number(self):
        raw = (self.cleaned_data.get("card_number") or "").strip()
        digits = re.sub(r"\D", "", raw)
        if len(digits) != 16:
            raise forms.ValidationError("Card number must be exactly 16 digits.")
        return digits

    def clean_cvv(self):
        cvv = (self.cleaned_data.get("cvv") or "").strip()
        if not re.fullmatch(r"\d{3}", cvv):
            raise forms.ValidationError("CVV must be exactly 3 digits.")
        return cvv

    class Meta:
        model =Payment
        fields =['person_name','card_number','cvv','expiry_year','expiry_month']



class Prescriptionform(forms.ModelForm):
    class Meta:
        model=Prescription
        fields=['diagnosis','medicines','dosage']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 4, 'class': 'w-full resize-y rounded-lg border-outline-variant bg-surface-container-lowest text-sm focus:border-primary focus:ring-primary/20', 'placeholder': 'Enter diagnosis summary'}),
            'medicines': forms.Textarea(attrs={'rows': 4, 'class': 'w-full resize-y rounded-lg border-outline-variant bg-surface-container-lowest text-sm focus:border-primary focus:ring-primary/20', 'placeholder': 'List medicines with strength'}),
            'dosage': forms.Textarea(attrs={'rows': 3, 'class': 'w-full resize-y rounded-lg border-outline-variant bg-surface-container-lowest text-sm focus:border-primary focus:ring-primary/20', 'placeholder': 'Add dosage schedule and duration'}),
        }


class ComplaintForm(forms.ModelForm):
    CATEGORY_CHOICES = [
        ("Billing", "Billing"),
        ("Service", "Service"),
        ("Medical", "Medical"),
        ("Technical", "Technical"),
    ]

    category = forms.ChoiceField(choices=CATEGORY_CHOICES)

    class Meta:
        model = Complaint
        fields = ["category", "subject", "message"]
        widgets = {
            "subject": forms.TextInput(attrs={
                "id": "subject",
                "class": "w-full h-12 px-4 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md input-focus-ring outline-none transition-all placeholder:text-on-surface-variant/50",
                "placeholder": "Briefly describe the issue",
            }),
            "message": forms.Textarea(attrs={
                "id": "description",
                "rows": 6,
                "class": "w-full p-4 rounded-lg bg-surface-container-lowest border border-outline-variant text-on-surface font-body-md input-focus-ring outline-none transition-all placeholder:text-on-surface-variant/50 resize-y",
                "placeholder": "Provide as much detail as possible to help us resolve your concern...",
            }),
        }



class AIPredictionForm(forms.ModelForm):
    class Meta:
        model = AIPrediction
        fields = ['xray_image', 'symptoms']
        widgets = {
            'symptoms': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full rounded-lg border border-outline-variant bg-surface-container-lowest p-3 text-sm focus:border-primary focus:ring-1 focus:ring-primary',
                'placeholder': 'Describe your symptoms (e.g. cough, chest pain, shortness of breath)...'
            }),
            'xray_image': forms.ClearableFileInput(attrs={
                'class': 'w-full text-sm text-on-surface-variant file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary file:text-on-primary hover:file:bg-primary/90',
                'accept': 'image/*'
            }),
        }