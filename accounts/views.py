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
    

    @method_decorator(login_required)
    def post(self, request):
        stellarResource, _ = self.get_User_Stellar_Resource(request)

        server = self.serverConnection(server_url)
        network_passphrase = self.set_network_passphrase()
        base_fee = server.fetch_base_fee()

        source = self.get_or_create_keypair(request, source_secret_key)
        source_account = server.load_account(account_id=source.public_key)

        destination = self.get_or_create_keypair(request)

        # print(source, destination)
        # if destination:
        #     pass # destination empty?
        print(f"\n\-----New Keypair: \n\taccount id: {destination.public_key}\
            \n\tsecret seed: {destination.secret}\n\r------\n\r")
        
        print(network_passphrase, base_fee, sep="\n\r")

        # build the transaction
        transaction = self.init_trx(source_account, network_passphrase, base_fee) \
            .append_create_account_op(destination=destination.public_key, starting_balance=f"10.0") \
            .set_timeout(30) \
            .build()

        # sign $ submit the transaction
        transaction.sign(source)
        response = server.submit_transaction(transaction)

        if response["successful"]:
            stellarResource.acc_ID = destination.public_key
            stellarResource.secretkey = destination.secret
            stellarResource.has_account = True
            stellarResource.save()

        print("\n\r-----------Transaction hash: {}\n\r-----------\n\r".format(response["hash"]))

        # return redirect('dashboard')
        return render(request, self.template_name, {
            "account_created": True
        })
