
from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view

schema_view = get_schema_view(title='ListSample API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('search.urls')),  # ホームURLに設定
    path('api-auth/', include('rest_framework.urls')),  # API認証
    path('schema/', schema_view),  # APIスキーマ
]
