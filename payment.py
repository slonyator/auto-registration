"""
payment.py

Demonstrates auto-registration of providers using __init_subclass__.
- Multiple payment providers (Stripe, PayPal, Square) behind ONE interface
- Providers auto-register themselves with their default configuration
- No central "if/elif" factory needed
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar


@dataclass
class ChargeResult:
    provider: str
    transaction_id: str
    amount: float
    currency: str


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers with built-in auto-registration.

    Subclasses register themselves via __init_subclass__:
        class StripeProvider(PaymentProvider, name="stripe", default_config={...}):
            ...
    """

    _registry: ClassVar[dict[str, tuple[type[PaymentProvider], dict[str, Any]]]] = {}

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        default_config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            cls._registry[name] = (cls, default_config or {})

    @classmethod
    def from_name(cls, name: str, **kwargs: Any) -> PaymentProvider:
        """Create a provider by name, merging default config with kwargs."""
        provider_cls, default_config = cls._registry[name]
        return provider_cls(**{**default_config, **kwargs})

    @classmethod
    def list_available(cls) -> list[str]:
        return list(cls._registry.keys())

    @abstractmethod
    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        raise NotImplementedError


@dataclass
class StripeProvider(
    PaymentProvider,
    name="stripe",
    default_config={"api_key": "sk_test_123"},
):
    api_key: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[Stripe] Charging {amount} {currency} using source={source}")
        return ChargeResult("stripe", "stripe_tx_123", amount, currency)


@dataclass
class PayPalProvider(
    PaymentProvider,
    name="paypal",
    default_config={"client_id": "my-app", "secret": "super-secret"},
):
    client_id: str
    secret: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[PayPal] Charging {amount} {currency} using source={source}")
        return ChargeResult("paypal", "paypal_tx_456", amount, currency)


@dataclass
class SquareProvider(
    PaymentProvider,
    name="square",
    default_config={"access_token": "sq_test_token", "location_id": "LOC_123"},
):
    access_token: str
    location_id: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[Square] Charging {amount} {currency} using source={source}")
        return ChargeResult("square", "square_tx_789", amount, currency)
