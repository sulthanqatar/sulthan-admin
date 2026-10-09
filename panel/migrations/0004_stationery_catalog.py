from django.db import migrations


# Existing grocery rows are renamed in place so order lines keep their quantities.
RENAMES = {
    "Basmati rice 5kg": ("Tableware", "Paper glass"),
    "Sella rice 10kg": ("Tableware", "Paper plate"),
    "Sunflower oil 1.8L": ("Bottles", "Plastic bottle"),
    "Medjool dates 1kg": ("Bottles", "Glass bottle"),
    "Green tea 100 bags": ("Hygiene", "Tissue paper"),
    "Mineral water 1.5L case": ("Hygiene", "Glow"),
    "Green cardamom 200g": ("Hygiene", "Mask"),
    "Vermicelli 500g": ("Stationery", "Pen"),
    "Sidr honey 500g": ("Packaging", "Paper bag"),
    "Arabic coffee 250g": ("Tableware", "Paper straw"),
}

NEW_ITEMS = [
    ("Stationery", "Sticky notes", "3.00", 180),
    ("Hygiene", "Towel", "12.00", 90),
]


def category_names():
    names = {category for category, _name in RENAMES.values()}
    names.update(category for category, _name, _price, _stock in NEW_ITEMS)
    return names


def load_stationery(apps, schema_editor):
    Product = apps.get_model("panel", "Product")
    if Product.objects.filter(name="Paper glass").exists():
        return

    ProductCategory = apps.get_model("panel", "ProductCategory")
    categories = {}

    def category_for(name):
        category = categories.get(name)
        if category is None:
            category = ProductCategory.objects.create(name=name)
            categories[name] = category
        return category

    for old_name, (category_name, new_name) in RENAMES.items():
        product = Product.objects.filter(name=old_name).first()
        if product is None:
            continue
        product.category = category_for(category_name)
        product.sku = new_name
        product.name = new_name
        product.description = f"{new_name} for the Sulthan catalog."
        product.save(update_fields=["category", "sku", "name", "description"])

    for category_name, name, price, stock in NEW_ITEMS:
        if Product.objects.filter(name=name).exists():
            continue
        Product.objects.create(
            category=category_for(category_name),
            sku=name,
            name=name,
            description=f"{name} for the Sulthan catalog.",
            price=price,
            stock=stock,
        )

    ProductCategory.objects.exclude(name__in=category_names()).filter(products__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("panel", "0003_stock_keeping_unit"),
    ]

    operations = [
        migrations.RunPython(load_stationery, migrations.RunPython.noop),
    ]
