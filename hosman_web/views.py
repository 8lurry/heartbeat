from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from hosman_web.modules.storage import store_gContent
from .models import Patient
from editorial.models import Center
from .forms import *
from .views_profile import *


# Create your views here.

def get_profile_view(request):
    if request.user.is_authenticated:
        url = "../profile/" + request.user.username + "/"
        return HttpResponseRedirect(url)
    return HttpResponseRedirect("../login/")

def ThankYouView(request):
    return HttpResponse("<h1>THANK YOU</h1>")

class GContentView(FormView):
    form_class = GContentForm
    template_name = "hosman_web/g_content.html"
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            g_content = form.save(commit=False)
            media = request.FILES['content']
            g_content.content = media
            g_content = store_gContent(request.user.username, g_content)
            g_content.save()
            url = f"../accounts/profile/{request.user.username}/"
            return HttpResponseRedirect(url)
        return render(request, self.template_name, {'form': form})
    def get(self, request):
        if request.user.is_authenticated:
            context = self.get_context_data()
            context['form'].fields['belongs_to'].initial = Patient.objects.get(user=request.user.id)
            return self.render_to_response(context)
        return HttpResponse("Error 610")

class IndexView(TemplateView):
    template_name = 'hosman_web/index.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("home/")
        context = self.get_context_data(**kwargs)
        context['index'] = True
        return self.render_to_response(context)

class HomeView(TemplateView):
    template_name = 'hosman_web/home.html'