import copy
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

DEMO_USERNAME = "admin"
DEMO_PASSWORD = "admin@123"

PORTALS = {
    "staff": {
        "title": "Staff",
        "kicker": "Office",
        "lede": "Accept incoming orders, mark them packed, and update product stock.",
    },
    "warehouse": {
        "title": "Warehouse",
        "kicker": "Storage",
        "lede": "Track on-hand stock at each warehouse and storage location.",
    },
    "delivery": {
        "title": "Delivery",
        "kicker": "Dispatch",
        "lede": "See orders ready to go out and mark them delivered or not.",
    },
}

STATUS_LABELS = {
    "new": "New",
    "accepted": "Accepted",
    "packed": "Packed",
    "delivered": "Delivered",
    "not_delivered": "Not delivered",
}

SEED = {
    "products": [
        {"id": "p1", "sku": "RCE-5KG", "name": "Basmati rice 5kg", "stock": 240},
        {"id": "p2", "sku": "RCE-10KG", "name": "Sella rice 10kg", "stock": 128},
        {"id": "p3", "sku": "OIL-18", "name": "Sunflower oil 1.8L", "stock": 86},
        {"id": "p4", "sku": "DTE-1KG", "name": "Medjool dates 1kg", "stock": 54},
        {"id": "p5", "sku": "TEA-100", "name": "Green tea 100 bags", "stock": 160},
        {"id": "p6", "sku": "WTR-15", "name": "Mineral water 1.5L case", "stock": 310},
    ],
    "locations": [
        {
            "id": "doha",
            "name": "Doha main warehouse",
            "kind": "Warehouse",
            "address": "Industrial Area, Street 23",
        },
        {
            "id": "rayyan",
            "name": "Al Rayyan storage",
            "kind": "Storage",
            "address": "Al Rayyan, Zone 52",
        },
        {
            "id": "lusail",
            "name": "Lusail warehouse",
            "kind": "Warehouse",
            "address": "Lusail, Marina district",
        },
    ],
    "inventory": [
        {"location_id": "doha", "product_id": "p1", "qty": 140},
        {"location_id": "doha", "product_id": "p2", "qty": 70},
        {"location_id": "doha", "product_id": "p3", "qty": 40},
        {"location_id": "doha", "product_id": "p4", "qty": 30},
        {"location_id": "doha", "product_id": "p5", "qty": 90},
        {"location_id": "doha", "product_id": "p6", "qty": 180},
        {"location_id": "rayyan", "product_id": "p1", "qty": 60},
        {"location_id": "rayyan", "product_id": "p2", "qty": 38},
        {"location_id": "rayyan", "product_id": "p3", "qty": 26},
        {"location_id": "rayyan", "product_id": "p4", "qty": 12},
        {"location_id": "rayyan", "product_id": "p5", "qty": 40},
        {"location_id": "rayyan", "product_id": "p6", "qty": 80},
        {"location_id": "lusail", "product_id": "p1", "qty": 40},
        {"location_id": "lusail", "product_id": "p2", "qty": 20},
        {"location_id": "lusail", "product_id": "p3", "qty": 20},
        {"location_id": "lusail", "product_id": "p4", "qty": 12},
        {"location_id": "lusail", "product_id": "p5", "qty": 30},
        {"location_id": "lusail", "product_id": "p6", "qty": 50},
    ],
    "orders": [
        {
            "id": "SO-1048",
            "customer": "Al Mana Trading",
            "area": "West Bay",
            "items": "Basmati rice 5kg × 10, Sunflower oil × 4",
            "status": "new",
            "location": "Doha main warehouse",
        },
        {
            "id": "SO-1047",
            "customer": "Lusail Catering",
            "area": "Lusail",
            "items": "Medjool dates 1kg × 8, Green tea × 6",
            "status": "new",
            "location": "Lusail warehouse",
        },
        {
            "id": "SO-1046",
            "customer": "Bin Hindi Stores",
            "area": "Al Sadd",
            "items": "Sella rice 10kg × 6, Mineral water × 12",
            "status": "accepted",
            "location": "Doha main warehouse",
        },
        {
            "id": "SO-1045",
            "customer": "Pearl Hotel",
            "area": "The Pearl",
            "items": "Sunflower oil × 10, Green tea × 8",
            "status": "packed",
            "location": "Al Rayyan storage",
        },
        {
            "id": "SO-1044",
            "customer": "Wakrah Mini Mart",
            "area": "Al Wakrah",
            "items": "Mineral water × 20, Basmati rice 5kg × 4",
            "status": "packed",
            "location": "Doha main warehouse",
        },
    ],
}


def portal_data(request):
    if "portal_data" not in request.session:
        request.session["portal_data"] = copy.deepcopy(SEED)
    return request.session["portal_data"]


def save_portal_data(request):
    request.session.modified = True


