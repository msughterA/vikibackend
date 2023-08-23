from django.urls import re_path
from . import views


urlpatterns = [re_path(r"", views.ChatView.as_view(), name="chat")]
