from django.urls import path
from . import views
from . import admin_views

app_name = 'polls'
urlpatterns = [
    # मुख्य पोल्स अॅप्लिकेशन URL पॅटर्न
    path('', views.index, name='index'),
    path('<int:poll_id>/', views.detail, name='detail'),
    path('<int:poll_id>/vote/', views.vote, name='vote'),
    path('results/', views.all_results, name='all_results'),
    path('<int:poll_id>/results/', views.poll_results, name='poll_results'),
    path('create/', views.create, name='create'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('my-votes/', views.my_votes, name='my_votes'),
    
    # अॅडमिन पोल्स व्यवस्थापन URL पॅटर्न
    path('admin/polls/', admin_views.admin_polls_list, name='admin_polls_list'),
    path('admin/polls/add/', admin_views.admin_add_poll, name='admin_add_poll'),
    path('admin/polls/<int:poll_id>/', admin_views.admin_poll_detail, name='admin_poll_detail'),
    path('admin/polls/<int:poll_id>/edit/', admin_views.admin_edit_poll, name='admin_edit_poll'),
    path('admin/polls/<int:poll_id>/add-choice/', admin_views.admin_add_choice, name='admin_add_choice'),
    path('admin/polls/<int:poll_id>/choices/<int:choice_id>/edit/', admin_views.admin_edit_choice, name='admin_edit_choice'),
    path('admin/polls/<int:poll_id>/choices/<int:choice_id>/delete/', admin_views.admin_delete_choice, name='admin_delete_choice'),
    path('admin/polls/<int:poll_id>/delete/', admin_views.admin_delete_poll, name='admin_delete_poll'),
    
    # वापरकर्ता व्यवस्थापन URL पॅटर्न
    path('admin/users/', views.manage_users, name='manage_users'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin/users/add/', views.add_user, name='add_user'),
    path('admin/users/<int:user_id>/edit-department/', views.edit_user_department, name='edit_user_department'),
    
    # विभाग व्यवस्थापन URL पॅटर्न
    path('admin/departments/', views.manage_departments, name='manage_departments'),
    path('admin/departments/<int:dept_id>/delete/', views.delete_department, name='delete_department'),
] 