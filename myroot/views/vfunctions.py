from datetime import datetime, timedelta
import timeago


def dict_alert_msg(form_is_valid, alert_title, alert_msg, alert_type):
    """
    Function to call internal alert message to the user with the required
    paramaters: form_is_valid[True/False all small letters for json format],
    alert_title='string', alert_msg='string',
    alert_type='success, error, warning, info'
    """
    data = {
        'form_is_valid': form_is_valid,
        'alert_title': alert_title,
        'alert_msg': alert_msg,
        'alert_type': alert_type
    }
    return data


def convert_to_local_datetime(dt_value):
    MY_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
    dt = dt_value
    created_date_str = dt.strftime(MY_DT_FORMAT)  # convert to string
    created_date = dt.strptime(created_date_str, MY_DT_FORMAT)

    # timeago in python library to get user's local time
    now = datetime.now() + timedelta(seconds=60 * 3.4)
    event_date = timeago.format(created_date, now)

    return str(event_date)
