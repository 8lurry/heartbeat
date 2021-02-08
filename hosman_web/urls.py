from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from .views_profile import *
from .views_accounts import *
from .views_ajax import *
from .search import SearchView
from .admin import hcare

app_name = 'hosman_web'
urlpatterns = [
        path('su/', hcare.urls),
        #path('emergency/', EmergencyView.as_view(), name='emergency'),
        path('thanks/', ThankYouView),
        path('media/', GContentView.as_view()),
        #####################################################################################################################
        # ajax views
        #####################################################################################################################
        #path('emergency/', EmergencyView.as_view(), name='emergency'),
        path('get/search/', SearchView.as_view(), name='get-search'),
        #####################################################################################################################
        # ajax views
        #####################################################################################################################
        #path('emergency/', EmergencyView.as_view(), name='emergency'),
        path('ajax/validate_username/', validate_username, name='validate-username'),
        path('ajax/query_search/', query_search, name='query-search'),
        #####################################################################################################################
        # accounts views
        #####################################################################################################################
        #path('emergency/', EmergencyView.as_view(), name='emergency'),
        path('accounts/profile/<slug:slug>/', UserProfileView.as_view(), name='user-profile'),
        path('accounts/profile/', get_profile_view, name="get-profile"),
        path('accounts/signup/', UserCreationView.as_view(), name='sign-up'),
        path('accounts/profile/setup_wiz/update_info/', UpdateProfileView.as_view(), name='update-profile-info'),
        path('accounts/profile/setup_wiz/update_info/profile_picture/', ProfilePictureView.as_view(), name='add-profile-picture'),
        path('accounts/', include('django.contrib.auth.urls')),
        path('accounts/login/', CLoginView.as_view(), name='login'), # accounts/login/ [name='login']
        path('accounts/logout/', CLogoutView.as_view(), name='logout'), # accounts/logout/ [name='logout']
        #includes the following path
        # accounts/password_change/ [name='password_change']
        # accounts/password_change/done/ [name='password_change_done']
        # accounts/password_reset/ [name='password_reset']
        # accounts/password_reset/done/ [name='password_reset_done']
        # accounts/reset/<uidb64>/<token>/ [name='password_reset_confirm']
        # accounts/reset/done/ [name='password_reset_complete']
        path('', IndexView.as_view(), name='index'),
        path('home/', HomeView.as_view(), name='home'),
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
