from django.urls import path

from . import views

urlpatterns = [
    path('sqli/', views.sqli_demo, name='sqli-demo'),
    path('blind-sqli/', views.blind_sqli_demo, name='blind-sqli-demo'),
    path('stored-xss/', views.stored_xss_demo, name='stored-xss-demo'),
    path('reflected-xss/', views.reflected_xss_demo, name='reflected-xss-demo'),
    path('ssrf/', views.ssrf_demo, name='ssrf-demo'),
    path('files/', views.path_traversal_demo, name='path-traversal-demo'),
    path('command-injection/', views.command_injection_demo, name='command-injection-demo'),
    path('deserialization/', views.deserialization_demo, name='deserialization-demo'),
]