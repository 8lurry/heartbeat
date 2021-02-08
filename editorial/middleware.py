from django.utils.deprecation import MiddlewareMixin
from .models import Center, Doctor, Nurse, Employee, SiteManager

class CurrentSiteMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            request.privilege = None
            user = request.user
            if hasattr(user, 'is_manager') and user.is_manager:
                try: 
                    who = Doctor.objects.get(patient__user=user.id)
                    request.privilege = ["doctor"]
                except: pass
                try: 
                    who = Nurse.objects.get(patient__user=user.id)
                    request.privilege = ["nurse"]
                except: pass
                try: 
                    who = Employee.objects.get(patient__user=user.id)
                    request.privilege = ["employee"]
                except: pass
                try:
                    request.site = who.assigned_to
                    request.profile_picture = [who.patient.profile_picture.content.url]
                except: pass 
                who = SiteManager.objects.filter(patient__user=user.id)
                if who.count() > 0:
                    request.privilege = ["admin"]
                    request.site = who[0].site
                    request.profile_picture = [who[0].patient.profile_picture.content.url]
            if request.privilege is None:
                request.privilege = ["default"]
                request.site = Center.objects.get(branch__name='default')
                request.profile_picture = ['/static/hosman_web/gContent/imgs/default_avatar.jpg']
        except: pass