import json
from django.contrib.postgres import search
from django.views.generic import ListView
from django.db.models import Case, When, Value, CharField
from django.http import HttpResponse
from editorial.models import DoctorHasSpecialization, Schedule, SearchString
from .models import Dummy

DAYS = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2 ,'Wednesday'),
    (3 ,'Thursday'),
    (4 ,'Friday'),
    (5 ,'Saturday'),
    (6 ,'Sunday')
]

def search_doctor(query):
    s_vec_doc = search.SearchVector(
        'doctor__patient__user__username',
        'doctor__patient__first_name',
        'doctor__patient__last_name',
        'doctor__assigned_to__building_name',
        'doctor__assigned_to__description',
        'doctor__assigned_to__department__name',
        'specialization__name',
        'specialization__category',
        )
    s_que = search.SearchQuery(query, search_type='websearch')
    s_rank = search.SearchRank(s_vec_doc, s_que)
    return DoctorHasSpecialization.objects.annotate(rank=s_rank).filter(rank__gte=0.01).order_by('-rank')

def search_schedule(query):
    s_vec = search.SearchVector(
        'doctor__patient__user__username',
        'doctor__patient__first_name',
        'doctor__patient__last_name',
        'doctor__assigned_to__building_name',
        'doctor__assigned_to__description',
        'doctor__assigned_to__department__name',
        ) + search.SearchVector(
            Case(
                *[When(day_of_week=d, then=Value(v)) for d, v in DAYS],
                default=Value(''),
                output_field=CharField()
            )
        )
    s_que = search.SearchQuery(query, search_type='websearch')
    s_rank = search.SearchRank(s_vec, s_que)
    qs = Schedule.objects.annotate(rank=s_rank)
    aug_vec = search.SearchVector('specialization__name', 'specialization__category')
    aug_que = search.SearchQuery(query, search_type='websearch')
    aug_rank = search.SearchRank(aug_vec, aug_que)
    aug_qs = DoctorHasSpecialization.objects.annotate(rank=aug_rank)
    for aug_q in aug_qs:
        com = qs.filter(doctor=aug_q.doctor)
        if com.count() > 0:
            for i, _ in enumerate(com):
                qs.exclude(doctor=com[i].doctor)
                com[i].rank += aug_q.rank
            qs.union(com)
    return qs.filter(rank__gte=0.01).order_by('-rank')[:20]

def search_facility(query):
    return []

def q_suggest(request):
    query = request.GET.get('search')
    doctor = json.loads(request.GET.get('doctor'))
    schedule = json.loads(request.GET.get('schedule'))
    facility = json.loads(request.GET.get('facility'))
    return SearchString.objects.filter(doctor=doctor, schedule=schedule, facility=facility)\
        .annotate(rank=search.SearchRank(search.SearchVector('string'), \
            search.SearchQuery(query, search_type='websearch'))).order_by('-rank')[:12]

class SearchView(ListView):
    template_name = "hosman_web/search.html"
    paginate_by = 10
    def get(self, request, *args, **kwargs):
        query = request.GET.get('search')
        doctor = request.GET.get('doctor') == 'doctor'
        schedule = request.GET.get('schedule') == 'schedule'
        facility = request.GET.get('facility') == 'facility'
        try:
            srch_str = SearchString.objects.get(string=query, doctor=doctor, schedule=schedule, facility=facility)
            srch_str.save() #save method increments the search ranking by 1
        except SearchString.DoesNotExist:
            SearchString.objects.create(string=query, doctor=doctor, schedule=schedule, facility=facility)
        qs = []
        if doctor:
            qs += [(q, q.rank) for q in search_doctor(query)]
        if schedule:
            qs += [(q, q.rank) for q in search_schedule(query)]
        if facility:
            pass
        def second(val):
            return val[1]
        qs.sort(key=second, reverse=True)
        self.object_list = [q for q, _ in qs]
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            pass
        return HttpResponse("ok")