from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from .models import *
from .forms import *



class UserProfileView(DetailView):
    model = User
    slug_field = 'username'
    def get_context_data(self, *args, **kwargs):
        context = super(UserProfileView, self).get_context_data(*args, **kwargs)
        patient = Patient.objects.get(user=self.object.id)
        context['patient'] = patient
        context['picture'] = patient.profile_picture.content
        try:
            record_objs = HistoricalRecord.objects.get(patient=self.object.id)
            context['timeline'] = record_objs
        except:
            context['timeline'] = 'You have no hospital record yet!'
        return context
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.object = self.get_object()
            if request.user.username != self.object.username:
                return HttpResponse("Error 610!")
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        return HttpResponse("Error 610!")