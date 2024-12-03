from django.urls import path

from oneid.views import get_oneid_token

urlpatterns = [
    path('get-oneid-token/', get_oneid_token, name='get-oneid-token'),
]

