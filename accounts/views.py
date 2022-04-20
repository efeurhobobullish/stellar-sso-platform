import json
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


class Dashboard(View, Stellar):
    form_class = StellarAccountForm
    model = StellarResource
    template_name = 'dashboard/dashboard.html'

    @method_decorator(login_required)
    def get(self, request):
        form = self.form_class()
        
        
        # 1. retrieve user stellar accountID
        try:
            user = StellarResource.objects.get(user=request.user)
            pub_key = user.acc_ID
        except self.model.DoesNotExist:
            return redirect('home')

        if pub_key:
            # 2. retreive and display wallet balance
            server = self.serverConnection(server_url)
            wallet = server.accounts().account_id(pub_key).call()
            print('\n\n', wallet,'\n\n')

            if len(wallet['balances']) == 1:
                wallet_balance = 0.00
            else:
                for balance in wallet['balances']:
                    print(f"Type: {balance['asset_type']}, Balance: {balance['balance']}\n\n\n")
                    if balance['asset_code'] == 'NGNT':
                        wallet_balance = balance['balance']
                        break
            
            print(wallet_balance, "CONTEXT OF DASH")
            
            # 3. render balance via context
            context = {
                'form': form,
                'wallet_balance': round(float(wallet_balance), 3),
                'paystack_public_key': PAYSTACK_PUBLIC_KEY,
                'charges': APP_CHARGES,
            }

        return render(request, self.template_name, context)

    @method_decorator(login_required)
    def post(self, request):
        form = self.form_class(request.POST)
        wallet_balance = 0.00

        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        deposit_price = body_data['amount_NGN']

        server = self.serverConnection(server_url)
        network_passphrase = self.set_network_passphrase()
        base_fee = server.fetch_base_fee()

        # Keys for accounts to issue and receive the new asset
        # -- sender / issuer
        issuing_keypair = self.get_or_create_keypair(request, source_secret_key)
        issuing_public = issuing_keypair.public_key
        issuing_account = server.load_account(account_id=issuing_public)

        # -- reciever
        user = StellarResource.objects.get(user=request.user)
        sec_key = user.secretkey

        distributor_keypair = self.get_or_create_keypair(request, sec_key)
        distributor_public = distributor_keypair.public_key
        distributor_account = server.load_account(distributor_public)

        # Create an object to represent the new asset
        # NGNT = Asset("NGNT", issuing_public)
        NGNT = self.ngnt_asset()

        trust_transaction = self.init_trx(distributor_account, network_passphrase, base_fee) \
            .append_change_trust_op(asset=NGNT) \
            .set_timeout(100) \
            .build()

        trust_transaction.sign(distributor_keypair)
        trust_transaction_resp = server.submit_transaction(trust_transaction)

        print(f"Change Trust Transaction Resp:\n{trust_transaction_resp}")

        payment_transaction = self.init_trx(issuing_account, network_passphrase, base_fee) \
            .append_payment_op(destination=distributor_public, amount=deposit_price, asset=NGNT) \
            .set_timeout(30) \
            .build()

        payment_transaction.sign(issuing_keypair)
        payment_transaction_resp = server.submit_transaction(payment_transaction)

        print(f"Payment Transaction Resp:\n{payment_transaction_resp}")

        wallet = server.accounts().account_id(distributor_public).call()

        for balance in wallet['balances']:
            print(f"Type: {balance['asset_type']}, Balance: {balance['balance']}\n\n\n")

            if balance['asset_code'] == 'NGNT':
                wallet_balance = balance['balance']
                break

        context = {
            'form': form,
            'wallet_balance': round(float(wallet_balance), 3),
            'paystack_public_key': PAYSTACK_PUBLIC_KEY,
            'charges': APP_CHARGES,
        }
        return render(request, self.template_name, context)