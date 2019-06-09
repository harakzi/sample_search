import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .forms import SearchForm, PostForm
from django.db.models import Q
from django.shortcuts import render, redirect, reverse
from search.models import Post
from search.serializers import PostSerializer, UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from search.models import CustomUser
from rest_framework import permissions
from search.permissions import IsOwnerOrReadOnly
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import action

logger = logging.getLogger('development')


# このビュークラスに飛んできたリクエストは、LoginRequiredMixinによって一度ユーザ認証画面に遷移される？
class IndexView(LoginRequiredMixin, generic.ListView):

    # デフォルト変数のオーバーライド→ページングする際の１ページあたりの最大件数
    paginate_by = 5
    # デフォルト変数のオーバーライド→利用するテンプレートを上書き
    template_name = 'search/index.html'
    # こちらもオーバーライド→取り扱うモデルクラスを上書き
    model = Post

    # セッションに検索フォームの値を渡す
    def post(self, request, *args, **kwargs):

        # 検索フォームに何も入力されずにボタンが押下されたときの挙動を記述
        form_value = [
            self.request.POST.get('title', None),
            self.request.POST.get('text', None),
        ]
        request.session['form_value'] = form_value

        # 検索時にページネーションに関連したエラーを防ぐ??
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()

        return self.get(request, *args, **kwargs)

    # セッションから検索フォームの値を取得して、検索フォームの初期値としてセットする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sessionに値がある場合、その値をセットする。（ページングしてもform値が変わらないように）
        title = ''
        text = ''
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            # ユーザによって入力された値をセットする
            title = form_value[0]
            text = form_value[1]

        # ディクショナリ
        default_data = {'title': title,  # タイトル
                        'text': text,  # 内容
                        }

        test_form = SearchForm(initial=default_data) # 検索フォーム
        context['test_form'] = test_form

        return context

    # セッションから取得した検索フォームの値に応じてクエリを発行する。
    def get_queryset(self):

        # sessionに値がある場合、その値でクエリ発行する。
        if 'form_value' in self.request.session:
            form_value = self.request.session['form_value']
            title = form_value[0]
            text = form_value[1]

            # 検索条件（★）⇒Q()メソッドの役割調査
            condition_title = Q()
            condition_text = Q()

            if len(title) != 0 and title[0]:
                condition_title = Q(title__icontains=title)
            if len(text) != 0 and text[0]:
                condition_text = Q(text__contains=text)

            return Post.objects.select_related().filter(condition_title & condition_text)
        else:
            # 何も返さない
            return Post.objects.none()


class CreateView(generic.CreateView):
    # 登録画面
    model = Post
    form_class = PostForm

    def get_success_url(self):  # 詳細画面にリダイレクトする。
        return reverse('search:detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs['initial'] = {'author': self.request.user}  # フォームに初期値を設定する。
        return form_kwargs


class DetailView(generic.DetailView):
    # 詳細画面
    model = Post
    template_name = 'search/detail.html'


class PostViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        post = self.get_object()
        return Response(post.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'posts': reverse('post-list', request=request, format=format),
    })