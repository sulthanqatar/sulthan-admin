"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from config.admin_site import patch_admin
from config import portals

patch_admin()

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('staff/login/', portals.login, {'role': 'staff'}, name='staff_login'),
    path('staff/logout/', portals.logout, {'role': 'staff'}, name='staff_logout'),
    path('staff/', portals.staff_orders, name='staff_orders'),
    path('staff/orders/<str:order_id>/status/', portals.staff_order_status, name='staff_order_status'),
    path('staff/products/', portals.staff_products, name='staff_products'),
    path('staff/products/<str:product_id>/stock/', portals.staff_stock, name='staff_stock'),
    path('warehouse/login/', portals.login, {'role': 'warehouse'}, name='warehouse_login'),
    path('warehouse/logout/', portals.logout, {'role': 'warehouse'}, name='warehouse_logout'),
    path('warehouse/', portals.warehouse_home, name='warehouse_home'),
    path('warehouse/stock/', portals.warehouse_stock, name='warehouse_stock'),
    path('delivery/login/', portals.login, {'role': 'delivery'}, name='delivery_login'),
    path('delivery/logout/', portals.logout, {'role': 'delivery'}, name='delivery_logout'),
    path('delivery/', portals.delivery_home, name='delivery_home'),
    path('delivery/orders/<str:order_id>/status/', portals.delivery_status, name='delivery_status'),
    path('admin/', include('panel.urls')),
    path('superadmin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
