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
from django.http import HttpResponse
from django.urls import reverse
from io import BytesIO
from reportlab.pdfgen import canvas



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
            if login.status == 2:
                messages.warning(request, 'Your doctor account is disabled by hospital administration.')
                return redirect('loginpage')

        
            elif login.status == 0:
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


def _normalize_time_str(raw):
    value = str(raw).strip()
    if len(value) == 5:
        value = value + ":00"
    return value


def _get_schedule_for_date(doctor, target_date):
    day_schedule = slot.objects.filter(d_id=doctor, slot_date=target_date).first()
    if day_schedule:
        return day_schedule

    return slot.objects.filter(
        d_id=doctor,
        slot_date__isnull=True,
        weekday=target_date.weekday(),
    ).first()


def _build_slots_for_date(doctor, selected_date, exclude_appointment_id=None):
    schedule = _get_schedule_for_date(doctor, selected_date)
    if not schedule:
        return []

    all_times = build_15min_slots(schedule.starttime, schedule.endtime, step=15)
    all_times = [t for t in all_times if not in_break(t, schedule.break_start, schedule.break_end)]

    now = timezone.localtime()
    if selected_date == now.date():
        all_times = [
            t for t in all_times
            if timezone.make_aware(datetime.combine(selected_date, t)) >= now
        ]

    booked_qs = Appointment.objects.filter(
        doctorid=doctor,
        date=selected_date,
        cancel_status=0,
    )
    if exclude_appointment_id:
        booked_qs = booked_qs.exclude(id=exclude_appointment_id)

    booked_raw = booked_qs.values_list("time", flat=True)

    booked = {_normalize_time_str(raw) for raw in booked_raw}

    return [
        {
            "value": t.strftime("%H:%M:%S"),
            "label": t.strftime("%I:%M %p"),
            "disabled": t.strftime("%H:%M:%S") in booked,
            "status": "booked" if t.strftime("%H:%M:%S") in booked else "available",
        }
        for t in all_times
    ]


def _build_available_date_markers(doctor, start_date, days_ahead=180, exclude_appointment_id=None):
    end_date = start_date + timedelta(days=days_ahead)

    dated_slots = set(
        slot.objects.filter(
            d_id=doctor,
            slot_date__isnull=False,
            slot_date__gte=start_date,
            slot_date__lte=end_date,
        ).values_list("slot_date", flat=True)
    )

    recurring_weekdays = set(
        slot.objects.filter(
            d_id=doctor,
            slot_date__isnull=True,
            weekday__isnull=False,
        ).values_list("weekday", flat=True)
    )

    candidate_dates = set(dated_slots)
    if recurring_weekdays:
        for offset in range(days_ahead + 1):
            current = start_date + timedelta(days=offset)
            if current.weekday() in recurring_weekdays:
                candidate_dates.add(current)

    available_dates = []
    for day in sorted(candidate_dates):
        if any(
            not slot_data["disabled"]
            for slot_data in _build_slots_for_date(
                doctor,
                day,
                exclude_appointment_id=exclude_appointment_id,
            )
        ):
            available_dates.append(day.strftime("%Y-%m-%d"))

    return available_dates



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






