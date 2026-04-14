from django.db import models


class Book(models.Model):
    """
    書本模型，用於存儲書本相關信息。
    """
    book_name = models.CharField(max_length=30, verbose_name="書籍名稱")
    description = models.CharField(max_length=255, verbose_name="書籍描述")
    writer = models.CharField(max_length=30, verbose_name="作者")
    publish_date = models.DateField(verbose_name="出版日期")

    created_at = models.DateTimeField(null=True, blank=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(null=True, blank=True, verbose_name="修改時間")

    # Django 會自動為每個 model 類別創建一個名為 .objects 的 manager。
    objects = models.Manager()

    def __str__(self):
        return f"{self.book_name}" or "書本"

    class Meta:
        verbose_name = '書本'
        verbose_name_plural = '書本'
