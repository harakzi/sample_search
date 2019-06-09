from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    # ユーザ名とそのEメールアドレスを合わせて返却
    def __str__(self):
        return self.username + ":" + self.email

# １テーブルに対応するクラス（Excelでいう１シートに該当）
class Post(models.Model):
    """投稿モデル"""
    class Meta:
        db_table = 'post'

    # クラスの属性にDBのカラムを定義
    # verbose_name：フィールド名（列の先頭の名称←カラム名）
    title = models.CharField(verbose_name='タイトル', max_length=255)
    text = models.CharField(verbose_name='内容', max_length=255, default='', blank=True)
    author = models.ForeignKey(
        'search.CustomUser',
        # 参照するオブジェクトが削除されたときに、それと紐づけられたオブジェクトも一緒に削除するのか、それともそのオブジェクトは残しておくのかを設定するもの
        # models.CASCADE：自身のレコードを削除する
        # https://www.djangobrothers.com/blogs/on_delete/
        on_delete=models.CASCADE,
        related_name='posts',
    )
    created_at = models.DateTimeField(verbose_name='登録日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    # 管理サイトに表示される文字列を定義
    def __str__(self):
        # 管理サイトの一件あたりのPostについての表記を指定
        return self.title + ',' + self.text

    @staticmethod
    def get_absolute_url(self):
        return reverse('search:index')