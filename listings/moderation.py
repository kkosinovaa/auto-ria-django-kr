import re

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q

from .models import Listing, ForbiddenWord


def has_bad_words(listing):
    text = f"{listing.title} {listing.description}"

    words = ForbiddenWord.objects.values_list("word", flat=True)

    for word in words:
        pattern = rf"(?<!\w){re.escape(word)}(?!\w)"

        if re.search(pattern, text, flags=re.IGNORECASE):
            return True

    return False


def notify_managers(listing):
    User = get_user_model()

    emails = list(
        User.objects.filter(is_active=True)
        .filter(Q(groups__name="Manager") | Q(is_superuser=True))
        .exclude(email="")
        .values_list("email", flat=True)
        .distinct()
    )

    if emails:
        send_mail(
            subject="Listing requires moderation",
            message=f"Listing #{listing.id}: {listing.title}",
            from_email=None,
            recipient_list=emails,
        )


def moderate_listing(listing, is_edit=False):
    if has_bad_words(listing):
        if is_edit:
            listing.moderation_attempts += 1

        if listing.moderation_attempts >= 3:
            listing.status = Listing.Status.INACTIVE
        else:
            listing.status = Listing.Status.NEEDS_EDIT
    else:
        listing.status = Listing.Status.ACTIVE
        listing.moderation_attempts = 0

    listing.save(
        update_fields=[
            "status",
            "moderation_attempts",
            "updated_at",
        ]
    )

    if listing.status == Listing.Status.INACTIVE:
        notify_managers(listing)
