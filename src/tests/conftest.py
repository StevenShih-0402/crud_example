"""測試共用的 fixtures。

本專案的端點測試一律「不碰資料庫」：
Service 層（以及 DRF 為 unique 欄位自動加上的驗證器）都在各測試中以 mock
取代，因此不需要 pytest.mark.django_db，測試跑起來快且不受既有資料影響。
"""

import pytest
from rest_framework.test import APIClient


class StubUser:
    is_authenticated = True
    is_active = True

    def __init__(self, username: str = "tester", is_staff: bool = False):
        self.pk = 1
        self.username = username
        self.is_staff = is_staff

    def __str__(self):
        return self.username


@pytest.fixture
def api_client() -> APIClient:
    """未登入的 API client。"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client: APIClient) -> APIClient:
    """一般已登入使用者：端點只要求 IsAuthenticated。
    """
    api_client.force_authenticate(user=StubUser())
    return api_client


@pytest.fixture
def admin_client(api_client: APIClient) -> APIClient:
    """管理員：users 端點的 IsAdminUser 要求 is_staff=True。"""
    api_client.force_authenticate(user=StubUser(username="admin", is_staff=True))
    return api_client
