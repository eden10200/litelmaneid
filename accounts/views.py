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
from django.shortcuts import get_object_or_404
from django.contrib import messages
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
        context['date']=start_date
        context['date_e']=end_date
        context['transactions'] = transactions

        context['total_expense'] = total_expense

        return context

def delete_transaction(request, pk):
    # ユーザーの取引を取得
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    # 取引を削除
    transaction.delete()

    # 削除後、メッセージを表示してリダイレクト
    messages.success(request, '取引が削除されました。')
    return redirect('accounts:money_manage', pk=request.user.pk)



'''サインアップ'''
def edit_transaction(request, pk):
    # 取引を取得
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()  # 変更を保存
            messages.success(request, '取引が更新されました。')
            return redirect('accounts:money_manage', pk=request.user.pk)
        else:
            messages.error(request, 'フォームにエラーがあります。')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'accounts/edit_transaction.html', {'form': form, 'transaction': transaction})

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
        print(f"Action received: {action}")  # デバッグ用

        if action == "analyze":
            # レシート解析処理
            uploaded_file = request.FILES.get('receipt_image')
            if not uploaded_file:
                form = self.form_class(request.POST)
                return render(request, self.template_name, {'form': form, 'error': 'レシート画像をアップロードしてください。'})

            # 一時ファイルの作成とOCR処理
            temp_dir = 'temp'
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, uploaded_file.name)

            try:
                with open(temp_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)

                # OCR処理
                

                load_dotenv()
                GOOGLE_CLOUD_KEY_JSON_PATH = os.getenv("GOOGLE_CLOUD_KEY_JSON_PATH")
                ocr_client = ReceiptOcrClient(
                    credentials_path=GOOGLE_CLOUD_KEY_JSON_PATH
                )
                payment_info = ocr_client.get_payment_info(file_name=temp_path)
                print(f"OCR Results: {payment_info}")  # デバッグ用

                # フォームを初期化（OCR結果を設定）
                form = self.form_class(
                    initial={
                        'date': payment_info.get('date', ''),
                        'amount': payment_info.get('amount', ''),
                    },
                    ocr_mode=True
                )
            finally:
                # 一時ファイルの削除
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        elif action == "save":
            # 保存処理
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_success_url())
        else:
            form = self.form_class(request.POST)

        # エラー時のデバッグ
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
