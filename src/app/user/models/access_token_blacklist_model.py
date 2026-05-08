from django.db import models


class AccessTokenBlacklist(models.Model):
    jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Access Token 黑名單"
        verbose_name_plural = "Access Token 黑名單"
