from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model # ユーザーモデルを取得するため
from django import forms
from django import forms
from .models import Transaction
# ユーザーモデル取得
User = get_user_model()


'''ログイン用フォーム'''
class LoginForm(AuthenticationForm):

    # bootstrap4対応
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label  # placeholderにフィールドのラベルを入れる


from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

'''サインアップ用フォーム'''


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email', 'username',)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = ''  # 全フィールドを入力必須

            # オートフォーカスとプレースホルダーの設定
            print(field.label)
            if field.label == '姓':
                field.widget.attrs['autofocus'] = ''  # 入力可能状態にする
                field.widget.attrs['placeholder'] = '田中'
            elif field.label == '名':
                field.widget.attrs['placeholder'] = '一郎'
            elif field.label == 'メールアドレス':
                field.widget.attrs['placeholder'] = '***@gmail.com'


'''ユーザー情報更新用フォーム'''


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email', 'username',)

    # bootstrap4対応
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            self.control = 'form-control'
            field.widget.attrs['class'] = self.control
            field.widget.attrs['required'] = ''  # 全フィールドを入力必須


from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm

'''パスワード変更フォーム'''


class MyPasswordChangeForm(PasswordChangeForm):

    # bootstrap4対応で、classを指定
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'date', 'store_name', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1, 'placeholder': '金額（必須）'}),
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '店名（任意）'}),
            'user': forms.HiddenInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        ocr_mode = kwargs.pop('ocr_mode', False)
        super().__init__(*args, **kwargs)

        self.fields['date'].required = False
        self.fields['store_name'].required = False
        self.fields['amount'].required = False
class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)
