from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("movies/", views.movie_list, name="movie_list"),
    path("movies/<int:pk>/", views.movie_detail, name="movie_detail"),

    path("signup/", views.signup, name="signup"),

    path("reviews/add/<int:movie_id>/", views.add_review, name="add_review"),
    path("reviews/<int:pk>/edit/", views.edit_review, name="edit_review"),
    path("reviews/<int:pk>/delete/", views.delete_review, name="delete_review"),
    path("reviews/<int:pk>/report/", views.report_review, name="report_review"),

    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:movie_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:movie_id>/", views.cart_remove, name="cart_remove"),
    path("cart/clear/", views.cart_clear, name="cart_clear"),

    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_list, name="order_list"),
    
    # Petition URLs
    path("petitions/", views.petition_list, name="petition_list"),
    path("petitions/<int:petition_id>/vote/", views.petition_vote, name="petition_vote"),
    path("petitions/<int:petition_id>/delete/", views.petition_delete, name="petition_delete"),
]