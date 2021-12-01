from django.contrib import admin
from django.shortcuts import redirect

from .models import Password, ArchivedPassword
from .forms import PasswordAddForm, PasswordEditForm


class PasswordAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expire_date', 'is_alive')
    list_display_links = ('id', 'name')
    list_filter = ('is_alive',)

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.form = PasswordEditForm
        else:
            self.form = PasswordAddForm
        return super(PasswordAdmin, self).get_form(request, obj, **kwargs)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save'] = False
        extra_context['show_delete'] = False
        return super().change_view(request, object_id, form_url=form_url, extra_context=extra_context)


class ArchivedPasswordAdmin(PasswordAdmin):
    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Password, PasswordAdmin)
admin.site.register(ArchivedPassword, ArchivedPasswordAdmin)

admin.site.site_header = "Propars Password Manager"
admin.site.site_title = "Propars Password Manager"
admin.site.index_title = ""

