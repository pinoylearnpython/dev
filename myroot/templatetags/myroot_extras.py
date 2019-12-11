from django import template

register = template.Library()

@register.simple_tag
def split_me(strings):
    """
    Function to split strings into an array to loop later
    from the template.
    """
    splited_values = strings.split(",")
    return splited_values
