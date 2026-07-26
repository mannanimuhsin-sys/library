from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Book, Member, IssueRecord


# ─────────────────────────────────────────────────────────────────────────────
#  PUBLIC / VIEW MODE
# ─────────────────────────────────────────────────────────────────────────────

def public_home(request):
    """Public view – shows available books, search, and registration."""
    search_query = request.GET.get('search', '')
    books = Book.objects.filter(is_available=True)
    all_books = Book.objects.all()

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(book_number__icontains=search_query) |
            Q(author__icontains=search_query)
        )

    context = {
        'available_books': books,
        'all_books': all_books,
        'search_query': search_query,
        'total_books': all_books.count(),
        'available_count': Book.objects.filter(is_available=True).count(),
        'issued_count': Book.objects.filter(is_available=False).count(),
    }
    return render(request, 'library/public_home.html', context)


def register_member(request):
    """Member self-registration (public)."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        if name and mobile:
            Member.objects.create(name=name, mobile=mobile)
            messages.success(request, f'Registration successful! Your request is pending admin approval.')
            return redirect('library:public_home')
        else:
            messages.error(request, 'Please fill in all fields.')
    return redirect('library:public_home')


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN AUTH
# ─────────────────────────────────────────────────────────────────────────────

def admin_login_view(request):
    """Custom admin login page."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('library:admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('library:admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions.')

    return render(request, 'library/admin_login.html')


def admin_logout_view(request):
    """Logout admin."""
    logout(request)
    return redirect('library:public_home')


# ─────────────────────────────────────────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='library:admin_login')
def admin_dashboard(request):
    """Admin dashboard with statistics."""
    context = {
        'total_books': Book.objects.count(),
        'available_books': Book.objects.filter(is_available=True).count(),
        'issued_books': Book.objects.filter(is_available=False).count(),
        'total_members': Member.objects.count(),
        'pending_members': Member.objects.filter(is_approved=False).count(),
        'approved_members': Member.objects.filter(is_approved=True).count(),
        'active_issues': IssueRecord.objects.filter(is_returned=False).count(),
        'recent_issues': IssueRecord.objects.filter(is_returned=False).order_by('-issued_date')[:5],
        'pending_registrations': Member.objects.filter(is_approved=False).order_by('-registered_date')[:5],
    }
    return render(request, 'library/admin_dashboard.html', context)


# ─────────────────────────────────────────────────────────────────────────────
#  BOOK MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='library:admin_login')
def book_list(request):
    """List all books with filter options."""
    filter_type = request.GET.get('filter', 'all')
    search_query = request.GET.get('search', '')

    books = Book.objects.all()
    if filter_type == 'available':
        books = books.filter(is_available=True)
    elif filter_type == 'issued':
        books = books.filter(is_available=False)

    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(book_number__icontains=search_query) |
            Q(author__icontains=search_query)
        )

    context = {
        'books': books,
        'filter_type': filter_type,
        'search_query': search_query,
    }
    return render(request, 'library/book_list.html', context)


