from django.db import models

# Create your models here.
class Proposal(models.Model):
    p_id = models.CharField(unique=True, max_length=250)
    ref_id = models.TextField()


class BotChatUser(models.Model):
    user_bot_id = models.CharField(max_length=250, unique=True)


class ProposalVoteSibscribe(models.Model):
    user = models.ForeignKey(BotChatUser, on_delete=models.CASCADE)
    ref_id = models.CharField(max_length=2000)

    class Meta:
        unique_together = ('user', 'ref_id')


class VotersVoteSubscribe(models.Model):
    user = models.ForeignKey(BotChatUser, on_delete=models.CASCADE)
    address = models.CharField(max_length=250)

    class Meta:
        unique_together = ('user', 'address')