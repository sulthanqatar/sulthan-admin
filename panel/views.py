import hmac
from functools import wraps

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from config.portals import DEMO_PASSWORD, DEMO_USERNAME
from panel.forms import (
    BannerForm,
    CouponForm,
    CustomerForm,
    InternalUserForm,
    ProductCategoryForm,
    ProductForm,
)
from panel.models import (
    AuditTrail,
    B2BRegistration,
    Banner,
    Coupon,
    Customer,
    InternalUser,
    Order,
    Product,
    ProductCategory,
    ProductImage,
)


def audit(request, action, target):
    AuditTrail.objects.create(
        actor=request.session.get("admin_username") or DEMO_USERNAME,
        action=action,
        target=target[:240],
    )


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("panel_admin"):
            return redirect("panel:login")
        return view(request, *args, **kwargs)

    return wrapper


def _same(left, right):
    return hmac.compare_digest(left.encode(), right.encode())


@require_http_methods(["GET", "POST"])
def login(request):
    if request.session.get("panel_admin"):
        return redirect("panel:dashboard")
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        if _same(username, DEMO_USERNAME) and _same(password, DEMO_PASSWORD):
            request.session["panel_admin"] = True
            request.session["admin_username"] = DEMO_USERNAME
            audit(request, "Signed in", "Admin panel")
            return redirect("panel:dashboard")
        error = "Those credentials are not valid."
    return render(
        request,
        "portals/login.html",
        {
            "portal": {
                "title": "Admin",
                "lede": "Run the store: products, orders, customers, banners, and coupons.",
            },
            "error": error,
        },
    )


@require_POST
def logout(request):
    if request.session.get("panel_admin"):
        audit(request, "Signed out", "Admin panel")
    request.session.pop("panel_admin", None)
    request.session.pop("admin_username", None)
    return redirect("panel:login")


@admin_required
def dashboard(request):
    ranked = (
        Product.objects.annotate(units=Sum("order_lines__quantity"))
        .filter(units__gt=0)
        .order_by("-units", "name")
        .first()
    )
    return render(
        request,
        "panel/dashboard.html",
        {
            "section": "dashboard",
            "order_count": Order.objects.count(),
            "customer_count": Customer.objects.count(),
            "b2b_count": B2BRegistration.objects.filter(
                status=B2BRegistration.STATUS_ACCEPTED
            ).count(),
            "most_ordered": ranked,
            "recent_orders": Order.objects.select_related("customer").order_by("-created_at")[:10],
        },
    )


def _save_form(request, form, action, label):
    saved = form.save()
    audit(request, action, f"{label}: {saved}")
    messages.success(request, f"{saved} saved.")
    return saved


@admin_required
@require_http_methods(["GET", "POST"])
def category_edit(request, pk=None):
    category = get_object_or_404(ProductCategory, pk=pk) if pk else None
    form = ProductCategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        _save_form(
            request,
            form,
            "Updated category" if category else "Created category",
            "Category",
        )
        return redirect("panel:categories")
    return render(
        request,
        "panel/form.html",
        {
            "section": "categories",
            "heading": "Edit category" if category else "New category",
            "form": form,
            "cancel_url_name": "panel:categories",
        },
    )


@admin_required
def category_list(request):
    return render(
        request,
        "panel/category_list.html",
        {
            "section": "categories",
            "categories": ProductCategory.objects.annotate(product_count=Count("products")).order_by("-created_at"),
        },
    )


@admin_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(ProductCategory, pk=pk)
    if category.products.exists():
        messages.error(request, "Move or delete this category’s products before deleting it.")
        return redirect("panel:categories")
    name = category.name
    category.delete()
    audit(request, "Deleted category", f"Category: {name}")
    messages.success(request, f"{name} deleted.")
    return redirect("panel:categories")


