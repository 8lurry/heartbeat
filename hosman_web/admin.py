from itertools import chain
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.forms import BaseInlineFormSet
from .models import User
from editorial.models import SiteManager, Hospital, Branch, Department, Center, MembershipRequest
from hosman_web.models import Address, Patient
from domains.models import Domain

# Register your models here.


class HospitalAdmin(admin.ModelAdmin):
    pass

class SiteManagerAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = self.model.objects.filter(patient__user__is_manager=True)
        ordering = self.get_ordering(request)
        if ordering:
            qs.order_by(*ordering)
        return qs

class MembershipRequestAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_selection_counter = True
    fields = ('request_for', 'site_manager')
    list_display = ['request_for', 'user']
    def user(self, obj):
        if obj.site_manager is not None:
            return obj.site_manager.patient.user.username
        elif obj.doctor is not None:
            return obj.doctor.patient.user.username
        elif obj.nurse is not None:
            return obj.nurse.patient.user.username
        elif obj.employee is not None:
            return obj.employee.patient.user.username
        else:
            return "Something went wrong!"
    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset()
        qs = qs.filter(
            Q(doctor__assigned_to__department__name="default") | 
            Q(nurse__assigned_to__department__name="default") |
            Q(employee__assigned_to__department__name="default") |
            Q(doctor=None, nurse=None, employee=None)
            )
        print(qs)
        ordering = self.get_ordering(request)
        if ordering:
            qs.order_by(*ordering)
        return qs
    def save_model(self, request, obj, form, change):
        save_method = True
        super().save_model(request, obj, form, change)
        if obj.site_manager is not None:
            obj.site_manager.patient.user.is_manager = True
            obj.site_manager.patient.user.save()
            if obj.site_manager.site.branch.name == 'default':
                pass
            elif obj.site_manager.site.site_manager == None:
                obj.site_manager.site.site_manager = obj.site_manager
                obj.site_manager.site.save()
            else:
                Center.objects.create(site_manager=obj.site_manager, branch=obj.site_manager.site.branch, department=obj.site_manager.site.department).save()
        self.delete_model(request, obj, save_method)
    def delete_model(self, request, obj, save_method=False):
        if not save_method:
            if obj.site_manager is not None:
                obj.site_manager.delete()
        super().delete_model(request, obj)

class CenterInlineFormset(BaseInlineFormSet):
    def is_valid(self):
        if not self.is_bound:
            return False
        forms_valid = True
        self.errors
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if self.can_delete:
                if self._should_delete_form(form):
                    continue
            try:
                if form.cleaned_data['department'] is not None:
                    try:
                        data = form.cleaned_data
                        try:
                            site_manager = data['site_manager']
                        except:
                            site_manager = None
                        center = form.save(commit=False)
                        try:
                            current_site_manager = SiteManager.objects.get(site=center.id)
                        except:
                            current_site_manager = None
                        if site_manager is not None:
                            if site_manager.site is None:
                                site_manager.site = center
                                site_manager.save()
                            elif site_manager.site.id == center.id:
                                pass
                            else:
                                recursive_manager = SiteManager.objects.create(patient=site_manager.patient, designation=site_manager.designation)
                                recursive_manager.site = center
                                recursive_manager.save()
                                form.cleaned_data['site_manager'] = recursive_manager
                        if current_site_manager is not None and site_manager is not None and current_site_manager.id != site_manager.id:
                            current_site_manager.site = None
                            current_site_manager.save()
                        if current_site_manager is not None and site_manager is None:
                            current_site_manager.site = None
                            current_site_manager.save()
                    except: pass
            except: pass
            forms_valid &= form.is_valid()
        return forms_valid and not self.non_form_errors()

class CenterInline(admin.StackedInline):
    model = Center
    extra = 1
    formset = CenterInlineFormset

class HCenter(admin.ModelAdmin):
    inlines = [CenterInline]
    def save_model(self, requst, obj, form, change):
        super().save_model(requst, obj, form, change)

class HCare(admin.AdminSite):
    site_title = "H-Care Admin Site"
    site_header = "H-Care Administration"
    def has_permission(self, request):
        return request.user.is_active and request.user.is_admin

class SuAdmin(UserAdmin):
    def email(self, obj):
        return Patient.objects.get(user=obj.id).email
    def first_name(self, obj):
        return Patient.objects.get(user=obj.id).first_name
    def last_name(self, obj):
        return Patient.objects.get(user=obj.id).last_name

hcare = HCare(name="hcare")

hcare.register(User, SuAdmin)
hcare.register(SiteManager, SiteManagerAdmin)

hcare.register(Address, admin.ModelAdmin)
hcare.register(Hospital, HospitalAdmin)
hcare.register(Department, admin.ModelAdmin)
hcare.register(Branch, HCenter)
hcare.register(MembershipRequest, MembershipRequestAdmin)
hcare.register(Domain, admin.ModelAdmin)