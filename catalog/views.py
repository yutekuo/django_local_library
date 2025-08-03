from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.views import generic

# Create your views here.
from .models import Author, Book, BookInstance, Genre


def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    num_genres_fantasy = Genre.objects.filter(name__icontains="fantasy").count()
    num_books_contain_the = Book.objects.filter(title__icontains="the").count()

    num_visits = request.session.get("num_visits", 0)
    num_visits += 1
    request.session["num_visits"] = num_visits

    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_genres_fantasy": num_genres_fantasy,
        "num_books_contain_the": num_books_contain_the,
        "num_visits": num_visits,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 5


class BookDetailView(generic.DetailView):
    model = Book


class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5


class AuthorDetailView(generic.DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 3

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class AllLoanedBooksListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = "catalog/bookinstance_list_all_borrowed_books.html"
    paginate_by = 5
    permission_required = "catalog.can_mark_returned"

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact="o").order_by("due_back")