def bookappointment(request, id):
    login_id = request.session.get("login_id")
    patient = get_object_or_404(User, loginid=login_id)
    doctor = get_object_or_404(Doctor, id=id)
    date_str = request.GET.get("date") or request.POST.get("date") or timezone.localdate().strftime("%Y-%m-%d")
    selected_date = None
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = None
    slots = _build_slots_for_date(doctor, selected_date) if selected_date else []
    available_dates = _build_available_date_markers(doctor, timezone.localdate(), days_ahead=180)
    available_slot_count = sum(1 for slot_data in slots if not slot_data["disabled"])
    booked_slot_count = sum(1 for slot_data in slots if slot_data["disabled"])
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.userid = patient
            appointment.doctorid = doctor
            appointment.cancel_status = 0
            if not selected_date:
                form.add_error("date", "Please select a valid date.")
            elif selected_date < timezone.localdate():
                form.add_error("date", "Past dates are not allowed.")
            else:
                appointment.date = selected_date
                allowed = {x["value"] for x in slots if not x["disabled"]}
                chosen = _normalize_time_str(appointment.time)
                if chosen not in allowed:
                    form.add_error("time", "This slot is not available. Please choose another.")
                else:
                    try:
                        with transaction.atomic():
                            appointment.save()
                        return redirect("payment", appointment.id)
                    except IntegrityError:
                        form.add_error("time", "This slot was just booked by someone else. Please choose another.")
    else:
        form = AppointmentForm(initial={"date": date_str})
    return render(request, "bookappointment.html", {
        "form": form,
        "doctor": doctor,
        "selected_date": selected_date.strftime("%Y-%m-%d") if selected_date else "",
        "slots": slots,
        "available_dates": available_dates,
        "available_slot_count": available_slot_count,
        "booked_slot_count": booked_slot_count,
    })


def payment(request, id):
    login_id = request.session.get('login_id')
    patient = get_object_or_404(User, loginid=login_id)
    appointment = get_object_or_404(Appointment, id=id, userid=patient)
    if appointment.payment_status == 1:
        return redirect("bookingconfirmation", appointment.id)
    amount = appointment.doctorid.consultation_fee
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_row = form.save(commit=False)
            payment_row.userid = patient.loginid
            payment_row.appointmentid = appointment
            payment_row.amount = amount
            with transaction.atomic():
                payment_row.save()
                appointment.payment_status = 1
                appointment.save(update_fields=["payment_status"])
            return redirect("bookingconfirmation", appointment.id)
    else:
        form = PaymentForm()
    return render(request, 'payment.html', {
        'form': form,
        'appointment': appointment,
        'doctor': appointment.doctorid,
        'amount': amount,
    })

def bookingconfirmation(request, id):
    login_id = request.session.get('login_id')
    patient = get_object_or_404(User, loginid=login_id)
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctorid", "doctorid__hospitalid"),
        id=id,
        userid=patient,
    )
    if appointment.payment_status != 1:
        messages.error(request, "Payment not completed for this appointment.")
        return redirect("payment", appointment.id)
    return render(request, 'bookingconfirmation.html', {'appointment': appointment})


def download_receipt(request, id):
    login_id = request.session.get('login_id')
    patient = get_object_or_404(User, loginid=login_id)
    appointment = get_object_or_404(
        Appointment.objects.select_related("doctorid", "doctorid__hospitalid"),
        id=id,
        userid=patient,
    )

    if appointment.payment_status != 1:
        messages.error(request, "Receipt is available only after successful payment.")
        return redirect("bookingconfirmation", appointment.id)

    payment_row = Payment.objects.filter(appointmentid=appointment).order_by("-id").first()
    amount = payment_row.amount if payment_row else appointment.doctorid.consultation_fee

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "MEDSTREAM APPOINTMENT RECEIPT")
    y -= 30
    pdf.setFont("Helvetica", 11)

    lines = [
        f"Receipt Date: {timezone.localdate()}",
        f"Appointment ID: MS-{appointment.id}",
        f"Doctor: {appointment.doctorid.doctor_name}",
        f"Specialization: {appointment.doctorid.specialization}",
        f"Hospital: {appointment.doctorid.hospitalid.hospital_name}",
        f"Date: {appointment.date}",
        f"Time: {appointment.time.strftime('%I:%M %p')}",
        "Mode: Video Consultation",
        f"Amount Paid: INR {amount}.00",
        "Payment Status: Paid",
    ]

    for line in lines:
        pdf.drawString(50, y, line)
        y -= 20

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename=\"receipt_MS_{appointment.id}.pdf\"'
    return response




