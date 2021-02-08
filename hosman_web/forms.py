from django.contrib.auth import password_validation
from django.contrib.auth.forms import UsernameField, UserCreationForm
from django.forms import ModelForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from editorial.models import *


class PatientForm(ModelForm):
    class Meta:
        model = Patient
        exclude = ['profile_picture', 'varified']
        localized_fields = "__all__"
        widgets = {
            'user': forms.HiddenInput(),
            'address': forms.HiddenInput()
        }

class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude =[]
        localized_fields = "__all__"

class GContentForm(ModelForm):
    class Meta:
        model = GContent
        exclude = []
        labels = {
            'content': 'Upload Media'
        }
        widgets = {
            
        }
        localized_fields = "__all__"

class CUserCreationForm(UserCreationForm, ModelForm):
    error_messages = {
        "password_mismatch": _("The two password fields did not match.")
    }
    password1 = forms.CharField(
        label=_("Password"), 
        strip=False, 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html()
        )
    password2 = forms.CharField(
        label=_("Password Confirmation"), 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), 
        help_text=_("Enter the same password as above for validation.")
        )
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username']
        field_classes = {'username': UsernameField}
        localized_fields = "__all__"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs['autofocus'] = True
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch')
        return password2
    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get('password2')
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error('password2', error)
    def save(self, commit=True):
        user = super(CUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user