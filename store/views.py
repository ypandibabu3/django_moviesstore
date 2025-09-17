from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from .models import Movie, Review, Order, OrderItem
from .models import ReviewReport
from .forms import SignUpForm, ReviewForm

CART_SESSION_KEY = "cart"

def _get_cart(session):
    cart = session.get(CART_SESSION_KEY)
    if cart is None:
        cart = {}
        session[CART_SESSION_KEY] = cart
    return cart

def _cart_items(cart):
    movie_ids = [int(mid) for mid in cart.keys()]
    movies = {m.id: m for m in Movie.objects.filter(id__in=movie_ids)}
    items = []
    total = Decimal("0.00")
    for mid, qty in cart.items():
        m = movies.get(int(mid))
        if not m:
            continue
        line_total = Decimal(str(m.price)) * qty
        total += line_total
        items.append({"movie": m, "quantity": qty, "line_total": line_total})
    return items, total

def home(request):
    return render(request, "home.html")

def movie_list(request):
    q = request.GET.get("q", "").strip()
    movies = Movie.objects.all()
    if q:
        movies = movies.filter(Q(title__icontains=q) | Q(description__icontains=q))
    movies = movies.annotate(
        avg_rating=Avg("reviews__rating"),
        review_count=Count("reviews")
    )
    return render(request, "movies/list.html", {"movies": movies, "q": q})

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    reviews = movie.reviews.select_related("user").order_by("-created_at")
    # Exclude reviews that the current user has reported (so they disappear for that user)
    if request.user.is_authenticated:
        reported_qs = ReviewReport.objects.filter(user=request.user).values_list("review_id", flat=True)
        reviews = reviews.exclude(id__in=reported_qs)
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
    form = ReviewForm()
    return render(
        request,
        "movies/detail.html",
        {"movie": movie, "reviews": reviews, "user_review": user_review, "form": form},
    )


@login_required
def report_review(request, pk):
    """Create a Report for a review so it will be hidden for the reporting user.

    Accepts POST with optional `reason`. Redirects back to movie_detail.
    """
    review = get_object_or_404(Review, pk=pk)
    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        # Create or ignore duplicate reports by the same user
        ReviewReport.objects.get_or_create(review=review, user=request.user, defaults={"reason": reason})
    return redirect("movie_detail", pk=review.movie_id)

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("movie_list")
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            existing = Review.objects.filter(movie=movie, user=request.user).first()
            if existing:
                existing.rating = form.cleaned_data["rating"]
                existing.text = form.cleaned_data["text"]
                existing.save()
            else:
                Review.objects.create(
                    movie=movie,
                    user=request.user,
                    rating=form.cleaned_data["rating"],
                    text=form.cleaned_data["text"],
                )
            return redirect("movie_detail", pk=movie.id)
    return redirect("movie_detail", pk=movie.id)

@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("movie_detail", pk=review.movie_id)
    else:
        form = ReviewForm(instance=review)
    return render(request, "movies/review_form.html", {"form": form, "movie": review.movie, "edit": True})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    movie_id = review.movie_id
    if request.method == "POST":
        review.delete()
        return redirect("movie_detail", pk=movie_id)
    return render(request, "movies/review_confirm_delete.html", {"review": review})

def cart_detail(request):
    cart = _get_cart(request.session)
    items, total = _cart_items(cart)
    return render(request, "cart/detail.html", {"items": items, "total": total})

def cart_add(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    cart = _get_cart(request.session)
    qty = cart.get(str(movie.id), 0)
    cart[str(movie.id)] = qty + 1
    request.session.modified = True
    return redirect("cart_detail")

def cart_remove(request, movie_id):
    cart = _get_cart(request.session)
    mid = str(movie_id)
    if mid in cart:
        if cart[mid] > 1:
            cart[mid] -= 1
        else:
            del cart[mid]
        request.session.modified = True
    return redirect("cart_detail")

def cart_clear(request):
    if CART_SESSION_KEY in request.session:
        del request.session[CART_SESSION_KEY]
        request.session.modified = True
    return redirect("cart_detail")

@login_required
def checkout(request):
    cart = _get_cart(request.session)
    items, total = _cart_items(cart)
    if not items:
        return redirect("cart_detail")
    order = Order.objects.create(user=request.user)
    for it in items:
        OrderItem.objects.create(
            order=order,
            movie=it["movie"],
            quantity=it["quantity"],
            price=it["movie"].price,
        )
    if CART_SESSION_KEY in request.session:
        del request.session[CART_SESSION_KEY]
        request.session.modified = True
    return redirect("order_list")

@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related("items__movie").order_by("-created_at")
    return render(request, "orders/list.html", {"orders": orders})