def user_appointmentsview(request):
    login_id = request.session.get('login_id')
    user = get_object_or_404(User, loginid=login_id)

    search = request.GET.get('search', '').strip()
    current_status = request.GET.get('status', 'upcoming').strip().lower()
    allowed_statuses = {'all', 'upcoming', 'completed', 'cancelled'}
    if current_status not in allowed_statuses:
        current_status = 'upcoming'

    qs = Appointment.objects.select_related(
        'doctorid',
        'doctorid__hospitalid',
    ).filter(
        userid=user,
        payment_status=1,
    )

    if search:
        qs = qs.filter(
            Q(doctorid__doctor_name__icontains=search) |
            Q(doctorid__specialization__icontains=search) |
            Q(doctorid__hospitalid__hospital_name__icontains=search)
        )

    now = timezone.localtime()
    status_counts = {'upcoming': 0, 'completed': 0, 'cancelled': 0}
    appointments = []

    for appt in qs:
        if appt.cancel_status == 1:
            status = 'cancelled'
        else:
            appt_dt = timezone.make_aware(datetime.combine(appt.date, appt.time))
            status = 'upcoming' if appt_dt >= now else 'completed'

        status_counts[status] += 1

        if current_status != 'all' and status != current_status:
            continue

        appointments.append({
            'appointment': appt,
            'status': status,
        })

    if current_status == 'upcoming':
        appointments.sort(key=lambda x: (x['appointment'].date, x['appointment'].time))
    else:
        appointments.sort(key=lambda x: (x['appointment'].date, x['appointment'].time), reverse=True)

    return render(request, 'user_appointmentsview.html', {
        'user': user,
        'patient_code': f"MT-{user.id:04d}",
        'appointments': appointments,
        'search': search,
        'current_status': current_status,
        'status_counts': status_counts,
    })



def user_appointmentdetailsview(request, id=None):
    if id is None:
        return redirect('user_appointmentsview')

    login_id = request.session.get('login_id')
    user = get_object_or_404(User, loginid=login_id)

    appointment = get_object_or_404(
        Appointment.objects.select_related('doctorid', 'doctorid__hospitalid'),
        id=id,
        userid=user,
        payment_status=1,
    )

    now = timezone.localtime()
    if appointment.cancel_status == 1:
        status = 'cancelled'
    else:
        appt_dt = timezone.make_aware(datetime.combine(appointment.date, appointment.time))
        status = 'upcoming' if appt_dt >= now else 'completed'
    can_modify = appointment.cancel_status == 0 and timezone.make_aware(
        datetime.combine(appointment.date, appointment.time)
    ) > now
    prescription = Prescription.objects.filter(
        appointment_id=appointment,
        doctor_id=appointment.doctorid,
    ).first()
    video = Video.objects.filter(appointmentid=appointment).order_by('-id').first()

    return render(request, 'viewdetails.html', {
        'user': user,
        'patient_code': f"MT-{user.id:04d}",
        'appointment': appointment,
        'prescription': prescription,
        'video': video,
        'status': status,
        'can_modify': can_modify,
        'appointment_code': f"MT-{appointment.id:06d}",
    })


