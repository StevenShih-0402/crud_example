from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    自訂使用者模型，繼承 AbstractUser。

    AbstractUser 已內建：username、email、password、first_name、last_name、
    is_staff、is_active、date_joined 等欄位，以及完整的密碼雜湊機制。
    在此額外新增 phone 欄位作為擴充示範。
    """

    phone = models.CharField(max_length=20, blank=True, verbose_name="電話")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "使用者"
        verbose_name_plural = "使用者"
