import hashlib
import string
from django import forms
from django.utils import timezone
from django.conf import settings
from .models import Password


def calculate_password_hash(raw_password):
    raw_password = raw_password.encode() if isinstance(raw_password, str) else raw_password
    pw_sha256 = hashlib.sha256(raw_password).hexdigest()
    salt_md5 = hashlib.md5(settings.SECRET_KEY.encode()).hexdigest()
    return hashlib.sha256((pw_sha256+salt_md5).encode()).hexdigest()


class PasswordInput(forms.TextInput):
    template_name = 'password_generator.html'


class PasswordAddForm(forms.ModelForm):
    valid_days = forms.IntegerField(required=True, initial=120)
    password_length = forms.IntegerField(required=False, initial=30)
    contains_punctuation = forms.BooleanField(required=False)
    raw_password = forms.CharField(required=True, widget=PasswordInput)

    def clean_raw_password(self):
        min_length = 12
        raw_password = self.cleaned_data['raw_password']
        _errors = []

        # minimum length check
        if len(raw_password) < min_length:
            _errors.append('Password must be at least 12 characters')

        # check for numeric characters
        if not any(c.isdigit() for c in raw_password):
            _errors.append('Password must contain at least 1 digit.')

        # lowercase check
        if not any(c.isalpha() and c.islower() for c in raw_password):
            _errors.append('Password must contain at least 1 lowercase letter.')

        # uppercase check
        if not any(c.isalpha() and c.isupper() for c in raw_password):
            _errors.append('Password must contain at least 1 uppercase letter.')

        # special character check
        if not any(c in string.punctuation for c in raw_password):
            _errors.append('Password must contain at least 1 special character.')

        if _errors:
            raise forms.ValidationError(_errors)

        return raw_password

    def clean_valid_days(self):
        valid_days = self.cleaned_data['valid_days']
        # minimum valid days: 90
        # maximum valid days: 180
        if valid_days < 90 or valid_days > 180:
            raise forms.ValidationError('Valid days must be between 90 and 180.')
        return valid_days

    def save(self, commit=True):
        self.instance.hash = calculate_password_hash(self.cleaned_data['raw_password'])

        # this line checks password hash is already in the table
        if Password.all_objects.filter(hash=self.instance.hash).exists():
            raise forms.ValidationError({'raw_password': 'this password is already used'})

        self.instance.expire_date = timezone.now() + timezone.timedelta(days=self.cleaned_data['valid_days'])
        instance = super(PasswordAddForm, self).save(commit=commit)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Password
        fields = ['name', 'valid_days', 'password_length', 'contains_punctuation', 'raw_password']


class IsArchivedInput(forms.CheckboxInput):
    template_name = 'is_archived_field.html'
    label = ''

    def label_tag(self):
        pass


class PasswordEditForm(forms.ModelForm):
    is_archived = forms.BooleanField(widget=IsArchivedInput)

    class Meta:
        model = Password
        exclude = ('hash',)