def resheduleappointment(request, id=None):
    if id is None:
        return redirect('user_appointmentsview')

    login_id = request.session.get('login_id')
    user = get_object_or_404(User, loginid=login_id)
    appointment = get_object_or_404(
        Appointment.objects.select_related('doctorid', 'doctorid__hospitalid'),
        id=id,
        userid=user,
        payment_status=1,
    )

    now = timezone.localtime()
    appt_dt = timezone.make_aware(datetime.combine(appointment.date, appointment.time))
    if appointment.cancel_status == 1:
        messages.error(request, "Cancelled appointments cannot be rescheduled.")
        return redirect('user_appointmentdetailsview', id=appointment.id)
    if appt_dt <= now:
        messages.error(request, "Completed appointments cannot be rescheduled.")
        return redirect('user_appointmentdetailsview', id=appointment.id)

    selected_date = appointment.date
    if request.method == "POST":
        raw_date = request.POST.get("date", "").strip()
        raw_time = request.POST.get("time", "").strip()
        try:
            selected_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            selected_date = appointment.date

        available_slots = _build_slots_for_date(
            appointment.doctorid,
            selected_date,
            exclude_appointment_id=appointment.id,
        )
        allowed = {slot_data["value"] for slot_data in available_slots if not slot_data["disabled"]}
        selected_time = _normalize_time_str(raw_time)

        if selected_date < timezone.localdate():
            messages.error(request, "Past dates are not allowed.")
        elif selected_time not in allowed:
            messages.error(request, "Please choose an available slot.")
        else:
            try:
                with transaction.atomic():
                    appointment.date = selected_date
                    appointment.time = selected_time
                    appointment.save(update_fields=["date", "time"])
                messages.success(request, "Appointment rescheduled successfully.")
                return redirect('user_appointmentdetailsview', id=appointment.id)
            except IntegrityError:
                messages.error(request, "This slot was just booked. Please choose another.")
    else:
        raw_date = request.GET.get("date", "").strip()
        if raw_date:
            try:
                selected_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                selected_date = appointment.date

    slots = _build_slots_for_date(
        appointment.doctorid,
        selected_date,
        exclude_appointment_id=appointment.id,
    )
    available_dates = _build_available_date_markers(
        appointment.doctorid,
        timezone.localdate(),
        days_ahead=180,
        exclude_appointment_id=appointment.id,
    )

    return render(request, 'resheduleappointment.html', {
        'user': user,
        'patient_code': f"MT-{user.id:04d}",
        'appointment': appointment,
        'appointment_code': f"MT-{appointment.id:06d}",
        'selected_date': selected_date.strftime("%Y-%m-%d"),
        'today': timezone.localdate().strftime("%Y-%m-%d"),
        'current_time_value': appointment.time.strftime("%H:%M:%S"),
        'slots': slots,
        'available_dates': available_dates,
    })



def cancelappointment(request,id):
    login_id = request.session.get('login_id')
    user = get_object_or_404(User, loginid=login_id)
    appointment = get_object_or_404(
        Appointment,
        id=id,
        userid=user,
        payment_status=1,
    )

    if appointment.cancel_status == 1:
        messages.info(request, "Appointment is already cancelled.")
        return redirect('user_appointmentdetailsview', id=appointment.id)

    appt_dt = timezone.make_aware(datetime.combine(appointment.date, appointment.time))
    if appt_dt <= timezone.localtime():
        messages.error(request, "You can cancel only before the appointment time.")
        return redirect('user_appointmentdetailsview', id=appointment.id)

    appointment.cancel_status = 1
    appointment.save(update_fields=["cancel_status"])
    messages.success(request, "Appointment cancelled successfully.")
    return redirect('user_appointmentdetailsview', id=appointment.id)
    


