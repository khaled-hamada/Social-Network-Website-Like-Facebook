from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

app_name= "account"

urlpatterns = [
    # path('login/',views.user_login , name = 'login' ),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #change password
    path('password_change', auth_views.PasswordChangeView.as_view(), name='password-change'),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(), name='password-change-done'),
    # reset password urls
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('account:password_reset_done')),
         name='password-reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password-reset-complete'),

    path('', views.dashboard, name='dashboard'),
]
