from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        return request.build_absolute_uri(
            reverse('accounts:account_confirm_email', args=[emailconfirmation.key])
            )