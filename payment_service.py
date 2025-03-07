import os
import stripe
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StripePaymentService:
    def __init__(self):
        self.api_key = os.getenv("STRIPE_API_KEY")
        stripe.api_key = self.api_key
    
    def create_payment_intent(self, amount, currency="usd", description=None):
        """
        Create a PaymentIntent to track the payment lifecycle
        Amount should be in cents (e.g., $20.00 = 2000)
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                automatic_payment_methods={"enabled": True},
                description=description
            )
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "id": intent.id,
                "amount": amount,
                "currency": currency
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def retrieve_payment_intent(self, intent_id):
        """Retrieve a specific PaymentIntent by ID"""
        try:
            intent = stripe.PaymentIntent.retrieve(intent_id)
            return {
                "success": True,
                "status": intent.status,
                "amount": intent.amount,
                "currency": intent.currency
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_customer(self, name, email):
        """Create a Stripe customer that can be reused for future payments"""
        try:
            customer = stripe.Customer.create(
                name=name,
                email=email
            )
            return {
                "success": True,
                "customer_id": customer.id,
                "name": customer.name,
                "email": customer.email
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_subscription(self, customer_id, price_id):
        """Create a subscription for a customer"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                expand=["latest_invoice.payment_intent"]
            )
            return {
                "success": True,
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }