"""
URL configuration for demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from wildewidgets import WildewidgetDispatch

from demo.core.views import DemoPageView

urlpatterns = [
    path('', DemoPageView.as_view(), name='home'),
    path(
        'components/',
        DemoPageView.as_view(
            page_key='components',
            menu_item='Components',
            help_page_id='topics/pages',
        ),
        name='components',
    ),
    path(
        'workflow/',
        DemoPageView.as_view(
            page_key='workflow',
            menu_item='Workflow',
            help_book_slug='developer',
            help_page_id='authoring/pages',
        ),
        name='workflow',
    ),
    path(
        'status/',
        DemoPageView.as_view(
            page_key='status',
            menu_item='Status',
            help_book_slug='admin',
            help_page_id='admin/validation',
        ),
        name='status',
    ),
    path('wildewidgets_json', WildewidgetDispatch.as_view(), name='wildewidgets_json'),
    path('admin/', admin.site.urls),
]