def doctorappointmentsview(request):
    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'doctor':
        messages.error(request, "Please login as doctor to continue.")
        return redirect('loginpage')

    doctor = get_object_or_404(Doctor, loginid=login_id)
    current_status = request.GET.get('status', 'all').strip().lower()
    allowed_statuses = {'all', 'pending_today', 'upcoming', 'cancelled'}
    if current_status not in allowed_statuses:
        current_status = 'all'

    now = timezone.localtime()
    today = now.date()

    qs = Appointment.objects.select_related('userid').filter(
        doctorid=doctor,
        payment_status=1,
    ).order_by('date', 'time')

    rx_map = {
        rx.appointment_id_id: rx
        for rx in Prescription.objects.filter(
            doctor_id=doctor,
            appointment_id__in=qs,
        )
    }

    appointment_rows = []
    counts = {
        'all': 0,
        'pending_today': 0,
        'upcoming': 0,
        'cancelled': 0,
        'with_rx': 0,
    }

    for appt in qs:
        if appt.cancel_status == 1:
            category = 'cancelled'
        else:
            appt_dt = timezone.make_aware(datetime.combine(appt.date, appt.time))
            if appt.date == today and appt_dt >= now:
                category = 'pending_today'
            elif appt.date > today:
                category = 'upcoming'
            else:
                # Completed/expired slots are not part of this doctor workflow UI.
                continue

        counts[category] += 1
        counts['all'] += 1
        if rx_map.get(appt.id):
            counts['with_rx'] += 1

        if current_status != 'all' and category != current_status:
            continue

        appointment_rows.append({
            'appointment': appt,
            'category': category,
            'prescription': rx_map.get(appt.id),
        })

    category_order = {'pending_today': 0, 'upcoming': 1, 'cancelled': 2}
    appointment_rows.sort(
        key=lambda row: (
            category_order.get(row['category'], 9),
            row['appointment'].date,
            row['appointment'].time,
        )
    )

    prescription_form = Prescriptionform()
    modal_open_appointment_id = None
    modal_use_bound_form = False

    if request.method == 'POST':
        posted_status = request.POST.get('status', current_status).strip().lower()
        if posted_status not in allowed_statuses:
            posted_status = 'all'

        redirect_url = reverse('doctorappointmentsview')
        if posted_status != 'all':
            redirect_url = f"{redirect_url}?status={posted_status}"

        appointment_id = request.POST.get('appointment_id')
        target = get_object_or_404(
            Appointment,
            id=appointment_id,
            doctorid=doctor,
            payment_status=1,
        )
        existing_rx = Prescription.objects.filter(
            doctor_id=doctor,
            appointment_id=target
        ).first()
        action = request.POST.get('form_action', 'save')

        if action == 'delete':
            if existing_rx:
                existing_rx.delete()
                messages.success(request, "Prescription removed.")
            else:
                messages.info(request, "No prescription found to remove.")
            return redirect(redirect_url)

        prescription_form = Prescriptionform(request.POST, instance=existing_rx)
        if prescription_form.is_valid():
            rx = prescription_form.save(commit=False)
            rx.doctor_id = doctor
            rx.appointment_id = target
            rx.save()
            messages.success(request, "Prescription saved successfully.")
            return redirect(redirect_url)

        modal_open_appointment_id = str(target.id)
        modal_use_bound_form = True
        messages.error(request, "Please correct the prescription form errors.")

    return render(request, 'doctorappointmentsview.html', {
        'doctor': doctor,
        'appointment_rows': appointment_rows,
        'counts': counts,
        'current_status': current_status,
        'today': today,
        'prescription_form': prescription_form,
        'modal_open_appointment_id': modal_open_appointment_id,
        'modal_use_bound_form': modal_use_bound_form,
    })




# videoconference


import json
from urllib.parse import parse_qs, urlparse
from django.http import JsonResponse


def _video_room_id(video_url, appointment_id):
    if video_url:
        room_ids = parse_qs(urlparse(video_url).query).get("roomID")
        if room_ids and room_ids[0]:
            return room_ids[0]
    return f"appointment{appointment_id}"


def videoconference(request, id):
    login_id = request.session.get('login_id')
    usertype = request.session.get('usertype')
    if not login_id or usertype not in {'doctor', 'user'}:
        messages.error(request, "Please login to join a video call.")
        return redirect('loginpage')

    doctor = None
    patient = None
    can_save_url = False

    if usertype == 'doctor':
        doctor = get_object_or_404(Doctor, loginid=login_id)
        appointment = get_object_or_404(
            Appointment.objects.select_related('userid', 'doctorid'),
            id=id,
            doctorid=doctor,
            payment_status=1,
            cancel_status=0,
        )
        patient = appointment.userid
        participant_id = f"doctor{doctor.id}"
        participant_name = doctor.doctor_name
        back_url = reverse('doctorappointmentsview')
        can_save_url = True
    else:
        patient = get_object_or_404(User, loginid=login_id)
        appointment = get_object_or_404(
            Appointment.objects.select_related('userid', 'doctorid'),
            id=id,
            userid=patient,
            payment_status=1,
            cancel_status=0,
        )
        doctor = appointment.doctorid
        participant_id = f"patient{patient.id}"
        participant_name = patient.name
        back_url = reverse('user_appointmentdetailsview', args=[appointment.id])

    video = Video.objects.filter(appointmentid=appointment).order_by('-id').first()
    if usertype == 'user' and not (video and video.video_url):
        messages.info(request, "The video conference link is not available yet. Please wait for your doctor to start the call.")
        return redirect('user_appointmentdetailsview', id=appointment.id)

    room_id = _video_room_id(video.video_url if video else None, appointment.id)

    return render(request, 'videoconference.html', {
        'a': appointment,
        'appointment': appointment,
        'doctor': doctor,
        'patient': appointment.userid,
        'video': video,
        'room_id': room_id,
        'participant_id': participant_id,
        'participant_name': participant_name,
        'can_save_url': can_save_url,
        'save_url': reverse('save_appointment_url', args=[appointment.id]),
        'back_url': back_url,
    })


