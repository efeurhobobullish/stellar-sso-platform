from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from SSO.settings import server_url, source_secret_key, PAYSTACK_PUBLIC_KEY, APP_CHARGES

# cbv method
from django.views import View

# SSO
from .models import *
from .forms import *
from .stellar import Stellar


# Create your views here.

class Home(View, Stellar):
    template_name = 'dashboard/index.html'

    def get_User_Stellar_Resource(self, request):
        return StellarResource.objects.get_or_create(user=request.user)

    @method_decorator(login_required)
    def get(self, request):
        stellarResource, _ = self.get_User_Stellar_Resource(request)
        has_wallet = True if stellarResource.has_account else False

        if has_wallet:
            return redirect('dashboard')
        return render(request, self.template_name, {})
    
