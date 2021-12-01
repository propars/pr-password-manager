import hashlib
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
    valid_days = forms.IntegerField(required=True, initial=90)
    password_length = forms.IntegerField(required=False, initial=30)
    contains_punctuation = forms.BooleanField(required=False)
    raw_password = forms.CharField(required=True, widget=PasswordInput)

    def save(self, commit=True):
        self.instance.hash = calculate_password_hash(self.cleaned_data['raw_password'])

        # this line checks password hash is already in the table
        if Password.objects.filter(hash=self.instance.hash).exists():
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
