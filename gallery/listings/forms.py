from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

class YearForm(forms.Form):
    year = forms.IntegerField(
                validators=[MinValueValidator(2002), MaxValueValidator(2022)]
    )
