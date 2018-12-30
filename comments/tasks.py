from django.conf import settings
from celery.decorators import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import arrow
from dynamic_db_router import in_database

# Call myroot properties
from myroot.views.vemail import do_send_email

# Call bp properties
from bp.models import (BusinessNotifications,
                       BusinessNotificationsRead,
                       BusinessTag)


@task(name="task_bp_comment_send_mail")
def bp_comment_send_mail(full_name, bp_email, comment,
                         bp_profile_link, bp_company_name, GET_USER_TZN):
    # Form information submitted by the user
    do_send_email('email_bp_comment.html',
                  'New comment from ' + full_name,
                  settings.APP_EMAIL_FROM,
                  (bp_email,),
                  'Thank you for your comment!',
                  arrow.utcnow().to(GET_USER_TZN).format('MMM DD, YYYY hh:mm a'),
                  'Awesome!',
                  full_name,
                  None,
                  (settings.APP_EMAIL_BCC,),
                  comment,
                  bp_profile_link,
                  bp_company_name
                  )


@task(name="task_bp_review_send_mail")
def bp_review_send_mail(full_name, bp_email, review, bp_profile_link,
                        bp_company_name, RATE, GET_USER_TZN):
    # Form information submitted by the user
    do_send_email('email_bp_review.html',
                  'New business review from ' + full_name,
                  settings.APP_EMAIL_FROM,
                  (bp_email,),
                  'Thank you for your business review!',
                  arrow.utcnow().to(GET_USER_TZN).format('MMM DD, YYYY hh:mm a'),
                  'Awesome!',
                  full_name,
                  None,
                  (settings.APP_EMAIL_BCC,),
                  review,
                  bp_profile_link,
                  bp_company_name,
                  RATE
                  )


@task(name="task_bp_inquiry_send_mail")
def bp_inquiry_send_mail(full_name, bp_email, inquiry, bp_profile_link,
                         bp_company_name, author_email, subject, GET_USER_TZN):
    # Form information submitted by the user
    do_send_email('email_bp_inquiry.html',
                  'New business inquiry from ' + full_name,
                  settings.APP_EMAIL_FROM,
                  (bp_email,),
                  'Thank you for your business inquiry!',
                  arrow.utcnow().to(GET_USER_TZN).format('MMM DD, YYYY hh:mm a'),
                  'Awesome!',
                  full_name,
                  None,
                  (settings.APP_EMAIL_BCC,),
                  inquiry,
                  bp_profile_link,
                  bp_company_name,
                  author_email,
                  subject
                  )


@task(name="task_mark_all_read_notifications_bp")
def mark_all_read_notifications_bp(user_id):
    # Execute the celery task to marked all read bp notifications when
    # accessing the 'notifications' page only.
    all_unread = BusinessNotifications.objects.raw("""SELECT a.id, COUNT(CASE WHEN c.notify_id IS NULL THEN 0 END) AS mNotify_Tot_UnRead
                                         FROM minedbp_bp.bp_business_notification a
                                         JOIN minedbp_bp.bp_business b ON b.id = a.business_id AND b.created_by = %s
                                         LEFT JOIN minedbp_bp.bp_business_notification_read c ON c.notify_id = a.id
                                         WHERE c.notify_id IS NULL
                                         GROUP BY a.id""", [user_id])

    if all_unread:
        with in_database(settings.APP_LABEL_BP, write=True):
            for n in all_unread:
                # Insert new read status
                BusinessNotificationsRead.objects.create(
                    notify_id=n.id,
                    user_id=user_id
                )


@periodic_task(
    run_every=(crontab(hour=0, minute=5)),
    name="task-del-business-tags",
    ignore_result=True
)
def del_business_tags():
    """
    Cronjob to automatically delete all business tags
    marked as 'is_deleted=True'.
    This task will be executed every day at 12:05 AM.
    """
    BusinessTag.objects.using(settings.APP_LABEL_BP).filter(is_deleted=True).delete()
