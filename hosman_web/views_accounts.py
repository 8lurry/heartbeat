from PIL import Image
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from .forms import CUserCreationForm, AddressForm, PatientForm
from .models import Patient, User
from .views import GContentView


class ProfilePictureView(GContentView):
    template_name = "registration/add_p_picture.html"
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            g_content = form.save(commit=False)
            pro_pic = request.FILES['content']
            patient_object = Patient.objects.get(user=request.user.id)
            try:
                img = Image.open(pro_pic)
                try:
                    img.verify()
                    g_content.content = pro_pic
                    g_content.save()
                    patient_object.profile_picture = g_content
                    patient_object.save()
                    url = "../../../" + request.user.username + "/"
                    return HttpResponseRedirect(url)
                except ValidationError as valError:
                    form.add_error('content', valError)
            except TypeError as tError:
                form.add_error('content', tError)
            return render(request, self.template_name, {'form': form})
    def get(self, request):
        if request.user.is_authenticated:
            context = self.get_context_data()
            patient_object = Patient.objects.get(user=request.user.id)
            context['form'].fields['belongs_to'].initial = patient_object
            return self.render_to_response(context)
        return HttpResponse("Error 403")

class CLoginView(LoginView):
    pass

class CLogoutView(LogoutView):
    pass

class UserCreationView(FormView):
    form_class = CUserCreationForm
    template_name = 'registration/sign_up.html'
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            pt = Patient.objects.create(user=user)
            pt.profile_picture = Patient.objects.get(user__username="default").profile_picture
            pt.save()
            return HttpResponseRedirect("../profile/setup_wiz/update_info/")
        return render(request, self.template_name, {'form': form})

class UpdateProfileView(TemplateView):
    patient_form_class = PatientForm
    address_form_class = AddressForm
    template_name = 'registration/update_profile.html'
    def post(self, request, *args, **kwargs):
        patient_form = self.patient_form_class(request.POST, instance=Patient.objects.get(user=request.user))
        if patient_form.instance.address:
            address_form = self.address_form_class(request.POST, instance=patient_form.instance.address)
        else:
            address_form = self.address_form_class(request.POST)
        if request.user.is_authenticated:
            if address_form.is_valid():
                address = address_form.save()
                if patient_form.is_valid():
                    patient = patient_form.save(commit=False)
                    patient.address = address
                    patient.save()
                    return HttpResponseRedirect('profile_picture/')
            return render(request, self.template_name, {'patient_form': patient_form, 'address_form': address_form})
        return HttpResponse("Error 610!")
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            patient_form = self.patient_form_class(instance=Patient.objects.get(user=request.user))
            context = self.get_context_data(patient_form=patient_form)
            print(dir(context['patient_form'].instance))
            print("="*70)
            if context['patient_form'].instance.address:
                context['address_form'] = self.address_form_class(instance=context['patient_form'].instance.address)
            else:
                context['address_form'] = self.address_form_class()
            return self.render_to_response(context)
        return HttpResponse("Error 610!")