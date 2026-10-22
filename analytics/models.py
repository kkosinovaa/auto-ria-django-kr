from django.db import models


class ListingView(models.Model):
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="listing_views"
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Listing {self.listing_id}"