def _store_images(request, product):
    for image_id in request.POST.getlist("delete_image"):
        image = product.images.filter(pk=image_id).first()
        if image:
            image.delete()
            audit(request, "Removed image", f"Product: {product.name}")
    for upload in request.FILES.getlist("images"):
        image = ProductImage(product=product, image=upload, alt=product.name)
        try:
            image.full_clean()
        except ValidationError:
            messages.error(request, f"{upload.name} is not a valid image.")
            continue
        image.save()
        audit(request, "Uploaded image", f"Product: {product.name}")


@admin_required
@require_http_methods(["GET", "POST"])
def product_edit(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk else None
    form = ProductForm(request.POST or None, instance=product)
    if request.method == "POST" and form.is_valid():
        saved = _save_form(
            request,
            form,
            "Updated product" if product else "Created product",
            "Product",
        )
        _store_images(request, saved)
        return redirect("panel:products")
    return render(
        request,
        "panel/product_form.html",
        {
            "section": "products",
            "heading": "Edit product" if product else "New product",
            "form": form,
            "product": product,
        },
    )


@admin_required
def product_list(request):
    products = (
        Product.objects.select_related("category")
        .annotate(image_count=Count("images"))
        .order_by("-created_at")
    )
    return render(request, "panel/product_list.html", {"section": "products", "products": products})


@admin_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.order_lines.exists():
        messages.error(request, "This product is on an order, so it stays in the catalog.")
        return redirect("panel:products")
    name = product.name
    for image in product.images.all():
        image.delete()
    product.delete()
    audit(request, "Deleted product", f"Product: {name}")
    messages.success(request, f"{name} deleted.")
    return redirect("panel:products")


@admin_required
def order_list(request):
    orders = (
        Order.objects.select_related("customer")
        .prefetch_related("lines__product")
        .order_by("-created_at")
    )
    return render(
        request,
        "panel/order_list.html",
        {
            "section": "orders",
            "orders": orders,
            "order_count": orders.count(),
        },
    )


@admin_required
@require_POST
def order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    status = request.POST.get("status", "")
    allowed = {Order.STATUS_ACCEPTED, Order.STATUS_CANCELLED}
    if order.status != Order.STATUS_NEW or status not in allowed:
        messages.error(request, "Only a new order can be accepted or cancelled.")
        return redirect("panel:orders")
    order.status = status
    order.save(update_fields=["status"])
    label = "Accepted" if status == Order.STATUS_ACCEPTED else "Cancelled"
    audit(request, f"{label} order", f"Order: {order.number}")
    messages.success(request, f"{order.number} {label.lower()}.")
    return redirect("panel:orders")


@admin_required
def customer_list(request):
    return render(
        request,
        "panel/customer_list.html",
        {"section": "customers", "customers": Customer.objects.order_by("-created_at")},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def customer_edit(request, pk=None):
    customer = get_object_or_404(Customer, pk=pk) if pk else None
    form = CustomerForm(request.POST or None, instance=customer)
    if request.method == "POST" and form.is_valid():
        _save_form(
            request,
            form,
            "Updated customer" if customer else "Created customer",
            "Customer",
        )
        return redirect("panel:customers")
    return render(
        request,
        "panel/form.html",
        {
            "section": "customers",
            "heading": "Edit customer" if customer else "New customer",
            "form": form,
            "cancel_url_name": "panel:customers",
        },
    )


@admin_required
@require_POST
def customer_toggle(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.is_active = not customer.is_active
    customer.save(update_fields=["is_active"])
    state = "Enabled" if customer.is_active else "Disabled"
    audit(request, f"{state} customer", f"Customer: {customer.name}")
    messages.success(request, f"{customer.name} {state.lower()}.")
    return redirect("panel:customers")


@admin_required
def user_list(request):
    return render(
        request,
        "panel/user_list.html",
        {"section": "users", "users": InternalUser.objects.order_by("-created_at")},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def user_edit(request, pk=None):
    user = get_object_or_404(InternalUser, pk=pk) if pk else None
    form = InternalUserForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        _save_form(
            request,
            form,
            "Updated user" if user else "Created user",
            "User",
        )
        return redirect("panel:users")
    return render(
        request,
        "panel/form.html",
        {
            "section": "users",
            "heading": "Edit user" if user else "New user",
            "form": form,
            "cancel_url_name": "panel:users",
        },
    )


@admin_required
@require_POST
def user_toggle(request, pk):
    user = get_object_or_404(InternalUser, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    state = "Enabled" if user.is_active else "Disabled"
    audit(request, f"{state} user", f"User: {user.name}")
    messages.success(request, f"{user.name} {state.lower()}.")
    return redirect("panel:users")


@admin_required
def b2b_list(request):
    return render(
        request,
        "panel/b2b_list.html",
        {"section": "b2b", "registrations": B2BRegistration.objects.order_by("-created_at")},
    )


@admin_required
@require_POST
def b2b_status(request, pk):
    registration = get_object_or_404(B2BRegistration, pk=pk)
    status = request.POST.get("status", "")
    allowed = {B2BRegistration.STATUS_ACCEPTED, B2BRegistration.STATUS_CANCELLED}
    if registration.status != B2BRegistration.STATUS_PENDING or status not in allowed:
        messages.error(request, "Only a pending registration can be accepted or cancelled.")
        return redirect("panel:b2b")
    registration.status = status
    registration.save(update_fields=["status"])
    label = "Accepted" if status == B2BRegistration.STATUS_ACCEPTED else "Cancelled"
    audit(request, f"{label} B2B registration", f"B2B: {registration.company}")
    messages.success(request, f"{registration.company} {label.lower()}.")
    return redirect("panel:b2b")


@admin_required
def banner_list(request):
    return render(
        request,
        "panel/banner_list.html",
        {"section": "banners", "banners": Banner.objects.order_by("-updated_at", "-id")},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def banner_edit(request, pk=None):
    banner = get_object_or_404(Banner, pk=pk) if pk else None
    form = BannerForm(request.POST or None, request.FILES or None, instance=banner)
    if request.method == "POST" and form.is_valid():
        _save_form(
            request,
            form,
            "Updated banner" if banner else "Created banner",
            "Banner",
        )
        return redirect("panel:banners")
    return render(
        request,
        "panel/form.html",
        {
            "section": "banners",
            "heading": "Edit banner" if banner else "New banner",
            "form": form,
            "cancel_url_name": "panel:banners",
        },
    )


@admin_required
@require_POST
def banner_delete(request, pk):
    banner = get_object_or_404(Banner, pk=pk)
    title = banner.title
    if banner.image:
        banner.image.delete(save=False)
    banner.delete()
    audit(request, "Deleted banner", f"Banner: {title}")
    messages.success(request, f"{title} deleted.")
    return redirect("panel:banners")


@admin_required
def coupon_list(request):
    return render(
        request,
        "panel/coupon_list.html",
        {"section": "coupons", "coupons": Coupon.objects.order_by("-created_at")},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def coupon_edit(request, pk=None):
    coupon = get_object_or_404(Coupon, pk=pk) if pk else None
    form = CouponForm(request.POST or None, instance=coupon)
    if request.method == "POST" and form.is_valid():
        _save_form(
            request,
            form,
            "Updated coupon" if coupon else "Created coupon",
            "Coupon",
        )
        return redirect("panel:coupons")
    return render(
        request,
        "panel/form.html",
        {
            "section": "coupons",
            "heading": "Edit coupon" if coupon else "New coupon",
            "form": form,
            "cancel_url_name": "panel:coupons",
        },
    )


@admin_required
@require_POST
def coupon_delete(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    code = coupon.code
    coupon.delete()
    audit(request, "Deleted coupon", f"Coupon: {code}")
    messages.success(request, f"{code} deleted.")
    return redirect("panel:coupons")


@admin_required
def audit_list(request):
    return render(
        request,
        "panel/audit_list.html",
        {"section": "audit", "entries": AuditTrail.objects.order_by("-created_at")[:200]},
    )
