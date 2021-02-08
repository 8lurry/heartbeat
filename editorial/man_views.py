import datetime
from django.views.generic.edit import FormView
from django.views.generic import ListView, CreateView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import render
from .storage import fs
from .man_forms import *
from .models import ScheduleRequest, Schedule, Token, AppointmentHistory
from hosman_web.models import Patient
from hosman_web.modules.storage import store_gContent

class HistoricalRecordCreateView(CreateView):
    form_class = HistoricalRecordForm
    template_name = 'site/edit/record_keep.html'
    def get(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        i = int(request.path.split('/')[5])
        token = Token.objects.get(id=i)
        context['form'].fields['date'].initial = token.date
        context['form'].fields['doctor'].initial = token.schedule.doctor
        context['form'].fields['patient'].initial = token.patient
        context['form'].fields['center'].initial = request.site
        return self.render_to_response(context)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            media = request.FILES['content']
            obj.content = media
            print(fs.location)
            print("="*80)
            obj = store_gContent(obj.patient.user.username, obj, location=fs.location+'/')
            obj.save()
            url = f"../../../../../update/{Token.objects.get(id=int(request.path.split('/')[5])).schedule.id}/token/"
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})

class TokenView(ListView):
    model = Token
    template_name = 'site/token.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager:
            self.object_list = self.model._default_manager.filter(schedule=int(request.path.replace('/', ' ').split()[3]))
            allow_empty = self.get_allow_empty()
            if not allow_empty:
                if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = not self.object_list
                if is_empty:
                    raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                        'class_name': self.__class__.__name__,
                    })
            context = self.get_context_data()
            return self.render_to_response(context)
        return HttpResponse('Error 610!')

class TokenCreateView(CreateView):
    form_class = TokenForm
    template_name = 'site/edit/token.html'
    success_url = "../"
    def get(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data()
        i = int(request.path.replace('/', ' ').split()[3])
        schedule = Schedule.objects.get(id=i)
        serial = Token.objects.filter(schedule=schedule.id).count()
        day = datetime.date.today()
        wd = day.weekday()
        timedelta = schedule.day_of_week - wd if schedule.day_of_week > wd else schedule.day_of_week + 7 - wd if schedule.day_of_week < wd else 0
        day += datetime.timedelta(days=timedelta)
        context['form'].fields['schedule'].initial = schedule
        context['form'].fields['date'].initial = day
        context['form'].fields['serial'].initial = serial + 1
        if request.user.is_authenticated:
            patient = Patient.objects.get(user=request.user.id)
            revisit = AppointmentHistory.objects.filter(patient=patient.id, doctor=schedule.doctor.id, center=schedule.center.id).count() > 0
            context['form'].fields['tokenie_logged'].initial = True
            context['form'].fields['revisit'].initial = revisit
            context['form'].fields['patient_name'].initial = patient.__str__()
            context['form'].fields['patient'].initial = patient
        else:
            context['form'].fields['patient'].initial = request.user
        return self.render_to_response(context)

class ScheduleCreateView(CreateView):
    form_class = ScheduleForm
    template_name = 'site/edit/schedule.html'
    success_url = '../'
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            obj = form.save()
            sr = ScheduleRequest.objects.create(schedule=obj, made_by=Patient.objects.get(user=request.user.id), request="C")
            sr.save()
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager:
            self.object = None
            context = self.get_context_data()
            context['form'].fields['center'].initial = request.site
            if request.privilege == 'employee':
                context['form'].fields['receptionist'].initial = request.user
            elif request.privilege == 'doctor':
                context['form'].fields['doctor'].initial = request.user
            super().get(request, *args, **kwargs)
            return self.render_to_response(context)
        return HttpResponse("Error 610")

class ScheduleView(ListView):
    model = Schedule
    template_name = 'site/schedule.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager:
            self.object_list = self.model._default_manager.filter(center=request.site.id)
            srs = ScheduleRequest.objects.filter(schedule__center=request.site.id)
            for i, _ in enumerate(srs):
                self.object_list = self.object_list.exclude(id=srs[i].schedule.id)
            allow_empty = self.get_allow_empty()
            if not allow_empty:
                if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = not self.object_list
                if is_empty:
                    raise Http404(_('Empty list and “%(class_name)s.allow_empty” is False.') % {
                        'class_name': self.__class__.__name__,
                    })
            context = self.get_context_data()
            return self.render_to_response(context)
        return HttpResponse('Error 610!')

class ScheduleUpdateView(UpdateView):
    model = Schedule
    form_class = ScheduleForm
    template_name = 'site/edit/schedule.html'
    success_url = "../../"
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            retain_old = self.get_object()
            sr_test = ScheduleRequest.objects.filter(schedule__center=retain_old.center.id, schedule__office_no=retain_old.office_no, request="R")
            obj = form.save()
            if sr_test.count() == 0:
                dup_old = Schedule.objects.create(
                    start_time=retain_old.start_time, 
                    end_time=retain_old.end_time,
                    day_of_week=retain_old.day_of_week,
                    office_no=retain_old.office_no,
                    phone=retain_old.phone,
                    fee_1st=retain_old.fee_1st,
                    fee_revisit=retain_old.fee_revisit,
                    receptionist=retain_old.receptionist,
                    doctor=retain_old.doctor,
                    center=retain_old.center
                    )
                dup_old.save()
                sr_ret = ScheduleRequest.objects.create(schedule=dup_old, made_by=Patient.objects.get(user=request.user.id), request="R", ref_id=obj.id)
                sr_ret.save()
            else:
                sr_test[0].made_by = Patient.objects.get(user=request.user.id)
                sr_test[0].ref_id = obj.id
                sr_test[0].save()
                if sr_test.count() > 1:
                    for i in range(1, len(sr_test)):
                        sr_test[i].delete()
            retain_old.delete()
            sr = ScheduleRequest.objects.create(schedule=obj, made_by=Patient.objects.get(user=request.user.id), request="U")
            sr.save()
            return HttpResponseRedirect(self.success_url)
        return render(request, self.template_name, {'form': form})
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_manager:
            self.object = self.get_object()
            return super().get(request, *args, **kwargs)
        return HttpResponse("Error 610!")