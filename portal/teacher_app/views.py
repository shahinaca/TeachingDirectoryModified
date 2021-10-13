from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from .models import Subject, Teacher
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.views.generic.base import TemplateResponseMixin, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.files import File

from django import forms
from .forms import TeacherForm, ImportFileForm
from django.contrib import messages
from zipfile import ZipFile
from django.conf import settings
from io import BytesIO
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io
import csv
import zipfile
from io import TextIOWrapper


class DashboardView(View):
    model = Teacher
    template_name = 'dashboard.html'

    def get(self, request):
        teachers = self.model.objects.all()
        return render(request, self.template_name, {'teachers': teachers, 'filename': 'dashboard'})


class TeachersView(ListView):
    paginate_by = 4
    model = Teacher
    template_name = 'teacher/teachers_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        array_last_name = []
        array_subjects_thought = []
        all_teachers = self.model.objects.values_list('last_name', flat=True).exclude(
            last_name='').filter(last_name__isnull=False).order_by('last_name').distinct()
        all_subjects = Subject.objects.values_list('display_name', flat=True).filter(
            display_name__isnull=False).exclude(display_name='').order_by('display_name').distinct()
        for teacher in all_teachers:
            letter_first = teacher.strip().upper()[0]
            if letter_first not in array_last_name:
                array_last_name.append(letter_first)
        for subject in all_subjects:
            letter_first = subject.strip()
            if letter_first not in array_subjects_thought:
                array_subjects_thought.append(letter_first)
        context['array_last_name'] = array_last_name
        context['filename'] = 'teachers'
        context['last_name_query'] = self.request.GET.get("last_name")
        context['subject_query'] = self.request.GET.get("subjects_taught")
        context['array_subjects_thought'] = array_subjects_thought
        return context

    def get_queryset(self):
        teachers = self.model.objects.all()
        last_name = self.request.GET.get("last_name")
        subjects_taught = self.request.GET.get("subjects_taught")
        if last_name or subjects_taught:
            if subjects_taught:
                teachers = teachers.filter(subjects_taught__display_name__contains=subjects_taught)
            if last_name:
                teachers = teachers.filter(last_name__istartswith=last_name)
        return teachers


class TeacherProfileView(DetailView):
    model = Teacher
    template_name = 'teacher/teacher_view.html'


class UploadTeachersView(LoginRequiredMixin, TemplateResponseMixin, View):
    template_name = 'teacher/teacher_upload.html'

    def get(self, request):
        form = ImportFileForm()
        return render(request, self.template_name, {'form': form, 'filename': 'teachers'})

    def post(self, request, *args, **kwargs):
        bulk_image_path = settings.MEDIA_ROOT.joinpath('images').joinpath('teachers.zip')
        form = ImportFileForm(request.POST, request.FILES)
        error_string = str()
        if form.is_valid():
            csv_file = request.FILES['teachers_details']
            data_bytes = TextIOWrapper(csv_file.file,
                                       encoding='utf-8')
            csv_file_data = csv.DictReader(data_bytes)

            images = request.FILES['image_details']
            target = open(bulk_image_path, 'wb+')

            for one in images.chunks():
                target.write(one)

            zip_file = zipfile.ZipFile(bulk_image_path, 'r')
            i = 0
            for one in csv_file_data:
                i = i + 1
                try:
                    if one['First Name'].strip() == '' or one['Email Address'].strip() == '':
                        raise Exception('First Name / Email cant be blank')

                    data_dict = {'first_name': one['First Name'].strip(), 'last_name': one['Last Name'].strip(),
                                 'email_address': one['Email Address'].strip(), 'phone_number': one[
                            'Phone Number'].strip(), 'room_number': one['Room Number'].strip()}
                    list_of_subjects_taught = []
                    tform = TeacherForm(data_dict)
                    if tform.is_valid():
                        teacher_model = tform.save()

                        subjects_taught = one['Subjects taught'].split(',')
                        # Unique Subjects
                        for single_subject in subjects_taught:
                            single_subject = single_subject.strip()
                            if single_subject not in list_of_subjects_taught:
                                list_of_subjects_taught.append(single_subject)

                        if one['Profile picture'] in zip_file.namelist():
                            zip_image = zip_file.open(one['Profile picture'], 'r')
                            file_image = File(zip_image)
                            teacher_model.profile_picture.save(one['Profile picture'], file_image, save=True)

                        for single_subject in list_of_subjects_taught:
                            if single_subject != '':
                                single_subject_attach, _ = Subject.objects.get_or_create(display_name=
                                                                                         single_subject.strip().upper())
                                if teacher_model.subjects_taught.count() < 5:
                                    teacher_model.subjects_taught.add(single_subject_attach)
                                else:
                                    error_string = error_string + \
                                                   ' <br> Row- ' + str(i) + ' ' + ' Subject must be less than' \
                                                                                  ' or equal to 5'
                                    break
                        messages.add_message(request, messages.SUCCESS, ' Row- ' + str(i) + ' Row Updated '
                                                                                            'successfully')
                    else:
                        error_string = error_string + ' <br> Row- ' + str(i) + ' ' + ' '.join(
                            [' '.join(x for x in l) for l in list(tform.errors.values())])

                except Exception as e:
                    error_string = error_string + ' <br> Row- ' + str(i) + ' ' + str(e)

            os.remove(bulk_image_path)
            messages.add_message(request, messages.ERROR, error_string)
        return render(request, self.template_name, {'form': form, 'filename': 'teachers'})


class ErrorView(View):

    def get(self, request, tagname):
        return render(request, '404.html')