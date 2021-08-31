from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models.document_version_models import DocumentVersion
from mayan.apps.organizations.utils import get_organization_installation_url
from mayan.apps.views.generics import MultipleObjectFormActionView

from ..forms import DocumentMailForm
from ..permissions import (
    permission_send_document_version_attachment,
    permission_send_document_version_link, permission_user_mailer_use
)
from ..tasks import task_send_document_version


class MailDocumentVersionView(MultipleObjectFormActionView):
    as_attachment = True
    form_class = DocumentMailForm
    object_permission = permission_send_document_version_attachment
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

        task_send_document_version.apply_async(
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
    object_permission = permission_send_document_version_link
    success_message = _(
        '%(count)d document version link queued for email delivery'
    )
    success_message_plural = _(
        '%(count)d document version links queued for email delivery'
    )
    title = 'Email document version link'
    title_plural = 'Email document version links'
    title_document = 'Email link for document version: %s'
