from django.core import mail

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from ..events import event_email_sent
from ..permissions import (
    permission_send_document_file_attachment,
    permission_send_document_file_link, permission_user_mailer_use
)

from .literals import TEST_EMAIL_ADDRESS, TEST_EMAIL_FROM_ADDRESS
from .mixins import DocumentFileMailerViewTestMixin, MailerTestMixin


class MailDocumentFileViewTestCase(
    DocumentFileMailerViewTestMixin, MailerTestMixin, GenericDocumentViewTestCase
):
    def test_document_file_send_link_view_no_permission(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self._clear_events()

        response = self._request_test_document_file_send_link_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), mail_messages)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_file_send_link_view_with_access(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self.grant_access(
            obj=self.test_document,
            permission=permission_send_document_file_link
        )
        self.grant_access(
            obj=self.test_user_mailer, permission=permission_user_mailer_use
        )

        self._clear_events()

        response = self._request_test_document_file_send_link_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), mail_messages + 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self.test_document_file)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)

    def test_trashed_document_file_send_link_view_with_access(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self.grant_access(
            obj=self.test_document,
            permission=permission_send_document_file_link
        )
        self.grant_access(
            obj=self.test_user_mailer, permission=permission_user_mailer_use
        )

        self.test_document.delete()

        self._clear_events()

        response = self._request_test_document_file_send_link_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), mail_messages)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_file_send_view_no_permission(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self._clear_events()

        response = self._request_test_document_file_send_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), mail_messages)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_document_file_send_view_with_access(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self.grant_access(
            obj=self.test_document,
            permission=permission_send_document_file_attachment
        )
        self.grant_access(
            obj=self.test_user_mailer, permission=permission_user_mailer_use
        )

        self._clear_events()

        response = self._request_test_document_file_send_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(len(mail.outbox), mail_messages + 1)
        self.assertEqual(mail.outbox[0].from_email, TEST_EMAIL_FROM_ADDRESS)
        self.assertEqual(mail.outbox[0].to, [TEST_EMAIL_ADDRESS])

        events = self._get_test_events()
        self.assertEqual(events.count(), 1)

        self.assertEqual(events[0].action_object, self.test_document_file)
        self.assertEqual(events[0].actor, self._test_case_user)
        self.assertEqual(events[0].target, self.test_user_mailer)
        self.assertEqual(events[0].verb, event_email_sent.id)

    def test_trashed_document_file_send_view_with_access(self):
        self._create_test_user_mailer()

        mail_messages = len(mail.outbox)

        self.grant_access(
            obj=self.test_document,
            permission=permission_send_document_file_attachment
        )
        self.grant_access(
            obj=self.test_user_mailer, permission=permission_user_mailer_use
        )

        self.test_document.delete()

        self._clear_events()

        response = self._request_test_document_file_send_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(len(mail.outbox), mail_messages)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)