def save_appointment_url(request, id):
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Invalid request'
        }, status=400)

    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'doctor':
        return JsonResponse({
            'success': False,
            'message': 'Doctor login required'
        }, status=403)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)

    url = (data.get('url') or '').strip()
    if not url:
        return JsonResponse({
            'success': False,
            'message': 'No URL provided'
        }, status=400)

    doctor = get_object_or_404(Doctor, loginid=login_id)
    appointment = get_object_or_404(
        Appointment,
        id=id,
        doctorid=doctor,
        payment_status=1,
        cancel_status=0,
    )

    video = Video.objects.filter(appointmentid=appointment).order_by('-id').first()
    if video:
        video.video_url = url
        if not video.start_time:
            video.start_time = timezone.now()
        video.save(update_fields=['video_url', 'start_time'])
    else:
        video = Video.objects.create(
            appointmentid=appointment,
            video_url=url,
            start_time=timezone.now(),
        )

    return JsonResponse({
        'success': True,
        'message': 'URL saved successfully',
        'video_id': video.id,
        'video_url': video.video_url,
    })


def user_complaints(request):
    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'user':
        messages.error(request, "Please login as patient to continue.")
        return redirect('loginpage')

    user = get_object_or_404(User, loginid=login_id)
    complaints = Complaint.objects.filter(userid=user).order_by('-submitted_at')
    edit_id = request.GET.get('edit')
    editing_complaint = None

    if edit_id:
        editing_complaint = get_object_or_404(Complaint, id=edit_id, userid=user)

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        complaint_id = request.POST.get('complaint_id')

        if action == 'delete':
            complaint = get_object_or_404(Complaint, id=complaint_id, userid=user)
            complaint.delete()
            messages.success(request, "Complaint deleted successfully.")
            return redirect('user_complaints')

        if complaint_id:
            editing_complaint = get_object_or_404(Complaint, id=complaint_id, userid=user)

        form = ComplaintForm(request.POST, instance=editing_complaint)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.userid = user
            complaint.save()
            if editing_complaint:
                messages.success(request, "Complaint updated successfully.")
            else:
                messages.success(request, "Complaint submitted successfully.")
            return redirect('user_complaints')
    else:
        if editing_complaint:
            form = ComplaintForm(instance=editing_complaint)
        else:
            form = ComplaintForm(initial={'category': 'Service'})

    return render(request, 'user_complaints.html', {
        'user': user,
        'patient_code': f"MT-{user.id:04d}",
        'form': form,
        'complaints': complaints,
        'editing_complaint': editing_complaint,
    })





# ─────────────────────────────────────────────────────────────
#  AI PREDICTION (Chatbot + X-ray Lung Cancer)
# ─────────────────────────────────────────────────────────────
 
