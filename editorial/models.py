from django.db import models
from django.utils.translation import gettext_lazy as _
from .storage import fs
from hosman_web.models import Patient, Address
from domains.models import Domain

# Create your models here.

class SearchString(models.Model):
    string = models.CharField(max_length=500)
    doctor = models.BooleanField(default=False)
    schedule = models.BooleanField(default=False)
    facility = models.BooleanField(default=False)
    q_count = models.IntegerField(default=-1)
    def save(self, *args, **kwargs):
        self.q_count += 1
        super(SearchString, self).save(*args, **kwargs)

class BinTray(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    bin_text = models.CharField(max_length=100)
    bin_detail = models.CharField(max_length=500, null=True, blank=True)
    bin_item = models.CharField(max_length=500)

class ScheduleRequest(models.Model):
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE)
    made_by = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    class CreateUpdate(models.TextChoices):
        CREATE = 'C', _('Create')
        UPDATE = 'U', _("Update")
        RETAINED = "R", ("Retained")
    request = models.CharField(max_length=1, choices=CreateUpdate.choices, default=CreateUpdate.CREATE)
    approve = models.BooleanField(default=False)
    ref_id = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.schedule.__str__()

class MembershipRequest(models.Model):
    class Membership(models.TextChoices):
        SITEMANAGER = "SM", _('Site Manager')
        SITEEMPLOYEE = "SE", _('General Employee')
        DOCTOR = "DR", _('Doctor')
        NURSE = "NS", _('Nurse')
    request_for = models.CharField(max_length=2, choices=Membership.choices, default=Membership.DOCTOR)
    doctor = models.OneToOneField("Doctor", on_delete=models.SET_NULL, null=True, blank=True)
    nurse = models.OneToOneField("Nurse", on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.OneToOneField("Employee", on_delete=models.SET_NULL, null=True, blank=True)
    site_manager = models.OneToOneField("SiteManager", on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        if self.doctor is not None:
            username = self.doctor.patient.user.username
            r_for = "Doctor"
        elif self.nurse is not None:
            username = self.nurse.patient.user.username
            r_for = "Nurse"
        elif self.employee is not None:
            username = self.employee.patient.user.username
            r_for = "Site Employee"
        elif self.site_manager is not None:
            username = self.site_manager.patient.user.username
            r_for = "Site Manager"
        else:
            return "Something really went wrong!"
        return "Membership Request for " + r_for + " from " + username

class SiteManager(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    class Designation(models.TextChoices):
        SITEADMIN = "SA", _("Site Administrator")
        SITEMANAGER = "SM", _("Site Manager")
        SITETECHIE = "ST", _("Site Techie")
    designation = models.CharField(max_length=2, choices=Designation.choices, default=Designation.SITEADMIN)
    site = models.ForeignKey('Center', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.patient.user.__str__()

class Hospital(models.Model):
    name = models.CharField(max_length=300)
    identifier = models.CharField(max_length=128, unique=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
class Department(models.Model):
    class DepartmentChoices(models.TextChoices):
        VISIT = "Visiting Center"
        WARD = "Ward Center"
        EMERGENGY = "Emergergy Center"
        SURGERY = "Surgical Center"
        DIAGNOSTIC = "Diagnostic Center"
        DEFAULT = "default"
    name = models.CharField(max_length=20, choices=DepartmentChoices.choices)
    def __str__(self):
        return self.name

class Branch(models.Model):
    name = models.CharField(max_length=80, unique=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
        )
    email = models.EmailField(
        max_length=250,
        null=True,
        blank=True
        )
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE
        )
    def __str__(self):
        return self.hospital.name + '; ' + self.address.__str__()

class Center(models.Model):
    building_name = models.CharField(max_length=180, null=True, blank=True)
    site_manager = models.ForeignKey('SiteManager', on_delete=models.SET_NULL, null=True, blank=True,)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.CharField(max_length=400, null=True, blank=True, editable=False)
    def __str__(self):
        return self.description
    def save(self, *args, **kwargs):
        self.description = self.branch.hospital.name+' ('+self.department.name+'); '+ self.branch.address.__str__()
        super(Center, self).save(*args, **kwargs)

class Doctor(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('Center', on_delete=models.SET_NULL, null=True, blank=True)
    specializations = models.ManyToManyField('Specialization')
    def __str__(self):
        return self.patient.__str__()

class Nurse(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('Center', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.patient.__str__()

class Employee(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    class EDesignation(models.TextChoices):
        OTHER = 'OR', _('Other')
        MANAGER = 'MR', _('Manager')
        RECEPTIONIST = 'RT', _('Receptionist')
    designation = models.CharField(max_length=2, choices=EDesignation.choices, default=EDesignation.OTHER)
    assigned_to = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.patient.__str__()

class Specialization(models.Model):
    category = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    class SpecClass(models.IntegerChoices):
        DOCTOR = 1
        NURSE = 0
    class_doctor = models.IntegerField(choices=SpecClass.choices, default=SpecClass.DOCTOR)
    def __str__(self):
        return self.name

class HistoricalRecord(models.Model):
    date = models.DateField()
    receipt_no = models.CharField(max_length=50, null=True, blank=True)
    class TypeTest(models.IntegerChoices):
        TEST = 1, _('Test')
        PRESCRIPTION = 0, _('Prescription')
    type_test = models.IntegerField(choices=TypeTest.choices, default=TypeTest.PRESCRIPTION)
    content = models.FileField(storage=fs)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.SET_NULL, null=True, blank=True)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.receipt_no

class PickDay(models.IntegerChoices):
    MONDAY = 0, _('Monday')
    TUESDAY = 1, _('Tuesday')
    WEDNESDAY = 2, _('Wednesday')
    THURSDAY = 3, _('Thursday')
    FRIDAY = 4, _('Friday')
    SATURDAY = 5, _('Saturday')
    SUNDAY = 6, _('Sunday')

class Schedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=PickDay.choices)
    office_no = models.CharField(max_length=6)
    phone = models.CharField(max_length=20)
    fee_1st = models.CharField(max_length=6)
    fee_revisit = models.CharField(max_length=6)
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.get_day_of_week_display()}: office#{self.office_no} @{self.start_time}"
    def get_absolute_url(self):
        return "%i/" % self.id

class Token(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField()
    tokenie_logged = models.BooleanField(default=False)
    serial = models.CharField(max_length=5)
    revisit = models.BooleanField(default=False)
    patient_name = models.CharField(max_length=50)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return str(self.serial)
    def get_absolute_url(self):
        return "%i/" % self.id

class AppointmentHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    datetime = models.DateTimeField()

class Reception(models.Model):
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    floor_no = models.CharField(max_length=20, null=True, blank=True)
    office_no = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=False)

class Test(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.name

class Service(models.Model):
    beds_no = models.CharField(max_length=4)
    name = models.CharField(max_length=20)
    category = models.CharField(max_length=20)
    visiting_hour = models.TimeField()
    visit_duration = models.DurationField()
    center = models.ForeignKey(
        Center,
        on_delete=models.CASCADE
        )
    def __str__(self):
        return self.name

class Bed(models.Model):
    bed_no = models.CharField(max_length=8)
    room_no = models.CharField(max_length=8)
    floor_no = models.CharField(max_length=8)
    fee = models.CharField(max_length=8)
    class Occupied(models.IntegerChoices):
        OCCUPIED = 1
        VACANT = 0
    occupied = models.IntegerField(choices=Occupied.choices)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
        )
    def __str__(self):
        return self.bed_no + "/" + self.room_no + "/" +self.floor_no

class Surgery(models.Model):
    building_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    def __str__(self):
        return self.center.__str__()

class Facility(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=400, null=True, blank=True)
    def __str__(self):
        return self.name

class Emergency(models.Model):
    building_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    receptionist = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    center = models.ForeignKey(Center, on_delete=models.CASCADE)
    def __str__(self):
        return self.center.__str__()

class DoctorHasSpecialization(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE)

class SurgeryHasFacility(models.Model):
    surgery = models.ForeignKey(Surgery, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)

class EmergencyHasFacility(models.Model):
    emergency = models.ForeignKey(Emergency, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)

class DoctorAtOT(models.Model):
    ot = models.ForeignKey(SurgeryHasFacility, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)

class NurseAtOT(models.Model):
    ot = models.ForeignKey(SurgeryHasFacility, on_delete=models.CASCADE)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)

class DoctorAtService(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=PickDay.choices)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

class NurseAtService(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=PickDay.choices)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)

class DoctorAtEmergency(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=PickDay.choices)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    ot = models.ForeignKey(EmergencyHasFacility, on_delete=models.CASCADE)

class NurseAtEmergency(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.IntegerField(choices=PickDay.choices)
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE)
    ot = models.ForeignKey(EmergencyHasFacility, on_delete=models.CASCADE)