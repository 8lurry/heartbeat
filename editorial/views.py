from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import *
from hosman_web.models import Patient
from .models import Center
# Create your views here.

class SiteLoginView(LoginView):
    pass

class AdminLoginView(LoginView):
    pass

class DoctorView(FormView):
    form_class = DoctorForm
    template_name = "request/doctor.html"
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            doctor = form.save()
            re_mem = MembershipRequest.objects.create(request_for=MembershipRequest.Membership.DOCTOR, doctor=doctor)
            re_mem.save()
            return HttpResponseRedirect("../../../thanks/")
        return render(request, self.template_name, {'form': form})
    def get(self, request):
        if request.user.is_authenticated:
            context = self.get_context_data()
            patient_object = Patient.objects.get(user=request.user.id)
            default_center = Center.objects.filter(department__name="default")
            context['form'].fields['assigned_to'].initial = default_center[0]
            context['form'].fields['patient'].initial = patient_object
            return self.render_to_response(context)
        return HttpResponseRedirect("../../../accounts/login/")

class NurseView(DoctorView):
    form_class = NurseForm
    template_name = "request/nurse.html"
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            nurse = form.save()
            re_mem = MembershipRequest.objects.create(request_for=MembershipRequest.Membership.NURSE, nurse=nurse)
            re_mem.save()
            return HttpResponseRedirect("../../../thanks/")
        return render(request, self.template_name, {'form': form})

class EmployeeView(DoctorView):
    form_class = EmployeeForm
    template_name = "request/employee.html"
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            employee = form.save()
            re_mem = MembershipRequest.objects.create(request_for=MembershipRequest.Membership.SITEEMPLOYEE, employee=employee)
            re_mem.save()
            return HttpResponseRedirect("../../../thanks/")
        return render(request, self.template_name, {'form': form})

class SiteManagerView(FormView):
    form_class = SiteManagerForm
    template_name = "request/site_manager.html"
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            site_manager = form.save()
            re_mem = MembershipRequest.objects.create(request_for=MembershipRequest.Membership.SITEMANAGER, site_manager=site_manager)
            re_mem.save()
            return HttpResponseRedirect("../../../thanks/")
        return render(request, self.template_name, {'form': form})
    def get(self, request):
        if request.user.is_authenticated:
            context = self.get_context_data()
            patient_object = Patient.objects.get(user=request.user.id)
            context['form'].fields['patient'].initial = patient_object
            return self.render_to_response(context)
        return HttpResponseRedirect("../../../accounts/login/")