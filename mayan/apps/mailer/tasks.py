from django.apps import apps

from mayan.celery import app


@app.task(ignore_result=True)
def task_send_document(
    body, sender, subject, recipient, user_mailer_id, document_id=None,
    organization_installation_url=None
):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    UserMailer = apps.get_model(
        app_label='mailer', model_name='UserMailer'
    )

    if document_id:
        document = Document.objects.get(pk=document_id)
    else:
        document = None

    user_mailer = UserMailer.objects.get(pk=user_mailer_id)

    user_mailer.send_document(
        body=body, document=document,
        organization_installation_url=organization_installation_url,
        subject=subject, to=recipient
    )


@app.task(ignore_result=True)
def task_send_document_file(
    body, sender, subject, recipient, user_mailer_id, as_attachment=False,
    document_file_id=None, organization_installation_url=None
):
    DocumentFile = apps.get_model(
        app_label='documents', model_name='DocumentFile'
    )
    UserMailer = apps.get_model(
        app_label='mailer', model_name='UserMailer'
    )

    if document_file_id:
        document_file = DocumentFile.objects.get(pk=document_file_id)
    else:
        document_file = None

    user_mailer = UserMailer.objects.get(pk=user_mailer_id)

    user_mailer.send_document_file(
        as_attachment=as_attachment, body=body, document_file=document_file,
        organization_installation_url=organization_installation_url,
        subject=subject, to=recipient
    )


@app.task(ignore_result=True)
def task_send_document_version(
    body, sender, subject, recipient, user_mailer_id, as_attachment=False,
    document_version_id=None, organization_installation_url=None
):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )
    UserMailer = apps.get_model(
        app_label='mailer', model_name='UserMailer'
    )

    if document_version_id:
        document_version = DocumentVersion.objects.get(pk=document_version_id)
    else:
        document_version = None

    user_mailer = UserMailer.objects.get(pk=user_mailer_id)

    user_mailer.send_document_version(
        as_attachment=as_attachment, body=body, document_version=document_version,
        organization_installation_url=organization_installation_url,
        subject=subject, to=recipient
    )
