from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.plans.models import Subscription

from .profile import Profile
from .user import User


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def sync_user_subscription_permissions(sender, instance, **kwargs):
    if not instance.school_id:
        return

    subscription = (
        Subscription.objects.filter(school=instance.school)
        .order_by("-start_date")
        .first()
    )

    if subscription and subscription.is_current:
        subscription.apply_permissions_to_school_users()