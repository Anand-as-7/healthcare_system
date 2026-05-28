from django.db import models
from django.utils import timezone
import re

# Create your models here.


class Login(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    usertype = models.CharField(max_length=20)
    status = models.IntegerField(default=0)

class User(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    gender = models.CharField(max_length=20)
    age = models.IntegerField()
    contactnumber = models.CharField(max_length=12)
    district = models.CharField(max_length=50)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

class Hospital(models.Model):
    hospitalid = models.CharField(max_length=30,unique=True,editable=False)
    hospital_name = models.CharField(max_length=150)
    address = models.TextField()
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)

    def generate_hospital_id(self):
        first_word = self.hospital_name.split()[0].upper()
        prefix = re.sub(r'[^A-Z0-9]', '', first_word)
        year = timezone.now().year
        base_id = f"{prefix}{year}"
        if not Hospital.objects.filter(hospitalid=base_id).exists():
            return base_id
        
        count = Hospital.objects.filter(
            hospitalid__startswith=base_id
        ).count() + 1

        return f"{base_id}{count:03d}"

    def save(self, *args, **kwargs):
        if not self.hospitalid:
            self.hospitalid = self.generate_hospital_id()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hospital_name} - {self.hospitalid}"



class Doctor(models.Model):
    doctor_name = models.CharField(max_length=100)
    photo=models.FileField(upload_to='media/')
    gender = models.CharField(max_length=20)
    dob = models.DateField()
    specialization = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    consultation_fee = models.IntegerField(default=0)
    contact = models.CharField(max_length=15)
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    hospitalid = models.ForeignKey(Hospital, on_delete=models.CASCADE)



class Appointment(models.Model):
    date = models.DateField()
    time = models.TimeField()
    userid = models.ForeignKey(User, on_delete=models.CASCADE)
    doctorid = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    payment_status = models.IntegerField(default=0)
    cancel_status = models.IntegerField(default=0)
    refund_status = models.IntegerField(default=0)

   

class slot(models.Model):
    d_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    h_id = models.ForeignKey(Hospital, on_delete=models.CASCADE,null=True)

    slot_date = models.DateField(null=True, blank=True)
    weekday = models.IntegerField(null=True, blank=True)  # 0=Mon ... 6=Sun

    starttime = models.TimeField()
    endtime = models.TimeField()

    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)

    currentdate = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # Prevent duplicates for weekly schedule entries
            models.UniqueConstraint(fields=["d_id", "weekday"], name="uniq_doctor_weekday_slot"),
            # Prevent duplicates for date-specific entries
            models.UniqueConstraint(fields=["d_id", "slot_date"], name="uniq_doctor_date_slot"),
        ]
