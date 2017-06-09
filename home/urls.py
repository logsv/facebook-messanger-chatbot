from django.conf.urls import url

from home import views


urlpatterns = (
    url(r'^66f5ad62249a4339ee1ae9b1e3ee2f33f6bf50aaa8fac061fd/$', views.MessangerBot.as_view(), name='messenger_webhook'),
)
