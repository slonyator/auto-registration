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
from typing import Any, ClassVar, NamedTuple


@dataclass
class ChargeResult:
    provider: str
    transaction_id: str
    amount: float
    currency: str


class ProviderInput(NamedTuple):
    cls: type[PaymentProvider]
    config: dict[str, Any]


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers with built-in auto-registration.

    Subclasses register themselves via __init_subclass__:
        class ApplePayProvider(PaymentProvider, name="applepay", default_config={...}):
            ...
    """

    _registry: ClassVar[dict[str, ProviderInput]] = {}

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        default_config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        if name is not None:
            cls._registry[name] = ProviderInput(cls, default_config or {})

    @classmethod
    def from_name(cls, name: str, **kwargs: Any) -> PaymentProvider:
        """Create a provider by name, merging default config with kwargs."""
        entry = cls._registry[name]
        return entry.cls(**{**entry.config, **kwargs})

    @classmethod
    def list_available(cls) -> list[str]:
        return list(cls._registry.keys())

    @abstractmethod
    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        raise NotImplementedError


@dataclass
class ApplePayProvider(
    PaymentProvider,
    name="applepay",
    default_config={"merchant_id": "merchant.com.example"},
):
    merchant_id: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[ApplePay] Charging {amount} {currency} using source={source}")
        return ChargeResult("applepay", "applepay_tx_123", amount, currency)


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
class GooglePayProvider(
    PaymentProvider,
    name="googlepay",
    default_config={"gateway": "example", "merchant_id": "exampleMerchantId"},
):
    gateway: str
    merchant_id: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[GooglePay] Charging {amount} {currency} using source={source}")
        return ChargeResult("googlepay", "googlepay_tx_789", amount, currency)
