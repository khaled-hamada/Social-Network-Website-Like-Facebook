from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

@receiver(post_save, sender = get_user_model(), dispatch_uid = "create_new_profile")
def create_new_profile(sender, **kwargs):
    user = kwargs['instance']
    created = kwargs['created']
    if created: # new user instance
        Profile.objects.create(user = user)
