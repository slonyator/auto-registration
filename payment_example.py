"""
payment_generics_example.py

Goal:
    - Multiple payment providers (Stripe, PayPal, Adyen)
    - One clean interface: PaymentProvider[R]
    - Auto-registration using __init_subclass__
    - Business logic depends only on PaymentProvider
    - Providers return their own typed response objects (R)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Type, TypeVar

# -------------------------------------------------------------------
# 1. Domain result types (provider-specific)
# -------------------------------------------------------------------


@dataclass
class StripeChargeResponse:
    payment_id: str
    receipt_url: str


@dataclass
class PayPalChargeResponse:
    transaction_id: str
    redirect_link: str


@dataclass
class AdyenChargeResponse:
    psp_reference: str
    result_code: str


# This generic type represents the PROVIDER'S RESULT TYPE
R = TypeVar("R")


# -------------------------------------------------------------------
# 2. Generic PaymentProvider interface + auto-registration
# -------------------------------------------------------------------


class PaymentProvider(Generic[R], ABC):
    """
    Generic interface for a payment provider.
    R = return type of the charge() implementation.
    """

    _registry: Dict[str, Type["PaymentProvider[Any]"]] = {}

    def __init_subclass__(cls, *, name: str | None = None, **kwargs):
        """
        Every subclass can register itself by specifying:
            class StripeProvider(PaymentProvider, name="stripe"):
        """
        super().__init_subclass__(**kwargs)
        if name:
            if name in cls._registry:
                raise ValueError(f"Provider {name!r} already registered")
            cls._registry[name] = cls

    # Factory method
    @classmethod
    def from_name(cls, name: str, **kwargs) -> PaymentProvider[Any]:
        try:
            provider_cls = cls._registry[name]
        except KeyError:
            raise ValueError(f"Unknown provider {name!r}. Known: {list(cls._registry)}")
        return provider_cls(**kwargs)

    # Generic interface
    @abstractmethod
    def charge(self, amount: float, currency: str, source: str) -> R:
        pass

    @abstractmethod
    def refund(self, charge_result: R, amount: float | None = None) -> bool:
        pass


# -------------------------------------------------------------------
# 3. Concrete Providers (each returns its OWN type R)
# -------------------------------------------------------------------


@dataclass
class StripeProvider(PaymentProvider[StripeChargeResponse], name="stripe"):
    api_key: str

    def charge(self, amount: float, currency: str, source: str) -> StripeChargeResponse:
        print(f"[Stripe] Charge {amount} {currency} from card {source}")
        return StripeChargeResponse(
            payment_id="stripe_123", receipt_url="https://stripe.com/receipt/123"
        )

    def refund(
        self, charge_result: StripeChargeResponse, amount: float | None = None
    ) -> bool:
        print(f"[Stripe] Refund {charge_result.payment_id} for {amount}")
        return True


@dataclass
class PayPalProvider(PaymentProvider[PayPalChargeResponse], name="paypal"):
    client_id: str
    secret: str

    def charge(self, amount: float, currency: str, source: str) -> PayPalChargeResponse:
        print(f"[PayPal] Charge {amount} {currency}")
        return PayPalChargeResponse(
            transaction_id="paypal_456", redirect_link="https://paypal.com/tx/456"
        )

    def refund(
        self, charge_result: PayPalChargeResponse, amount: float | None = None
    ) -> bool:
        print(f"[PayPal] Refund {charge_result.transaction_id}")
        return True


@dataclass
class AdyenProvider(PaymentProvider[AdyenChargeResponse], name="adyen"):
    merchant_account: str

    def charge(self, amount: float, currency: str, source: str) -> AdyenChargeResponse:
        print(f"[Adyen] Charge {amount} {currency}")
        return AdyenChargeResponse(psp_reference="adyen_789", result_code="Authorised")

    def refund(
        self, charge_result: AdyenChargeResponse, amount: float | None = None
    ) -> bool:
        print(f"[Adyen] Refund {charge_result.psp_reference}")
        return True


# -------------------------------------------------------------------
# 4. Business Logic Layer — completely independent of providers
# -------------------------------------------------------------------


class CheckoutService(Generic[R]):
    """
    Business logic sees only a PaymentProvider[R].
    It does NOT know or care which provider is actually used.
    """

    def __init__(self, provider: PaymentProvider[R]):
        self.provider = provider

    def checkout(self, card: str, amount: float) -> R:
        print("Processing checkout...")
        return self.provider.charge(amount, currency="USD", source=card)


# -------------------------------------------------------------------
# 5. Usage
# -------------------------------------------------------------------


def main():
    config_provider = "stripe"  # Could come from env or feature flag

    provider = PaymentProvider.from_name(
        config_provider,
        api_key="sk_test_123",  # only Stripe needs this
    )

    # type: provider is PaymentProvider[Any]
    checkout = CheckoutService(provider)

    result = checkout.checkout("4242 4242 4242 4242", 49.99)

    print("Checkout result:", result)


if __name__ == "__main__":
    main()
