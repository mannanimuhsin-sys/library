from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # ─── Public / View Mode ───────────────────────────────────────────────────
    path('', views.public_home, name='public_home'),
    path('register/', views.register_member, name='register_member'),

    # ─── Admin Auth ───────────────────────────────────────────────────────────
    path('admin-panel/login/', views.admin_login_view, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout_view, name='admin_logout'),

    # ─── Admin Dashboard ─────────────────────────────────────────────────────
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),

    # ─── Book Management ─────────────────────────────────────────────────────
    path('admin-panel/books/', views.book_list, name='book_list'),
    path('admin-panel/books/add/', views.add_book, name='add_book'),
    path('admin-panel/books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('admin-panel/books/<int:pk>/delete/', views.delete_book, name='delete_book'),

    # ─── Member Management ───────────────────────────────────────────────────
    path('admin-panel/members/', views.members_list, name='members_list'),
    path('admin-panel/members/<int:pk>/approve/', views.approve_member, name='approve_member'),
    path('admin-panel/members/<int:pk>/delete/', views.delete_member, name='delete_member'),

    # ─── Issue / Return ──────────────────────────────────────────────────────
    path('admin-panel/issue/', views.issue_book, name='issue_book'),
    path('admin-panel/return/<int:pk>/', views.return_book, name='return_book'),
    path('admin-panel/issue-records/', views.issue_records, name='issue_records'),
]
