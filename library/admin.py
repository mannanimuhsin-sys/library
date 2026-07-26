from django.contrib import admin
from .models import Book, Member, IssueRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_number', 'title', 'author', 'is_available', 'added_date')
    list_filter = ('is_available',)
    search_fields = ('title', 'author', 'book_number')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'registered_date', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'mobile')


@admin.register(IssueRecord)
class IssueRecordAdmin(admin.ModelAdmin):
    list_display = ('book', 'issued_by_name', 'issued_date', 'is_returned', 'return_date')
    list_filter = ('is_returned',)
    search_fields = ('issued_by_name', 'book__title')