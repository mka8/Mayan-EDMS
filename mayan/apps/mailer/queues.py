from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_c

queue_mailing = CeleryQueue(
    label=_('Mailing'), name='mailing', worker=worker_c
)

queue_mailing.add_task_type(
    label=_('Send document'),
    dotted_path='mayan.apps.mailer.tasks.task_send_document'
)
queue_mailing.add_task_type(
    label=_('Send document file'),
    dotted_path='mayan.apps.mailer.tasks.task_send_document_file'
)
queue_mailing.add_task_type(
    label=_('Send document version'),
    dotted_path='mayan.apps.mailer.tasks.task_send_document_version'
)
