from django.contrib import admin
from django.db.models import Q
# Register your models here.
from .models import (MembershipRequest, Specialization, SiteManager, Branch,
Doctor, Nurse, Employee, Reception, Schedule, ScheduleRequest, Token, HistoricalRecord)

def get_site(request):
    site_admin = SiteManager.objects.filter(patient__user__id=request.user.id)
    if site_admin.count() > 0:
        return site_admin[0].site.branch
    branch = Branch.objects.get(name="default")
    return branch

class MembershipRequestAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_selection_counter = True
    #fields = ('request_for', ('doctor', 'nurse',), ('employee', 'site_manager'))
    fieldsets = [
        (None, {'fields': ['request_for']}), 
        (None, {'classes': ('collapse'), 'fields': ('doctor', 'nurse','employee'),})
    ]
    list_display = ['request_for', 'user']
    def user(self, obj):
        if obj.doctor is not None:
            return obj.doctor.patient.user.username
        elif obj.nurse is not None:
            return obj.nurse.patient.user.username
        elif obj.employee is not None:
            return obj.employee.patient.user.username
        else:
            return "Something went wrong!"
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(
            Q(doctor__assigned_to__branch__name=get_site(request).name) |
            Q(nurse__assigned_to__branch__name=get_site(request).name) |
            Q(employee__assigned_to__branch__name=get_site(request).name)
            )
        ordering = self.get_ordering(request)
        if ordering:
            qs.order_by(*ordering)
        return qs
    def save_model(self, request, obj, form, change):
        save_method = True
        super().save_model(request, obj, form, change)
        if obj.doctor is not None:
            body = obj.doctor
        elif obj.nurse is not None:
            body = obj.nurse
        else:
            body = obj.employee
        body.patient.user.is_manager = True
        body.patient.user.save()
        self.delete_model(request, obj, save_method)
    def delete_model(self, request, obj, save_method=False):
        if not save_method:
            if obj.doctor is not None:
                obj.doctor.delete()
            if obj.nurse is not None:
                obj.nurse.delete()
            if obj.employee is not None:
                obj.employee.delete()
        super().delete_model(request, obj)

class BaseM(admin.ModelAdmin):
    list_display = ['__str__', 'user', 'assigned_to']
    def user(self, obj):
        return obj.patient.user.username
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(assigned_to__branch__name=get_site(request).name)
        ordering = self.get_ordering(request)
        if ordering:
            qs.order_by(*ordering)
        return qs

class ScheduleAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(center=request.site.id)
        sr = ScheduleRequest.objects.filter(schedule__center=request.site.id)
        for i in range(len(sr)):
            qs = qs.exclude(id=sr[i].schedule.id)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class ScheduleRequestAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model._default_manager.filter(schedule__center=request.site.id)
        qs = qs.exclude(request="R")
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
    def save_model(self, request, obj, form, change):
        save_method = True
        if obj.request == "C" and obj.approve == True:
            self.delete_model(request, obj, save_method=save_method)
        elif obj.request == "U" and obj.approve == True:
            #remove initial values
            sr = ScheduleRequest.objects.get(ref_id=obj.schedule.id)
            s = Schedule.objects.get(id=sr.schedule.id)
            s.delete()
            sr.delete()
            self.delete_model(request, obj, save_method=save_method)
        else:
            super().save_model(request, obj, form, change)
    def delete_model(self, request, obj, save_method=False):
        if obj.request == "C" and not save_method:
            sche = Schedule.objects.get(id=obj.schedule.id)
            sche.delete()
        if obj.request == "U" and not save_method:
            #retain initial values
            sr = ScheduleRequest.objects.get(ref_id=obj.schedule.id)
            sr.delete()
            sche = Schedule.objects.get(id=obj.schedule.id)
            sche.delete()
        super().delete_model(request, obj)

class Editorial(admin.AdminSite):
    site_header = 'H-Care Editorial'
    empty_value_display = "VACANT"

editorial = Editorial(name='editorial')

editorial.register(MembershipRequest, MembershipRequestAdmin)
editorial.register(Specialization, admin.ModelAdmin)
editorial.register(Doctor, BaseM)
editorial.register(Nurse, BaseM)
editorial.register(Employee, BaseM)
editorial.register(Reception, admin.ModelAdmin)
editorial.register(Schedule, ScheduleAdmin)
editorial.register(ScheduleRequest, ScheduleRequestAdmin)
editorial.register(Token, admin.ModelAdmin)
editorial.register(HistoricalRecord, admin.ModelAdmin)