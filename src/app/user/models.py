# 保留此檔案讓 Django 的 app registry 正常運作。
# 實際模型定義在 models/user_model.py。
from app.user.models.user_model import CustomUser

__all__ = ["CustomUser"]
