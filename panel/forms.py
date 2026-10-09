from django import forms

from panel.models import Banner, Coupon, Customer, InternalUser, Product, ProductCategory


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs["class"] = "field"


class ProductCategoryForm(StyledModelForm):
    class Meta:
        model = ProductCategory
        fields = ["name", "is_active"]


class ProductForm(StyledModelForm):
    class Meta:
        model = Product
        fields = ["category", "sku", "name", "description", "price", "stock", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class CustomerForm(StyledModelForm):
    class Meta:
        model = Customer
        fields = ["name", "email", "is_active"]


class InternalUserForm(StyledModelForm):
    class Meta:
        model = InternalUser
        fields = ["name", "email", "role", "is_active"]


class BannerForm(StyledModelForm):
    class Meta:
        model = Banner
        fields = ["title", "subtitle", "image", "link_url", "is_active"]


class CouponForm(StyledModelForm):
    class Meta:
        model = Coupon
        fields = ["code", "description", "discount_percent", "is_active", "expires_on"]
        widgets = {
            "expires_on": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["expires_on"].input_formats = ["%Y-%m-%d"]

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()
