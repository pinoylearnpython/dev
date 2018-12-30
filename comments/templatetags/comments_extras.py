from django.conf import settings
from bp.models import (Business, BusinessReview, BusinessTag)
from django.db.models import Count
from myroot.views.vcommon import math_divide

# Call bp properties
from bp.common import (get_bp_reviews, load_bp_reviews, sum_bp_reviews_rate)

from django import template
register = template.Library()


@register.simple_tag
def count_bp_reviews_rate(business_id, rate):
    """
    Function to get the total sum of business reviews rating.
    """
    bp_rate_count = BusinessReview.objects.using(
            settings.APP_LABEL_BP
            ).values('rate').annotate(tot_rate=Count('rate')).filter(
                    is_active=True, is_deleted=False, business_id=business_id,
                    rate=rate)
    return bp_rate_count


@register.simple_tag
def bp_star_rating(tot_group_rate, oa_reviews):
    """
    Function to compute business review per star rating
    star_rate = tot_group_rate / oa_reviews * 100%
    """
    star_rate = (int(tot_group_rate) / int(oa_reviews)) * 100
    m = round(star_rate, 2)
    return m


@register.simple_tag
def get_bp_review_rating(business_id):
    """
    Function to get bp review rating.
    """
    star_rate = 0

    bp_reviews = str(get_bp_reviews(business_id))
    bp_reviews_data = load_bp_reviews(business_id)
    bp_tot_rates = str(sum_bp_reviews_rate(business_id))
    star_rate = int(math_divide(int(bp_tot_rates), int(bp_reviews)))

    return star_rate