def ai_chatbot_predict(request):
    """
    Combined view: user types symptoms (chatbot) and optionally uploads
    an X-ray image. A simulated CNN result is returned.
    In a real deployment, replace the simulate_cnn_prediction() call
    with your actual trained TensorFlow/Keras model inference.
    """
    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'user':
        messages.error(request, 'Please login as a patient to use this feature.')
        return redirect('loginpage')
 
    user = get_object_or_404(User, loginid=login_id)
    form = AIPredictionForm()
    result = None
 
    if request.method == 'POST':
        form = AIPredictionForm(request.POST, request.FILES)
        if form.is_valid():
            prediction_obj = form.save(commit=False)
            prediction_obj.userid = user
 
            # ── Simulated CNN Prediction ──────────────────────
            # REPLACE this block with your actual model inference:
            #
            #   from tensorflow.keras.models import load_model
            #   model = load_model('path/to/lung_cancer_model.h5')
            #   img = Image.open(prediction_obj.xray_image).resize((224, 224))
            #   img_array = np.array(img) / 255.0
            #   img_array = np.expand_dims(img_array, axis=0)
            #   pred = model.predict(img_array)[0][0]
            #   label = "Cancer Detected" if pred > 0.5 else "Normal"
            #   confidence = float(pred) if pred > 0.5 else float(1 - pred)
            #
            # For now we use a keyword-based simulation:
            symptoms_text = (form.cleaned_data.get('symptoms') or '').lower()
            high_risk_keywords = ['cough', 'chest pain', 'blood', 'breathless', 'weight loss', 'fatigue']
            risk_score = sum(1 for kw in high_risk_keywords if kw in symptoms_text)
 
            if risk_score >= 3:
                label = "High Risk – Cancer Suspected"
                confidence = round(0.65 + risk_score * 0.04, 2)
            elif risk_score >= 1:
                label = "Moderate Risk – Further Tests Recommended"
                confidence = round(0.40 + risk_score * 0.05, 2)
            else:
                label = "Low Risk – Normal"
                confidence = round(0.85, 2)
 
            confidence = min(confidence, 0.99)
            prediction_obj.prediction = label
            prediction_obj.confidence = confidence
            prediction_obj.save()
            result = prediction_obj
 
    # Show last 5 predictions for this user
    past_predictions = AIPrediction.objects.filter(userid=user).order_by('-date')[:5]
 
    return render(request, 'ai_chatbot.html', {
        'form': form,
        'result': result,
        'past_predictions': past_predictions,
        'user': user,
    })
 
 
# ─────────────────────────────────────────────────────────────
#  AI DIET & HEALTH SUGGESTIONS
# ─────────────────────────────────────────────────────────────
 
def ai_diet_suggestions(request):
    """
    Provides personalized diet and health suggestions via Claude API.
    Uses rule-based logic as fallback if API key not set.
    """
    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'user':
        return redirect('loginpage')
 
    user = get_object_or_404(User, loginid=login_id)
 
    # Gather latest prescription/diagnosis for context
    latest_prescription = Prescription.objects.filter(
        appointment_id__userid=user
    ).order_by('-id').first()
 
    suggestions = None
 
    if request.method == 'POST':
        condition = request.POST.get('condition', '').strip()
        age = user.age
        suggestions = _generate_diet_suggestions(condition, age, latest_prescription)
 
    return render(request, 'ai_diet.html', {
        'user': user,
        'latest_prescription': latest_prescription,
        'suggestions': suggestions,
    })
 
 