def portal_required(role):
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.session.get("portal_role") != role:
                return redirect(f"/{role}/login/")
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def _find(items, item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


@require_http_methods(["GET", "POST"])
def login(request, role):
    portal = PORTALS[role]
    if request.session.get("portal_role") == role:
        return redirect(f"/{role}/")

    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if username == DEMO_USERNAME and password == DEMO_PASSWORD:
            request.session["portal_role"] = role
            request.session["portal_user"] = username
            portal_data(request)
            return redirect(f"/{role}/")
        error = "Those credentials were not recognised. Use the demo sign-in below."

    return render(
        request,
        "portals/login.html",
        {"role": role, "portal": portal, "error": error},
    )


def logout(request, role):
    if request.session.get("portal_role") == role:
        request.session.pop("portal_role", None)
        request.session.pop("portal_user", None)
    return redirect(f"/{role}/login/")


def _shell(request, role, section):
    return {
        "role": role,
        "portal": PORTALS[role],
        "section": section,
        "username": request.session.get("portal_user", DEMO_USERNAME),
    }


@portal_required("staff")
def staff_orders(request):
    data = portal_data(request)
    orders = sorted(
        data["orders"],
        key=lambda order: ("new", "accepted", "packed", "delivered", "not_delivered").index(
            order["status"]
        ),
    )
    context = _shell(request, "staff", "orders")
    context.update(
        {
            "orders": orders,
            "new_count": sum(1 for order in orders if order["status"] == "new"),
            "accepted_count": sum(1 for order in orders if order["status"] == "accepted"),
            "packed_count": sum(1 for order in orders if order["status"] == "packed"),
            "status_labels": STATUS_LABELS,
        }
    )
    return render(request, "portals/staff_orders.html", context)


@portal_required("staff")
@require_POST
def staff_order_status(request, order_id):
    status = request.POST.get("status")
    if status not in {"accepted", "packed"}:
        messages.error(request, "Staff can only mark an order accepted or packed.")
        return redirect("/staff/")

    order = _find(portal_data(request)["orders"], order_id)
    if order is None:
        messages.error(request, "That order was not found.")
        return redirect("/staff/")

    if order["status"] in {"delivered", "not_delivered"}:
        messages.error(request, f"{order_id} is already with delivery.")
        return redirect("/staff/")

    order["status"] = status
    save_portal_data(request)
    messages.success(request, f"{order_id} marked {STATUS_LABELS[status].lower()}.")
    return redirect("/staff/")


@portal_required("staff")
def staff_products(request):
    context = _shell(request, "staff", "products")
    context["products"] = portal_data(request)["products"]
    return render(request, "portals/staff_products.html", context)


@portal_required("staff")
@require_POST
def staff_stock(request, product_id):
    product = _find(portal_data(request)["products"], product_id)
    if product is None:
        messages.error(request, "That product was not found.")
        return redirect("/staff/products/")

    raw_qty = request.POST.get("stock", "").strip()
    try:
        qty = int(raw_qty)
    except ValueError:
        messages.error(request, "Enter a whole number for stock.")
        return redirect("/staff/products/")
    if qty < 0:
        messages.error(request, "Stock cannot be negative.")
        return redirect("/staff/products/")

    product["stock"] = qty
    save_portal_data(request)
    messages.success(request, f"{product['name']} stock updated to {qty}.")
    return redirect("/staff/products/")


@portal_required("warehouse")
def warehouse_home(request):
    data = portal_data(request)
    products = {product["id"]: product for product in data["products"]}
    locations = []
    for location in data["locations"]:
        lines = []
        units = 0
        for row in data["inventory"]:
            if row["location_id"] != location["id"]:
                continue
            product = products[row["product_id"]]
            lines.append({**row, "product": product})
            units += row["qty"]
        locations.append({**location, "lines": lines, "units": units})

    context = _shell(request, "warehouse", "inventory")
    context.update(
        {
            "locations": locations,
            "location_count": len(locations),
            "unit_count": sum(location["units"] for location in locations),
        }
    )
    return render(request, "portals/warehouse.html", context)


@portal_required("warehouse")
@require_POST
def warehouse_stock(request):
    location_id = request.POST.get("location_id", "")
    product_id = request.POST.get("product_id", "")
    raw_qty = request.POST.get("qty", "").strip()
    data = portal_data(request)

    row = next(
        (
            item
            for item in data["inventory"]
            if item["location_id"] == location_id and item["product_id"] == product_id
        ),
        None,
    )
    product = _find(data["products"], product_id)
    location = _find(data["locations"], location_id)
    if row is None or product is None or location is None:
        messages.error(request, "That stock line was not found.")
        return redirect("/warehouse/")

    try:
        qty = int(raw_qty)
    except ValueError:
        messages.error(request, "Enter a whole number for the quantity.")
        return redirect("/warehouse/")
    if qty < 0:
        messages.error(request, "Quantity cannot be negative.")
        return redirect("/warehouse/")

    row["qty"] = qty
    save_portal_data(request)
    messages.success(
        request, f"{product['name']} at {location['name']} updated to {qty}."
    )
    return redirect("/warehouse/")


@portal_required("delivery")
def delivery_home(request):
    orders = portal_data(request)["orders"]
    incoming = [order for order in orders if order["status"] == "packed"]
    settled = [
        order for order in orders if order["status"] in {"delivered", "not_delivered"}
    ]
    context = _shell(request, "delivery", "orders")
    context.update(
        {
            "incoming": incoming,
            "settled": settled,
            "status_labels": STATUS_LABELS,
        }
    )
    return render(request, "portals/delivery.html", context)


@portal_required("delivery")
@require_POST
def delivery_status(request, order_id):
    status = request.POST.get("status")
    if status not in {"delivered", "not_delivered"}:
        messages.error(request, "Delivery can only mark an order delivered or not delivered.")
        return redirect("/delivery/")

    order = _find(portal_data(request)["orders"], order_id)
    if order is None:
        messages.error(request, "That order was not found.")
        return redirect("/delivery/")
    if order["status"] != "packed":
        messages.error(request, f"{order_id} is not ready for delivery.")
        return redirect("/delivery/")

    order["status"] = status
    save_portal_data(request)
    messages.success(request, f"{order_id} marked {STATUS_LABELS[status].lower()}.")
    return redirect("/delivery/")
