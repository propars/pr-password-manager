from django import forms
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from .models import Password


class PasswordInput(forms.TextInput):
    template_name = 'password_generator.html'


class PasswordAddForm(forms.ModelForm):
    valid_days = forms.IntegerField(required=True, initial=90)
    password_length = forms.IntegerField(required=False, initial=30)
    contains_punctuation = forms.BooleanField(required=False)
    raw_password = forms.CharField(required=True, widget=PasswordInput)

    def save(self, commit=True):
        self.instance.hash = make_password(self.cleaned_data['raw_password'])

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
        fields = '__all__'
