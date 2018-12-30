from django.urls import path

# Call all ads app properties
import bp.views

urlpatterns = [
    # BP related urls
    path('mybusinesslistings/', bp.views.mybusinesslistings_view,
         name='mybusinesslistings'),

    path('<slug:slug>-<int:id>-bp/', bp.views.bp_view, name='bp'),

    path('search_bp_text/', bp.views.search_bp_text_view,
         name='search_bp_text'),

    path('search_bp_dr/', bp.views.search_bp_dr_view,
         name='search_bp_dr'),

    path('del_row_bp/', bp.views.del_row_bp_view,
         name='del_row_bp'),

    path('bp/add/', bp.views.add_bp_view, name='add_bp'),

    path('bp/<int:id>/change/', bp.views.change_bp_view,
         name='change_bp'),

    path('all_user_business_tags/',
         bp.views.get_all_user_business_tags_json_view,
         name='all_user_business_tags'),

    path('change_company_logo/', bp.views.change_company_logo_view,
         name='change_company_logo'),

    path('submitbp_comment/', bp.views.submitbp_comment_view,
         name='submitbp_comment'),

    path('submitbp_review/', bp.views.submitbp_review_view,
         name='submitbp_review'),

    path('submitbp_inquiry/', bp.views.submitbp_inquiry_view,
         name='submitbp_inquiry'),

    path('searchbp/', bp.views.searchbp_view,
         name='searchbp'),

    path('businesstag/<slug:slug>/',
         bp.views.business_tags_view, name='businesstag'),

    path('reviews/', bp.views.bp_reviews_view,
         name='reviews'),

    path('del_row_bp_review/', bp.views.del_row_bp_review_view,
         name='del_row_bp_review'),

    path('reading_pane_bp_review/', bp.views.reading_pane_bp_review_view,
         name='reading_pane_bp_review'),

    path('review/<int:id>/read/', bp.views.read_bp_review_view,
         name='review'),

    path('inquiries/', bp.views.inquiries_view,
         name='inquiries'),

    path('del_row_bp_inquiry/', bp.views.del_row_bp_inquiry_view,
         name='del_row_bp_inquiry'),

    path('reading_pane_bp_inquiry/', bp.views.reading_pane_bp_inquiry_view,
         name='reading_pane_bp_inquiry'),

    path('inquiry/<int:id>/read/', bp.views.read_bp_inquiry_view,
         name='inquiry'),

    path('comments/', bp.views.comments_view,
         name='comments'),

    path('del_row_bp_comment/', bp.views.del_row_bp_comment_view,
         name='del_row_bp_comment'),

    path('reading_pane_bp_comment/', bp.views.reading_pane_bp_comment_view,
         name='reading_pane_bp_comment'),

    path('comment/<int:id>/read/', bp.views.read_bp_comment_view,
         name='comment'),

    path('notify_marked_sel_read_bp/', bp.views.notify_marked_sel_read_bp_view,
         name='notify_marked_sel_read_bp'),

    path('bpnotify/', bp.views.bpnotify_view,
         name='bpnotify'),

    path('del_logo/', bp.views.del_logo_view,
         name='del_logo'),

    path('copy_bp/', bp.views.copy_bp_view,
         name='copy_bp'),

    # Redirect from old to new urls
    # old url: https://www.minedbp.com/mybusiness/about
    path('advertise.php/', bp.views.old_url_advert_view,
         name='old_url_advert'),

    path('mybusiness/about/', bp.views.old_url_about_view,
         name='old_url_about'),

    path('mybusiness/contactus/', bp.views.old_url_contact_us_view,
         name='old_url_contact_us'),

    path('mybusiness/register/', bp.views.old_url_register_view,
         name='old_url_register'),

    path('mybusiness/login/', bp.views.old_url_login_view,
         name='old_url_login'),

    path('mybusiness/forgot/', bp.views.old_url_forgot_view,
         name='old_url_forgot'),

    path('mybusiness/', bp.views.old_url_mybusiness_view,
         name='old_url_mybusiness'),

    path('<int:id>/<slug:slug>/', bp.views.old_url_co_view,
         name='old_url_co'),

    path('businesstag/<int:id>/<slug:slug>/', bp.views.old_url_category_view,
         name='old_url_category'),

    path('mail/', bp.views.mail_view, name='mail'),
]
