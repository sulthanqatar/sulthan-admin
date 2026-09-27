from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User


class StudioAdminSite(admin.AdminSite):
    site_header = "Sulthan Admin"
    site_title = "Sulthan Admin"
    index_title = "Overview"
    site_url = "/"
    enable_nav_sidebar = True

    def each_context(self, request):
        context = super().each_context(request)
        context["brand_name"] = "Sulthan"
        context["brand_tagline"] = "Admin"
        return context

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            {
                "stat_users": User.objects.count(),
                "stat_staff": User.objects.filter(is_staff=True).count(),
                "stat_groups": Group.objects.count(),
                "stat_actions": LogEntry.objects.count(),
            }
        )
        return super().index(request, extra_context)


class StudioUserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    list_per_page = 25
    show_facets = admin.ShowFacets.ALLOW


def patch_admin():
    admin.site.__class__ = StudioAdminSite
    admin.site.site_header = "Sulthan Admin"
    admin.site.site_title = "Sulthan Admin"
    admin.site.index_title = "Overview"
    if admin.site.is_registered(User):
        admin.site.unregister(User)
    admin.site.register(User, StudioUserAdmin)
