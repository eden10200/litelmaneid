from .forms import LoginForm, User,DateRangeForm  # 追加
from django.shortcuts import redirect, resolve_url  # 追加
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy  # 追加　遅延評価用
from .forms import LoginForm, SignupForm, UserUpdateForm, MyPasswordChangeForm  # 追加
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView  # 追加
from django.contrib.auth.models import User
from .models import Transaction
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.views import generic
from django.urls import reverse_lazy
from .forms import TransactionForm
from .receipt_ocr_client import ReceiptOcrClient
import os
from dotenv import load_dotenv
'''トップページ'''


class TopView(generic.TemplateView):
    template_name = 'accounts/top.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'


class Logout(LogoutView):
    template_name = 'accounts/logout.html'


'''自分しかアクセスできないようにするMixin(My Pageのため)'''


class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        # 今ログインしてるユーザーのpkと、そのマイページのpkが同じなら許可
        user = self.request.user
        return user.pk == self.kwargs['pk']


'''マイページ'''


class MyPage(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'accounts/my_page.html'
    # モデル名小文字(user)でモデルインスタンスがテンプレートファイルに渡される


'''money管理'''


class MoneyManage(OnlyYouMixin, generic.DetailView):
    model = User
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ログインユーザーの家計簿データを取得
        user = self.request.user
        form = DateRangeForm(self.request.GET)
        context['form'] = form

        # 開始日と終了日が指定されている場合
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        transactions = Transaction.objects.filter(user=user).order_by('-date')
        if start_date:
            transactions = transactions.filter(date__gte=start_date)  # 開始日以降
        if end_date:
            transactions = transactions.filter(date__lte=end_date)  # 終了日以前

        total_expense = transactions.aggregate(total=Sum('amount'))['total'] or 0

        # コンテキストに追加
        context['transactions'] = transactions

        context['total_expense'] = total_expense

        return context


'''サインアップ'''


class AddTransaction(LoginRequiredMixin, generic.CreateView):
    template_name = 'accounts/add_transaction.html'
    form_class = TransactionForm

    def get_success_url(self):
        return resolve_url('accounts:money_manage', pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Add Transaction"
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        print(f"Action received: {action}")  # Actionをデバッグ

        if action == "analyze":
            # 解析ボタンが押された場合
            uploaded_file = request.FILES.get('receipt_image')
            temp_dir = 'temp'
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)  # tempディレクトリを作成
            if uploaded_file:
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                                        
                load_dotenv()
                API_KEY_PATH = os.getenv("API_KEY_PATH")
                # OCR処理（Google APIなど）
                ocr_client = ReceiptOcrClient(credentials_path=API_KEY_PATH)
                payment_info = ocr_client.get_payment_info(file_name=temp_path)
                os.remove(temp_path)
                print(payment_info.get('date', ''))
                print(payment_info.get('amount',  ''))
                # OCR結果をフォームに反映（ocr_mode=Trueで必須項目を無効化）
                form = TransactionForm(request.POST, initial={
                    'date': payment_info.get('date', ''),
                    'amount': payment_info.get('amount', ''),

                }, ocr_mode=True)
            else:
                form = TransactionForm(request.POST)

        elif action == "save":
            # 保存ボタンが押された場合
            form = TransactionForm(request.POST)
            # 必須項目を送信時に設定
            form.fields['date'].required = True
            form.fields['amount'].required = True

            if form.is_valid():
                form.save()
                return redirect(self.get_success_url())

        # フォームが無効な場合、エラー内容をデバッグ
        print("Form errors:", form.errors)
        return render(request, self.template_name, {'form': form})
class Signup(generic.CreateView):
    template_name = 'accounts/user_form.html'
    form_class = SignupForm

    def form_valid(self, form):
        user = form.save()  # formの情報を保存
        return redirect('accounts:signup_done')

    # データ送信
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Sign up"
        return context


'''サインアップ完了'''


class SignupDone(generic.TemplateView):
    template_name = 'accounts/sign_up_done.html'


'''ユーザー登録情報の更新'''


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'

    def get_success_url(self):
        return resolve_url('accounts:my_page', pk=self.kwargs['pk'])

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Update"
        return context


class PasswordChange(PasswordChangeView):
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('account:password_change_done')
    template_name = 'accounts/user_form.html'

    # contextデータ作成
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["process_name"] = "Change Password"
        return context


'''パスワード変更完了'''


class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'accounts/password_change_done.html'
