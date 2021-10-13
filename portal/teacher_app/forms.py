from django import forms
from django.core.validators import FileExtensionValidator

from .models import Teacher


class ImportFileForm(forms.Form):
    teachers_details = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    image_details = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['zip'])])

    def clean(self):
        pass


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'first_name',
            'last_name',
            'email_address',
            'phone_number',
            'room_number'
        ]