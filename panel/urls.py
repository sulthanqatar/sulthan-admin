from django.urls import path

from panel import views

app_name = "panel"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("categories/", views.category_list, name="categories"),
    path("categories/new/", views.category_edit, name="category_new"),
    path("categories/<int:pk>/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("products/", views.product_list, name="products"),
    path("products/new/", views.product_edit, name="product_new"),
    path("products/<int:pk>/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:pk>/status/", views.order_status, name="order_status"),
    path("customers/", views.customer_list, name="customers"),
    path("customers/new/", views.customer_edit, name="customer_new"),
    path("customers/<int:pk>/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/toggle/", views.customer_toggle, name="customer_toggle"),
    path("users/", views.user_list, name="users"),
    path("users/new/", views.user_edit, name="user_new"),
    path("users/<int:pk>/", views.user_edit, name="user_edit"),
    path("users/<int:pk>/toggle/", views.user_toggle, name="user_toggle"),
    path("b2b/", views.b2b_list, name="b2b"),
    path("b2b/<int:pk>/status/", views.b2b_status, name="b2b_status"),
    path("banners/", views.banner_list, name="banners"),
    path("banners/new/", views.banner_edit, name="banner_new"),
    path("banners/<int:pk>/", views.banner_edit, name="banner_edit"),
    path("banners/<int:pk>/delete/", views.banner_delete, name="banner_delete"),
    path("coupons/", views.coupon_list, name="coupons"),
    path("coupons/new/", views.coupon_edit, name="coupon_new"),
    path("coupons/<int:pk>/", views.coupon_edit, name="coupon_edit"),
    path("coupons/<int:pk>/delete/", views.coupon_delete, name="coupon_delete"),
    path("audit/", views.audit_list, name="audit"),
]
