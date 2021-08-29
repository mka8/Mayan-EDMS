from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_version_models import DocumentVersion
from mayan.apps.organizations.utils import get_organization_installation_url
from mayan.apps.views.generics import (
    FormView, MultipleObjectFormActionView, SingleObjectDeleteView,
    SingleObjectDynamicFormCreateView, SingleObjectDynamicFormEditView,
    SingleObjectListView
)
from mayan.apps.views.mixins import ExternalObjectViewMixin

from ..classes import MailerBackend
from ..forms import (
    DocumentMailForm, UserMailerBackendSelectionForm, UserMailerDynamicForm,
    UserMailerTestForm
)
from ..icons import icon_mail_document_submit, icon_user_mailer_setup
from ..links import link_user_mailer_create
from ..models import UserMailer
from ..permissions import (
    permission_mailing_send_document_link, permission_mailing_send_document_attachment,
    permission_user_mailer_create, permission_user_mailer_delete,
    permission_user_mailer_edit, permission_user_mailer_use,
    permission_user_mailer_view
)
from ..tasks import task_send_document_version


class MailDocumentVersionView(MultipleObjectFormActionView):
    as_attachment = True
    form_class = DocumentMailForm
    object_permission = permission_mailing_send_document_attachment
    pk_url_kwarg = 'document_version_id'
    source_queryset = DocumentVersion.valid
    success_message = _(
        '%(count)d document version queued for email delivery'
    )
    success_message_plural = _(
        '%(count)d document versions queued for email delivery'
    )
    title = 'Email document version'
    title_plural = 'Email documents version'
    title_document = 'Email document version: %s'

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'submit_icon': icon_mail_document_submit,
            'submit_label': _('Send'),
            'title': ungettext(
                singular=self.title,
                plural=self.title_plural,
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _(self.title_document) % queryset.first()
                }
            )

        return result

    def get_form_extra_kwargs(self):
        return {
            'as_attachment': self.as_attachment,
            'user': self.request.user
        }

    def object_action(self, form, instance):
        AccessControlList.objects.check_access(
            obj=form.cleaned_data['user_mailer'],
            permissions=(permission_user_mailer_use,), user=self.request.user
        )

        task_send_document.apply_async(
            kwargs={
                'as_attachment': self.as_attachment,
                'body': form.cleaned_data['body'],
                'document_version_id': instance.pk,
                'organization_installation_url': get_organization_installation_url(
                    request=self.request
                ),
                'recipient': form.cleaned_data['email'],
                'sender': self.request.user.email,
                'subject': form.cleaned_data['subject'],
                'user_mailer_id': form.cleaned_data['user_mailer'].pk
            }
        )


class MailDocumentVersionLinkView(MailDocumentVersionView):
    as_attachment = False
    object_permission = permission_mailing_send_document_link
    success_message = _(
        '%(count)d document version link queued for email delivery'
    )
    success_message_plural = _(
        '%(count)d document version links queued for email delivery'
    )
    title = 'Email document version link'
    title_plural = 'Email document version links'
    title_document = 'Email link for document version: %s'

