from django.shortcuts import render, redirect,get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from datetime import datetime, timedelta,time as dt_time
from django.db import IntegrityError,transaction
from django.utils import timezone



# Create your views here.


def index(request):
    return render(request,'index.html')

def user_dashboard(request):
    return render(request,'user_dashboard.html')

def doctor_dashboard(request):
    return render(request,'doctor_dashboard.html')

def hospital_dashboard(request):
    return render(request,'hospital_dashboard.html')

def admin_dashboard(request):
    return render(request,'admin_dashboard.html')

def logout_user(request):
    request.session.flush()
    return redirect('loginpage')

def loginpage(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            login = Login.objects.get(email=email)

        except Login.DoesNotExist:
            messages.error(request, 'User does not exist. Please register first.')
            return redirect('loginpage')

        if not check_password(password, login.password):
            messages.error(request, 'Incorrect email or password.')
            return redirect('loginpage')

        # Normal user can login without status checking
        if login.usertype == 'user':
            request.session['login_id'] = login.id
            request.session['usertype'] = login.usertype
            return redirect('user_dashboard')

        # Hospital approval status
        elif login.usertype == 'hospital':
            if login.status == 0:
                messages.warning(request, 'Your hospital account is waiting for admin approval.')
                return redirect('loginpage')

            elif login.status == 2:
                messages.error(request, 'Your hospital registration has been rejected by the admin.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('hospital_dashboard')

        # Doctor approval status
        elif login.usertype == 'doctor':
            if login.status == 0:
                messages.warning(request, 'Your doctor account is waiting for hospital approval.')
                return redirect('loginpage')

            elif login.status == 2:
                messages.error(request, 'Your doctor registration has been rejected by the hospital.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('doctor_dashboard')

        # Admin approval status
        elif login.usertype == 'admin':
            if login.status == 0:
                messages.warning(request, 'Your admin account is not active yet.')
                return redirect('loginpage')

            elif login.status == 1:
                request.session['login_id'] = login.id
                request.session['usertype'] = login.usertype
                return redirect('admin_dashboard')

        messages.error(request, 'Invalid user type or inactive account.')
        return redirect('loginpage')

    return render(request, 'login.html')



def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form2 = LoginForm(request.POST)

        if form.is_valid() and form2.is_valid():
            login = form2.save(commit=False)
            login.usertype = 'user'
            login.password = make_password(form2.cleaned_data['password'])
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.save()

            messages.success(request, 'User registered successfully')
            return redirect('index')
    else:
        form = UserRegisterForm()
        form2 = LoginForm()

    return render(request, 'user_register.html', {'form': form,'form2': form2})


def hospital_register(request):
    if request.method == 'POST':
        form = HospitalRegisterForm(request.POST)
        form2 = LoginForm(request.POST)

        if form.is_valid() and form2.is_valid():
            login = form2.save(commit=False)
            login.usertype = 'hospital'
            login.password = make_password(form2.cleaned_data['password'])
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.save()

            messages.success(request, 'Hospital registered successfully')
            return redirect('index')
    else:
        form = HospitalRegisterForm()
        form2 = LoginForm()

    return render(request, 'hospital_register.html', {'form': form,'form2': form2})



def doctor_register(request):
    a=request.session.get('login_id')
    hosp=get_object_or_404(Hospital,loginid=a)

    if request.method == 'POST':
        form = DoctorRegisterForm(request.POST, request.FILES)
        form2 = LoginForm(request.POST)

        if form.is_valid() and form2.is_valid():
            login = form2.save(commit=False)
            login.usertype = 'doctor'
            login.password = make_password(form2.cleaned_data['password'])
            login.save()
            user = form.save(commit=False)
            user.loginid = login
            user.hospitalid=hosp
            user.save()

            messages.success(request, 'Doctor registered successfully')
            return redirect('hospital_dashboard')
    else:
        form = DoctorRegisterForm()
        form2 = LoginForm()

    return render(request, 'doctor_register.html', {'form': form,'form2': form2})


def adminusersview(request):
    a=User.objects.all().order_by('-id')
    return render(request,'adminusersview.html',{'a':a})

def adminhospitalsview(request):
    a=Hospital.objects.all().order_by('-id')
    return render(request,'adminhospitalsview.html',{'a':a})

def admindoctorsview(request):
    a=Doctor.objects.all().order_by('-id')
    return render(request,'admindoctorsview.html',{'a':a})


def approve_hospital(request,id):
    hospital=get_object_or_404(Login,id=id)
    hospital.status = 1
    hospital.save()
    return redirect('adminhospitalsview')


def reject_hospital(request,id):
    hospital=get_object_or_404(Login,id=id)
    hospital.status = 2
    hospital.save()
    return redirect('adminhospitalsview')



def hospitaldoctorsview(request):
    a=request.session.get('login_id')
    b=get_object_or_404(Hospital,loginid=a)
    doc=Doctor.objects.filter(hospitalid=b)
    return render(request,'hospitaldoctorsview.html',{'doc':doc})


def userdoctorsview(request):

    a = request.session.get('login_id')

    b = get_object_or_404(User, loginid=a)

    search = request.GET.get('search', '').strip()

    if search:
        doc = Doctor.objects.filter(
            Q(doctor_name__icontains=search) |
            Q(hospitalid__hospital_name__icontains=search)
        )
    else:
        doc = Doctor.objects.all()

    return render(request, 'user_doctorsview.html', {'doc': doc,'search': search})





def build_15min_slots(start_time, end_time, step=15):
    base = datetime(2000, 1, 1)
    s = datetime.combine(base.date(), start_time)
    e = datetime.combine(base.date(), end_time)

    out = []
    cur = s
    while cur + timedelta(minutes=step) <= e:
        out.append(cur.time())
        cur += timedelta(minutes=step)
    return out


def in_break(t, b1, b2):
    if not b1 or not b2:
        return False
    return b1 <= t < b2


def bookappointment(request, id):
    login_id = request.session.get('login_id')
    patient  = get_object_or_404(User, loginid=login_id)
    doctor   = get_object_or_404(Doctor, id=id)
 
    date_str = request.GET.get("date") or request.POST.get("date")
    selected_date = None
 
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = None
 
    slots = []
 
    if selected_date:
        s = (
            slot.objects.filter(d_id=doctor, slot_date=selected_date).first()
            or slot.objects.filter(d_id=doctor, slot_date__isnull=True).first()
        )
 
        if s:
            all_times = build_15min_slots(s.starttime, s.endtime, step=15)
            all_times = [t for t in all_times if not in_break(t, s.break_start, s.break_end)]
 
            # ── Filter past slots when selected date is today ──────────────
            now = timezone.localtime()
            if selected_date == now.date():
                all_times = [
                    t for t in all_times
                    # FIX: use timezone.make_aware instead of combine(…, tzinfo=…)
                    if timezone.make_aware(
                        datetime.combine(selected_date, t)
                    ) >= now
                ]
 
            # ── Booked slots: store as "HH:MM:SS" strings for comparison ──
            #    Appointment.time is a CharField, so values_list returns strings.
            #    We normalise both sides to "HH:MM:SS" to avoid type mismatch.
            booked_raw = Appointment.objects.filter(
                doctorid=doctor,
                date=selected_date,
                cancel_status=0,           # only active (not cancelled) appointments
            ).values_list("time", flat=True)
 
            # Normalise DB values → "HH:MM:SS" (handles "HH:MM" edge cases too)
            booked = set()
            for raw in booked_raw:
                raw = str(raw).strip()
                if len(raw) == 5:          # "HH:MM"  → "HH:MM:SS"
                    raw = raw + ":00"
                booked.add(raw)
 
            for t in all_times:
                time_str = t.strftime("%H:%M:%S")   # always "HH:MM:SS"
                slots.append({
                    "value":    time_str,
                    "label":    t.strftime("%I:%M %p"),
                    "disabled": time_str in booked,   # FIX: compare strings to strings
                })
 
    # ── Handle POST (save booking) ─────────────────────────────────────────
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            a = form.save(commit=False)
            a.userid    = patient
            a.doctorid  = doctor
            a.cancel_status  = 0
 
            if not selected_date:
                form.add_error("date", "Please select a valid date.")
            else:
                a.date = selected_date
 
                # Build the set of currently-allowed slot strings
                allowed = {x["value"] for x in slots if not x["disabled"]}
 
                # Normalise the submitted time value
                chosen = str(a.time).strip()
                if len(chosen) == 5:
                    chosen = chosen + ":00"
 
                if chosen not in allowed:
                    form.add_error(
                        "time",
                        "This slot is not available. Please choose another."
                    )
                else:
                    try:
                        with transaction.atomic():
                            a.save()
                        return redirect("payment", a.id, doctor.consultation_fee)
                    except IntegrityError:
                        # Caught by the DB unique_together constraint (see model below)
                        form.add_error(
                            "time",
                            "This slot was just booked by someone else. Please choose another."
                        )
        # form invalid — fall through and re-render with errors
    else:
        form = AppointmentForm(initial={"date": date_str})
 
    return render(request, "bookappointment.html", {
        "form":          form,
        "doctor":        doctor,
        "selected_date": selected_date.strftime("%Y-%m-%d") if selected_date else "",
        "slots":         slots,
    })




# ============================================================
#  views.py — add this delete_slot view
# ============================================================
 
def delete_slot(request, slot_id):
    """Delete a slot. Only the owning doctor can delete."""
    p = request.session.get('login_id')
    q = get_object_or_404(Doctor, loginid=p)
    s = get_object_or_404(slot, id=slot_id, d_id=q)   # ensures doctor owns it
    if request.method == "POST":
        s.delete()
        messages.success(request, "Slot deleted successfully.")
    return redirect('slotadding', id=q.id)
 
 
# ============================================================
#  views.py — update slotadding to pass slots to template
#  so the panel can show existing slots
# ============================================================
 
def slotadding(request,id):
    p = request.session.get('login_id')
    h=get_object_or_404(Hospital,loginid=p)
    q = get_object_or_404(Doctor, id=id)
 
    if request.method == "POST":
        form = TimeslotForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            base_defaults = {
                "starttime":   data["starttime"],
                "endtime":     data["endtime"],
                "break_start": data.get("break_start"),
                "break_end":   data.get("break_end"),
                "weekday":     None,
            }
 
            created_count = 0
            updated_count = 0
 
            if data["mode"] == "single":
                _, created = slot.objects.update_or_create(
                    d_id=q,
                    h_id=h,
                    slot_date=data["slot_date"],
                    defaults=base_defaults,
                )
                if created:
                    created_count = 1
                else:
                    updated_count = 1
            else:
                selected_weekdays = data["weekdays"]
                current = data["start_date"]
                while current <= data["end_date"]:
                    if int(current.weekday()) in [int(w) for w in selected_weekdays]:
                        _, created = slot.objects.update_or_create(
                            d_id=q,
                            h_id=h,
                            slot_date=current,
                            defaults=base_defaults,
                        )
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                    current += timedelta(days=1)
 
            if created_count and updated_count:
                messages.success(request, f"Created {created_count} and updated {updated_count} slot(s).")
            elif created_count:
                messages.success(request, f"Saved {created_count} slot{'s' if created_count != 1 else ''}.")
            elif updated_count:
                messages.info(request, f"Updated timings for {updated_count} existing slot{'s' if updated_count != 1 else ''}.")
            else:
                messages.warning(request, "No slots were saved. Check that selected weekdays fall within your date range.")
 
            return redirect('hospitaldoctorsview')
    else:
        form = TimeslotForm()
 
    # ← Pass existing slots to template so panel can display them
    doctor_slots = slot.objects.filter(d_id=q).order_by('slot_date')
 
    return render(request, 'slot.html', {
        'form': form,
        'slots': doctor_slots,   # ← NEW
    })
