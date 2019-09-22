from textwrap import dedent

from django import forms
from django.shortcuts import render
from ocflib.account.search import user_exists
from ocflib.misc.mail import send_mail_user

from ocfweb.component.forms import Form
# from ocfweb.component.celery import change_password as change_password_task

# TODO: Delete this series of comments
# and then start routing requests:

# - email_reset = prints out a form to enter in
# - an OCF username

reset_message = dedent('''
Hello {username},

We recently received a request to reset the account password for your Open Computing
Facility account. If this was you, please follow the link below to
continue resetting your password:

Username: {username}
Reset Link: {reset_link}

If this wasn't you, please feel free to safely ignore this email.

''')


def email_reset(request):
    error = None
    # Validate that the email is legitimate

    if request.method == 'POST':
        # Submitted a username to reset.
        form = EmailAccountForm(request.POST)

        if form.is_valid():
            account = form.cleaned_data['ocf_account']

            try:
                # TODO: Use account real name instead?
                reset_link = 'https://ocf.berkeley.edu/account/reset/continue?token={}'.format('asdfasdf')
                send_mail_user(
                    account, '[OCF] Link to reset your password',
                    reset_message.format(username=account, reset_link=reset_link),
                )
            except ValueError as ex:
                error = str(ex)
            else:
                return render(
                    request,
                    'account/resetpass/sent.html',
                    {
                        'account': account,
                        'title': 'Password Reset Email Sent',
                    },
                )
    else:
        form = EmailAccountForm()

    return render(
        request,
        'account/resetpass/index.html',
        {
            'error': error,
            'form': form,
            'title': 'Reset Password',
        },
    )


def reset_password(request):
    pass


class EmailAccountForm(Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ocf_account'] = forms.CharField(
            widget=forms.TextInput,
            label='OCF username',
        )

    def clean_ocf_account(self):
        data = self.cleaned_data['ocf_account']
        if not user_exists(data):
            raise forms.ValidationError('OCF user account does not exist.')

        return data
