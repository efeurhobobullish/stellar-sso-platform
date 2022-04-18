# general
import requests

# SSO app
from SSO.settings import DEBUG, source_public_key
from .models import *
from .forms import *

# stellar sdk
from stellar_sdk import TransactionBuilder, Server, Network, Keypair, Asset


# Create your views here.

class Stellar():
    """
    Stellar helper class
    """

    def get_or_create_keypair(self, req, secret_key=None, test_acc=False):
        """
        Retrieve keypair from db; if empty generate new keypair
        """
        user, _ = StellarResource.objects.get_or_create(user=req.user)

        if secret_key:
            return Keypair.from_secret(secret_key)
        
        if not user.acc_ID and not secret_key:
            keypair = Keypair.random()

            if test_acc:
                # auto create & fund test acc
                requests.get(f"https://friendbot.stellar.org?addr={keypair.public_key}")
            return keypair

    def set_network_passphrase(self):
        """Connect to the server"""
        return Network.TESTNET_NETWORK_PASSPHRASE if DEBUG else Network.PUBLIC_NETWORK_PASSPHRASE

    def serverConnection(self, server__url):
        """Connect to the server"""
        return Server(horizon_url = server__url)
    
    def init_trx(self, source_acc, network_phrase, base_fee):
        return TransactionBuilder(
            source_account=source_acc,
            network_passphrase = network_phrase,
            base_fee=base_fee
        )

    def ngnt_asset(self):
        return Asset("NGNT", source_public_key)
