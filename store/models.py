from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField()
    # New: optional uploaded image (preferred). Keep `image_url` as a fallback for external images.
    image = models.ImageField(upload_to="movies/images/", blank=True, null=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("movie", "user")

    def __str__(self):
        return f"{self.movie.title} – {self.user.username} ({self.rating})"

class ReviewReport(models.Model):
    """Track which reviews have been reported by which users.

    This allows reported reviews to be hidden for the reporting user without
    deleting the review for everyone.
    """
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_reviews")
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("review", "user")

    def __str__(self):
        return f"Report by {self.user.username} for review {self.review_id}"
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_amount(self):
        return sum(item.quantity * item.price for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} on {self.created_at:%Y-%m-%d}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=7, decimal_places=2)

    def line_total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.movie.title} x {self.quantity}"


# NEW PETITION MODELS
class Petition(models.Model):
    """Movie petition that users can create to request movies be added to catalog"""
    movie_title = models.CharField(max_length=200)
    description = models.TextField(help_text="Why should this movie be added?")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petitions")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def yes_votes_count(self):
        return self.votes.filter(vote_type='yes').count()
    
    def no_votes_count(self):
        return self.votes.filter(vote_type='no').count()
    
    def total_votes_count(self):
        return self.votes.count()
    
    def user_has_voted(self, user):
        """Check if a user has already voted on this petition"""
        if not user.is_authenticated:
            return False
        return self.votes.filter(user=user).exists()
    
    def user_vote(self, user):
        """Get the user's vote on this petition if it exists"""
        if not user.is_authenticated:
            return None
        vote = self.votes.filter(user=user).first()
        return vote.vote_type if vote else None

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Petition for '{self.movie_title}' by {self.creator.username}"


class PetitionVote(models.Model):
    """Track votes on petitions"""
    VOTE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]
    
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petition_votes")
    vote_type = models.CharField(max_length=3, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("petition", "user")  # One vote per user per petition

    def __str__(self):
        return f"{self.user.username} voted '{self.vote_type}' on {self.petition.movie_title}"