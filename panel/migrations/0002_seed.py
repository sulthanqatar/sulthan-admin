from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def seed(apps, schema_editor):
    ProductCategory = apps.get_model("panel", "ProductCategory")
    if ProductCategory.objects.exists():
        return

    Product = apps.get_model("panel", "Product")
    Customer = apps.get_model("panel", "Customer")
    InternalUser = apps.get_model("panel", "InternalUser")
    B2BRegistration = apps.get_model("panel", "B2BRegistration")
    Order = apps.get_model("panel", "Order")
    OrderLine = apps.get_model("panel", "OrderLine")
    Banner = apps.get_model("panel", "Banner")
    Coupon = apps.get_model("panel", "Coupon")
    AuditTrail = apps.get_model("panel", "AuditTrail")

    now = timezone.now()
    tableware = ProductCategory.objects.create(name="Tableware")
    bottles = ProductCategory.objects.create(name="Bottles")
    hygiene = ProductCategory.objects.create(name="Hygiene")
    packaging = ProductCategory.objects.create(name="Packaging")
    stationery = ProductCategory.objects.create(name="Stationery")

    catalog = [
        (tableware, "Paper glass", "Paper glass", "8.00", 240),
        (tableware, "Paper plate", "Paper plate", "7.50", 180),
        (bottles, "Plastic bottle", "Plastic bottle", "4.00", 320),
        (bottles, "Glass bottle", "Glass bottle", "6.50", 140),
        (hygiene, "Tissue paper", "Tissue paper", "5.00", 260),
        (hygiene, "Glow", "Glow", "9.00", 150),
        (hygiene, "Mask", "Mask", "3.50", 400),
        (stationery, "Pen", "Pen", "2.00", 500),
        (packaging, "Paper bag", "Paper bag", "6.00", 210),
        (tableware, "Paper straw", "Paper straw", "4.50", 300),
        (stationery, "Sticky notes", "Sticky notes", "3.00", 180),
        (hygiene, "Towel", "Towel", "12.00", 90),
    ]
    products = []
    for index, (category, sku, name, price, stock) in enumerate(catalog):
        product = Product.objects.create(
            category=category,
            sku=sku,
            name=name,
            price=price,
            stock=stock,
            description=f"{name} for the Sulthan catalog.",
        )
        Product.objects.filter(pk=product.pk).update(
            stock_updated_at=now - timedelta(hours=index)
        )
        products.append(product)

    people = [
        ("Mariam Al Kuwari", "mariam@example.com", "+974 5551 1001", "West Bay"),
        ("Faisal Rahman", "faisal@example.com", "+974 5551 1002", "Al Sadd"),
        ("Aisha Khan", "aisha@example.com", "+974 5551 1003", "The Pearl"),
        ("Sara Ibrahim", "sara@example.com", "+974 5551 1004", "Lusail"),
        ("Hassan Ali", "hassan@example.com", "+974 5551 1005", "Al Wakrah"),
        ("Noura Fakhro", "noura@example.com", "+974 5551 1006", "Al Rayyan"),
        ("Khalid Mansoor", "khalid@example.com", "+974 5551 1007", "Musheireb"),
        ("Lina George", "lina@example.com", "+974 5551 1008", "Doha"),
    ]
    customers = [
        Customer.objects.create(name=name, email=email, phone=phone, area=area)
        for name, email, phone, area in people
    ]

    InternalUser.objects.bulk_create(
        [
            InternalUser(name="Layla Hassan", email="layla@sulthan.example", role="admin"),
            InternalUser(name="Omar Farid", email="omar@sulthan.example", role="admin"),
            InternalUser(name="Noor Saleh", email="noor@sulthan.example", role="admin"),
            InternalUser(
                name="Huda Karim",
                email="huda@sulthan.example",
                role="admin",
                is_active=False,
            ),
            InternalUser(name="Yusuf Ali", email="yusuf@sulthan.example", role="staff"),
            InternalUser(name="Sami Nasser", email="sami@sulthan.example", role="warehouse"),
            InternalUser(name="Rana Iqbal", email="rana@sulthan.example", role="delivery"),
        ]
    )

    B2BRegistration.objects.bulk_create(
        [
            B2BRegistration(
                company="Al Mana Trading",
                contact_name="Adel Al Mana",
                email="adel@almana.example",
                phone="+974 4441 2001",
                status="pending",
            ),
            B2BRegistration(
                company="Doha Fresh Co",
                contact_name="Hanan Darwish",
                email="hanan@dohafresh.example",
                phone="+974 4441 2002",
                status="accepted",
            ),
            B2BRegistration(
                company="Lusail Catering",
                contact_name="Bilal Osman",
                email="bilal@lusailcatering.example",
                phone="+974 4441 2003",
                status="accepted",
            ),
            B2BRegistration(
                company="Bin Hindi Stores",
                contact_name="Tariq Bin Hindi",
                email="tariq@binhindi.example",
                phone="+974 4441 2004",
                status="accepted",
            ),
            B2BRegistration(
                company="Pearl Supplies",
                contact_name="Maya Joseph",
                email="maya@pearlsupplies.example",
                phone="+974 4441 2005",
                status="pending",
            ),
            B2BRegistration(
                company="Wakrah Mini Mart",
                contact_name="Fadi Nader",
                email="fadi@wakrahmm.example",
                phone="+974 4441 2006",
                status="cancelled",
            ),
        ]
    )

    # Paper glass quantities total 40, ahead of the other stationery items.
    line_plan = [
        ("new", [(0, 10), (5, 5)]),
        ("new", [(0, 8), (2, 2)]),
        ("new", [(0, 6), (4, 3)]),
        ("accepted", [(0, 12), (3, 4)]),
        ("accepted", [(0, 4), (1, 2)]),
        ("accepted", [(5, 10), (4, 6)]),
        ("cancelled", [(5, 8), (7, 5)]),
        ("accepted", [(2, 6), (6, 2)]),
        ("new", [(3, 3), (8, 1)]),
        ("cancelled", [(9, 4), (1, 1)]),
        ("accepted", [(4, 5), (6, 1)]),
        ("cancelled", [(7, 8)]),
    ]
    for index, (status, lines) in enumerate(line_plan):
        order = Order.objects.create(
            number=f"SO-{1101 + index}",
            customer=customers[index % len(customers)],
            status=status,
        )
        Order.objects.filter(pk=order.pk).update(created_at=now - timedelta(hours=11 - index))
        for product_index, quantity in lines:
            OrderLine.objects.create(
                order=order,
                product=products[product_index],
                quantity=quantity,
            )

    Banner.objects.bulk_create(
        [
            Banner(
                title="Ramadan pantry",
                subtitle="Rice, dates, and oil for the month",
                link_url="https://sulthan.example/ramadan",
            ),
            Banner(
                title="Office delivery",
                subtitle="Same-day drops across Doha",
                link_url="https://sulthan.example/delivery",
                is_active=False,
            ),
        ]
    )
    Coupon.objects.bulk_create(
        [
            Coupon(code="WELCOME10", description="First order", discount_percent=10),
            Coupon(code="RICE5", description="Rice and grains", discount_percent=5),
            Coupon(
                code="B2B15",
                description="Accepted business accounts",
                discount_percent=15,
                expires_on=(now + timedelta(days=90)).date(),
            ),
        ]
    )
    AuditTrail.objects.create(
        actor="system",
        action="Seeded demo data",
        target="Catalog, orders, customers, and coupons",
    )


def unseed(apps, schema_editor):
    ProductCategory = apps.get_model("panel", "ProductCategory")
    ProductCategory.objects.all().delete()
    for model_name in (
        "Customer",
        "InternalUser",
        "B2BRegistration",
        "Banner",
        "Coupon",
        "AuditTrail",
    ):
        apps.get_model("panel", model_name).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("panel", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
