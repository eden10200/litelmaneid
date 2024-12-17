from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),  # 追加
    path('logout/', views.Logout.as_view(), name='logout'),  # 追加
    path('my_page/<int:pk>/', views.MyPage.as_view(), name='my_page'),  # 追加
    path('signup/', views.Signup.as_view(), name='signup'),  # サインアップ
    path('signup_done/', views.SignupDone.as_view(), name='signup_done'),  # サインアップ完了
    path('user_update/<int:pk>', views.UserUpdate.as_view(), name='user_update'),  # 登録情報の更新
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),  # パスワード変更
    path('password_change_done/', views.PasswordChangeDone.as_view(), name='password_change_done'),  # パスワード変更完了
    path('money_manage/<int:pk>/', views.MoneyManage.as_view(), name='money_manage'),  #
    path('add_transaction/<int:pk>/', views.AddTransaction.as_view(), name='add_transaction'),

]