def _generate_diet_suggestions(condition, age, prescription):
    """
    Rule-based diet suggestions.
    In production: call Claude API or GPT for personalized suggestions.
    """
    condition_lower = condition.lower()
    base = {
        'breakfast': [],
        'lunch': [],
        'dinner': [],
        'avoid': [],
        'tips': [],
    }
 
    if 'cancer' in condition_lower or 'lung' in condition_lower:
        base['breakfast'] = ['Oatmeal with berries', 'Green tea', 'Whole grain toast']
        base['lunch'] = ['Grilled fish with vegetables', 'Brown rice', 'Lentil soup']
        base['dinner'] = ['Steamed broccoli with tofu', 'Quinoa', 'Fresh fruit']
        base['avoid'] = ['Processed meats', 'Alcohol', 'Fried foods', 'Excess red meat']
        base['tips'] = [
            'Stay well hydrated (8–10 glasses of water daily)',
            'Include antioxidant-rich foods (berries, spinach, nuts)',
            'Small frequent meals help maintain energy levels',
            'Consult your oncologist before any dietary changes',
        ]
    elif 'diabetes' in condition_lower or 'sugar' in condition_lower:
        base['breakfast'] = ['Sprouts salad', 'Skimmed milk', 'Whole grain bread']
        base['lunch'] = ['Brown rice with dal', 'Mixed vegetable curry', 'Buttermilk']
        base['dinner'] = ['Chapati with sabzi', 'Grilled chicken / paneer', 'Salad']
        base['avoid'] = ['White rice', 'Sweets', 'Fruit juices', 'Refined flour products']
        base['tips'] = [
            'Eat at regular intervals to maintain blood sugar',
            'Choose low glycaemic index foods',
            'Exercise for at least 30 minutes daily',
        ]
    elif 'hypertension' in condition_lower or 'blood pressure' in condition_lower or 'bp' in condition_lower:
        base['breakfast'] = ['Banana', 'Low-fat yogurt', 'Oatmeal']
        base['lunch'] = ['Dal, vegetables, chapati', 'Salad', 'Buttermilk']
        base['dinner'] = ['Grilled fish / chicken', 'Steamed vegetables', 'Brown rice']
        base['avoid'] = ['High-salt snacks', 'Pickles', 'Processed cheese', 'Alcohol']
        base['tips'] = [
            'Limit sodium to less than 2300 mg per day',
            'Follow the DASH diet principles',
            'Avoid caffeine in excess',
        ]
    else:
        base['breakfast'] = ['Fresh fruits', 'Whole grain cereal', 'Low-fat milk']
        base['lunch'] = ['Balanced dal-rice-sabzi', 'Curd', 'Salad']
        base['dinner'] = ['Chapati with protein', 'Cooked vegetables', 'Soup']
        base['avoid'] = ['Junk food', 'Excessive sugar', 'Fried items']
        base['tips'] = [
            'Eat a rainbow of vegetables every day',
            'Stay hydrated',
            'Exercise regularly',
            'Get 7–8 hours of sleep',
        ]
 
    # Age-based adjustments
    if age and age > 60:
        base['tips'].append('Ensure adequate calcium and Vitamin D intake for bone health.')
        base['tips'].append('Prefer soft, easily digestible foods.')
    elif age and age < 18:
        base['tips'].append('Include calcium-rich foods for bone growth.')
 
    return base
 
 
# ─────────────────────────────────────────────────────────────
#  MEDICAL HISTORY
# ─────────────────────────────────────────────────────────────
 
def user_medical_history(request):
    """User views their complete medical history (past appointments + prescriptions)."""
    login_id = request.session.get('login_id')
    if not login_id or request.session.get('usertype') != 'user':
        return redirect('loginpage')
 
    user = get_object_or_404(User, loginid=login_id)
 
    # Completed appointments with prescriptions
    history_qs = Appointment.objects.select_related(
        'doctorid', 'doctorid__hospitalid'
    ).filter(
        userid=user,
        payment_status=1,
    ).order_by('-date', '-time')
 
    now = timezone.localtime()
    history = []
    for appt in history_qs:
        appt_dt = timezone.make_aware(datetime.combine(appt.date, appt.time))
        is_completed = appt.cancel_status == 0 and appt_dt < now
        is_cancelled = appt.cancel_status == 1
 
        rx = Prescription.objects.filter(appointment_id=appt).first()
        ai_pred = AIPrediction.objects.filter(userid=user).order_by('-date').first()
 
        history.append({
            'appointment': appt,
            'prescription': rx,
            'ai_prediction': ai_pred,
            'is_completed': is_completed,
            'is_cancelled': is_cancelled,
        })
 
    # AI predictions
    ai_predictions = AIPrediction.objects.filter(userid=user).order_by('-date')
 
    return render(request, 'user_medical_history.html', {
        'user': user,
        'patient_code': f"MT-{user.id:04d}",
        'history': history,
        'ai_predictions': ai_predictions,
    })
 