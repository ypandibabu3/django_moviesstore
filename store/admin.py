from django.contrib import admin
from .models import Movie, Review, ReviewReport, Order, OrderItem, Petition, PetitionVote

admin.site.register(Movie)
admin.site.register(Review)
admin.site.register(ReviewReport)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Petition)
admin.site.register(PetitionVote)