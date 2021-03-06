from django.db import models
from django.db.models.aggregates import Count

from .utils import extract_user_data_from_update


class Proposal(models.Model):
    ref_id = models.CharField(max_length=2000, unique=True)
    title = models.CharField(max_length=2000)
    protocol = models.CharField(max_length=2000)
    current_state = models.CharField(max_length=256)
    results = models.JSONField()
    total_votes = models.IntegerField()
    next_reminder = models.IntegerField()


class BotChatUser(models.Model):
    user_id = models.CharField(max_length=250, unique=True)
    username = models.CharField(max_length=250, blank=True, null=True)
    alerting = models.BooleanField(default=False)
    is_blocked_bot = models.BooleanField(default=False)

    def __str__(self):
        return f"@{self.username}" if self.username is not None else f"{self.user_id}"

    @classmethod
    def get_user_and_created(cls, update, context):
        """python-telegram-bot's Update, Context --> User instance."""
        data = extract_user_data_from_update(update)
        return cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

    @classmethod
    def get_user(cls, update, context):
        u, _ = cls.get_user_and_created(update, context)
        return u


class Subscription(models.Model):
    user = models.ForeignKey(BotChatUser, on_delete=models.CASCADE)
    ref_id = models.CharField(max_length=2000)
    proposal_title = models.CharField(max_length=2000)
    protocol = models.CharField(max_length=256)

    class Meta:
        unique_together = ("user", "ref_id")

    @classmethod
    def top_protocols(cls) -> list:
        tops = []
        result = (
            Subscription.objects.values("protocol")
            .annotate(count=Count("protocol"))
            .order_by("-count")[:10]
        )
        for res in result:
            tops.append(res["protocol"])
        return tops

    @classmethod
    def top_proposals(cls) -> dict:
        tops = {}
        result = (
            Subscription.objects.values("ref_id", "proposal_title")
            .annotate(count=Count("ref_id"))
            .order_by("-count")[:10]
        )
        for res in result:
            tops[res["proposal_title"]] = res["ref_id"]
        return tops
