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
