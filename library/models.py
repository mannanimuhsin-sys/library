from django.db import models
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=200, verbose_name="Book Title")
    book_number = models.CharField(max_length=50, unique=True, verbose_name="Book Number")
    author = models.CharField(max_length=150, blank=True, null=True, verbose_name="Author")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name="Cover Image")
    is_available = models.BooleanField(default=True, verbose_name="Available")
    added_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['book_number']
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"[{self.book_number}] {self.title}"


class Member(models.Model):
    name = models.CharField(max_length=150, verbose_name="Full Name")
    mobile = models.CharField(max_length=15, verbose_name="Mobile Number")
    registered_date = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False, verbose_name="Approved")

    class Meta:
        ordering = ['-registered_date']
        verbose_name = "Member"
        verbose_name_plural = "Members"

    def __str__(self):
        return f"{self.name} ({self.mobile})"


class IssueRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issue_records', verbose_name="Book")
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='issue_records', verbose_name="Member")
    issued_by_name = models.CharField(max_length=150, verbose_name="Issued To (Name)")
    issued_date = models.DateField(verbose_name="Issue Date")
    expected_return_date = models.DateField(blank=True, null=True, verbose_name="Expected Return Date")
    return_date = models.DateField(blank=True, null=True, verbose_name="Actual Return Date")
    returned_by_name = models.CharField(max_length=150, blank=True, null=True, verbose_name="Returned By")
    is_returned = models.BooleanField(default=False, verbose_name="Returned")

    class Meta:
        ordering = ['-issued_date']
        verbose_name = "Issue Record"
        verbose_name_plural = "Issue Records"

    def __str__(self):
        status = "Returned" if self.is_returned else "Issued"
        return f"{self.book.title} → {self.issued_by_name} [{status}]"