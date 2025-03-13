from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from orders.models import Order


class OrderForm(forms.ModelForm):
    """
    Form for filling in basic information about the order.
    """
    country = CountryField(blank_label="Select country").formfield(
        widget=CountrySelectWidget(attrs={"class": "form-control"})
    )

    class Meta:
        model = Order
        fields = ["country", "address"]
        widgets = {
            "country": CountrySelectWidget(),
            "address": forms.TextInput(attrs={"placeholder": "Enter your address"}),
        }


class ShippingForm(forms.Form):
    """
    Form for choosing a delivery carrier.
    """
    CARRIER_CHOICES = [
        ("cargo_express", "CargoExpress"),
        ("dhl", "DHL"),
        ("fedex", "FedEx"),
    ]
    carrier = forms.ChoiceField(choices=CARRIER_CHOICES, widget=forms.RadioSelect)


class PaymentForm(forms.Form):
    """
    Form for selecting the method of payment.
    """
    PAYMENT_CHOICES = [
        ("credit_card", "Credit Card"),
        ("paypal", "PayPal"),
        ("google_pay", "Google Pay"),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES, widget=forms.RadioSelect
    )


class ReceiverForm(forms.Form):
    """
    Form for entering the recipient's data.
    """
    receiver_name = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "Full name"})
    )
    receiver_phone = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"placeholder": "Phone number"})
    )


class CommentForm(forms.Form):
    """
    Form for adding a comment to the order.
    """
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Add a comment", "rows": 3}),
    )
