from django import forms
from .models import Shipping_Address
from django.core.validators import validate_email, EmailValidator
from django.core.exceptions import ValidationError

from ecommerce.constants import ALLOWED_CONSUMER_DOMAINS

class ShippingForm(forms.ModelForm):
    
    class Meta:
        model= Shipping_Address
        fields= ['fullname', 'email', 'address1', 'address2', 'city', 'state', 'zipcode',]
        exclude= ['user',]

    def clean_fullname(self):
        fullname= self.cleaned_data.get('fullname').strip().lower()

        if len(fullname.split()) < 2:
            raise ValidationError("full name must at least contain the first name and last name")
    
        return fullname

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        
        # Secure secondary validation check to guarantee a strict email syntax match
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Please provide a valid email format.")
        # A robust list of the most widely used global consumer email domains


        if not email.endswith(tuple(ALLOWED_CONSUMER_DOMAINS)):
            raise ValidationError("Enter a valid email with a valid domain")
        return email

    def clean_zipcode(self):
        zipcode = self.cleaned_data.get('zipcode').strip()
        
        if not zipcode.isdigit() or len(zipcode) != 5:
            raise ValidationError("Zip code must be exactly 5 numeric digits.")
        return zipcode

    # 4. Global Form Sanitation Layout (Cross-field parsing)
    def clean(self):
        cleaned_data = super().clean()
        address1 = cleaned_data.get('address1')
        state = cleaned_data.get('state')

        # Clean check: Restrict PO Boxes
        if address1 and "p.o. box" in address1.lower():
            self.add_error('address1', "We cannot deliver shipments to P.O. Box addresses.")

        # Clean check: Capitalize state code to standard 2-character formatting (e.g., ca -> CA)
        if state:
            cleaned_data['state'] = state.strip().upper()
            if len(cleaned_data['state']) != 2:
                self.add_error('state', "Please use the standard 2-letter state abbreviation.")

        return cleaned_data
