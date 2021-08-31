from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.documents.models import Document
from mayan.apps.organizations.utils import get_organization_installation_url
from mayan.apps.views.generics import MultipleObjectFormActionView

from ..forms import DocumentMailForm
from ..permissions import (
    permission_send_document_link, permission_user_mailer_use
)
from ..tasks import task_send_document


class MailDocumentView(MultipleObjectFormActionView):
    form_class = DocumentMailForm
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid

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
            'user': self.request.user
        }

    def object_action(self, form, instance):
        AccessControlList.objects.check_access(
            obj=form.cleaned_data['user_mailer'],
            permissions=(permission_user_mailer_use,), user=self.request.user
        )

        task_send_document.apply_async(
            kwargs={
                'body': form.cleaned_data['body'],
                'document_id': instance.pk,
                'organization_installation_url': get_organization_installation_url(
                    request=self.request
                ),
                'recipient': form.cleaned_data['email'],
                'sender': self.request.user.email,
                'subject': form.cleaned_data['subject'],
                'user_mailer_id': form.cleaned_data['user_mailer'].pk
            }
        )


class MailDocumentLinkView(MailDocumentView):
    object_permission = permission_send_document_link
    success_message = _('%(count)d document link queued for email delivery')
    success_message_plural = _(
        '%(count)d document links queued for email delivery'
    )
    title = 'Email document link'
    title_plural = 'Email document links'
    title_document = 'Email link for document: %s'