@login_required(login_url='library:admin_login')
def add_book(request):
    """Add a new book."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        book_number = request.POST.get('book_number', '').strip()
        author = request.POST.get('author', '').strip()
        description = request.POST.get('description', '').strip()
        cover_image = request.FILES.get('cover_image')

        if title and book_number:
            if Book.objects.filter(book_number=book_number).exists():
                messages.error(request, f'Book number "{book_number}" already exists.')
            else:
                book = Book.objects.create(
                    title=title,
                    book_number=book_number,
                    author=author,
                    description=description,
                )
                if cover_image:
                    book.cover_image = cover_image
                    book.save()
                messages.success(request, f'Book "{title}" added successfully!')
                return redirect('library:book_list')
        else:
            messages.error(request, 'Title and Book Number are required.')

    return render(request, 'library/add_edit_book.html', {'action': 'Add', 'book': None})


@login_required(login_url='library:admin_login')
def edit_book(request, pk):
    """Edit an existing book."""
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        book.title = request.POST.get('title', book.title).strip()
        book.book_number = request.POST.get('book_number', book.book_number).strip()
        book.author = request.POST.get('author', '').strip()
        book.description = request.POST.get('description', '').strip()
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            book.cover_image = cover_image

        # Check unique book_number (exclude current book)
        if Book.objects.filter(book_number=book.book_number).exclude(pk=pk).exists():
            messages.error(request, f'Book number "{book.book_number}" is already used.')
        else:
            book.save()
            messages.success(request, f'Book "{book.title}" updated successfully!')
            return redirect('library:book_list')

    return render(request, 'library/add_edit_book.html', {'action': 'Edit', 'book': book})


@login_required(login_url='library:admin_login')
def delete_book(request, pk):
    """Delete a book."""
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Book "{title}" deleted.')
        return redirect('library:book_list')
    return render(request, 'library/confirm_delete.html', {'object': book, 'type': 'Book'})


# ─────────────────────────────────────────────────────────────────────────────
#  MEMBER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='library:admin_login')
def members_list(request):
    """List all members – pending and approved."""
    filter_type = request.GET.get('filter', 'all')
    members = Member.objects.all()
    if filter_type == 'pending':
        members = members.filter(is_approved=False)
    elif filter_type == 'approved':
        members = members.filter(is_approved=True)

    context = {
        'members': members,
        'filter_type': filter_type,
        'pending_count': Member.objects.filter(is_approved=False).count(),
        'approved_count': Member.objects.filter(is_approved=True).count(),
    }
    return render(request, 'library/members.html', context)


@login_required(login_url='library:admin_login')
def approve_member(request, pk):
    """Toggle member approval."""
    member = get_object_or_404(Member, pk=pk)
    member.is_approved = not member.is_approved
    member.save()
    status = "approved" if member.is_approved else "revoked"
    messages.success(request, f'Member "{member.name}" has been {status}.')
    return redirect('library:members_list')


@login_required(login_url='library:admin_login')
def delete_member(request, pk):
    """Delete a member."""
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        name = member.name
        member.delete()
        messages.success(request, f'Member "{name}" removed.')
        return redirect('library:members_list')
    return render(request, 'library/confirm_delete.html', {'object': member, 'type': 'Member'})


# ─────────────────────────────────────────────────────────────────────────────
#  ISSUE & RETURN
# ─────────────────────────────────────────────────────────────────────────────

@login_required(login_url='library:admin_login')
def issue_book(request):
    """Issue a book to a person."""
    available_books = Book.objects.filter(is_available=True)
    approved_members = Member.objects.filter(is_approved=True)

    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        member_id = request.POST.get('member_id')
        issued_by_name = request.POST.get('issued_by_name', '').strip()
        issued_date = request.POST.get('issued_date')
        expected_return_date = request.POST.get('expected_return_date') or None

        book = get_object_or_404(Book, pk=book_id, is_available=True)
        member = Member.objects.filter(pk=member_id).first() if member_id else None

        if not issued_by_name:
            messages.error(request, 'Please enter the name of the person receiving the book.')
        elif not issued_date:
            messages.error(request, 'Please select the issue date.')
        else:
            # Create issue record
            IssueRecord.objects.create(
                book=book,
                member=member,
                issued_by_name=issued_by_name,
                issued_date=issued_date,
                expected_return_date=expected_return_date,
            )
            # Mark book as issued
            book.is_available = False
            book.save()
            messages.success(request, f'Book "{book.title}" issued to {issued_by_name} successfully!')
            return redirect('library:issue_records')

    context = {
        'available_books': available_books,
        'approved_members': approved_members,
        'today': timezone.now().date(),
    }
    return render(request, 'library/issue_book.html', context)


@login_required(login_url='library:admin_login')
def return_book(request, pk):
    """Return a book."""
    issue_record = get_object_or_404(IssueRecord, pk=pk, is_returned=False)

    if request.method == 'POST':
        returned_by_name = request.POST.get('returned_by_name', '').strip()
        return_date = request.POST.get('return_date')

        if not returned_by_name:
            messages.error(request, 'Please enter the name of the person returning the book.')
        elif not return_date:
            messages.error(request, 'Please select the return date.')
        else:
            issue_record.returned_by_name = returned_by_name
            issue_record.return_date = return_date
            issue_record.is_returned = True
            issue_record.save()

            # Mark book as available again
            issue_record.book.is_available = True
            issue_record.book.save()

            messages.success(request, f'Book "{issue_record.book.title}" returned successfully and is now available!')
            return redirect('library:issue_records')

    context = {
        'record': issue_record,
        'today': timezone.now().date(),
    }
    return render(request, 'library/return_book.html', context)


@login_required(login_url='library:admin_login')
def issue_records(request):
    """View all issue records."""
    filter_type = request.GET.get('filter', 'active')
    records = IssueRecord.objects.select_related('book', 'member').all()

    if filter_type == 'active':
        records = records.filter(is_returned=False)
    elif filter_type == 'returned':
        records = records.filter(is_returned=True)

    context = {
        'records': records,
        'filter_type': filter_type,
        'active_count': IssueRecord.objects.filter(is_returned=False).count(),
        'returned_count': IssueRecord.objects.filter(is_returned=True).count(),
    }
    return render(request, 'library/issue_records.html', context)
