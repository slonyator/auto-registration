"""
payment_example.py

Goal:
- Multiple payment providers (Stripe, PayPal) behind ONE interface.
- Providers auto-register themselves with their default configuration.
- No separate PROVIDER_CONFIG dictionary needed.
- A generic, type-safe registry.
- Business logic depends only on the PaymentProvider interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Tuple, Type, TypeVar


# -------------------------------------------------------------------
# 1. Domain models
# -------------------------------------------------------------------


@dataclass
class ChargeResult:
    provider: str
    transaction_id: str
    amount: float
    currency: str


# -------------------------------------------------------------------
# 2. Generic provider registry with default config support
# -------------------------------------------------------------------

P = TypeVar("P", bound="PaymentProvider")


class ProviderRegistry(Generic[P]):
    """
    A generic registry mapping string keys to provider classes AND their
    default configurations.

    Generic parameter P ensures:
      - Registry only contains subclasses of PaymentProvider
      - create() returns the correct type
    """

    def __init__(self) -> None:
        self._providers: Dict[str, Tuple[Type[P], Dict[str, Any]]] = {}

    def register(
        self,
        name: str,
        provider_cls: Type[P],
        default_config: Dict[str, Any] | None = None,
    ) -> None:
        """
        Register a provider class with optional default configuration.
        """
        if name in self._providers:
            raise ValueError(f"Provider {name!r} already registered")
        self._providers[name] = (provider_cls, default_config or {})

    def create(self, name: str, **kwargs: Any) -> P:
        """
        Create a provider instance by name.

        Default configuration is merged with kwargs, where kwargs take precedence.
        """
        if name not in self._providers:
            raise ValueError(
                f"Unknown provider {name!r}. "
                f"Known providers: {list(self._providers.keys())}"
            )

        provider_cls, default_config = self._providers[name]
        merged_config = {**default_config, **kwargs}

        return provider_cls(**merged_config)

    def get_default_config(self, name: str) -> Dict[str, Any]:
        """Retrieve the default configuration for a provider."""
        if name not in self._providers:
            raise ValueError(f"Unknown provider {name!r}")
        return self._providers[name][1].copy()

    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())


# Global registry for all payment providers
provider_registry: ProviderRegistry["PaymentProvider"] = ProviderRegistry()


# -------------------------------------------------------------------
# 3. Base interface + auto-registration via __init_subclass__
# -------------------------------------------------------------------


class PaymentProvider(ABC):
    """
    Abstract base class for all payment providers.

    Subclasses register themselves via __init_subclass__ with:
      - name: The provider identifier (e.g., "stripe", "paypal")
      - default_config: Default kwargs for instantiation
    """

    def __init_subclass__(
        cls,
        *,
        name: str | None = None,
        default_config: Dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if name is not None:
            provider_registry.register(name, cls, default_config)

    @classmethod
    def from_name(cls, name: str, **kwargs: Any) -> PaymentProvider:
        """
        Create a provider by name ("stripe", "paypal", ...).

        Uses registered default configuration, with kwargs as overrides.
        """
        return provider_registry.create(name, **kwargs)

    @classmethod
    def list_available(cls) -> list[str]:
        """List all available provider names."""
        return provider_registry.list_providers()

    @abstractmethod
    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        raise NotImplementedError


# -------------------------------------------------------------------
# 4. Concrete payment providers (Stripe, PayPal)
#    Default config is embedded in the class definition
# -------------------------------------------------------------------


@dataclass
class StripeProvider(
    PaymentProvider,
    name="stripe",
    default_config={"api_key": "sk_test_123"},
):
    api_key: str

    def charge(self, amount: float, currency: str, source: str) -> ChargeResult:
        print(f"[Stripe] Charging {amount} {currency} using source={source}")
        return ChargeResult(
            provider="stripe",
            transaction_id="stripe_tx_123",
            amount=amount,
            currency=currency,
        )


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
        return ChargeResult(
            provider="paypal",
            transaction_id="paypal_tx_456",
            amount=amount,
            currency=currency,
        )


# -------------------------------------------------------------------
# 5. Business/service layer (depends ONLY on PaymentProvider)
# -------------------------------------------------------------------


class CheckoutService:
    """
    Service layer that depends exclusively on the PaymentProvider interface.
    """

    def __init__(self, provider: PaymentProvider) -> None:
        self._provider = provider

    def process_payment(
        self, amount: float, currency: str, source: str
    ) -> ChargeResult:
        return self._provider.charge(amount, currency, source)


# -------------------------------------------------------------------
# 6. Wiring / usage - NO MORE PROVIDER_CONFIG dictionary needed!
# -------------------------------------------------------------------


def main() -> None:
    print("Available providers:", PaymentProvider.list_available())
    print()

    # Example 1: Use default configuration (no kwargs needed)
    provider_name = "stripe"
    provider = PaymentProvider.from_name(provider_name)

    print(f"Created provider: {provider!r}")
    print(f"Provider type: {type(provider).__name__}")

    checkout = CheckoutService(provider)
    result = checkout.process_payment(49.99, "USD", "card_abc")
    print("Payment result:", result)
    print()

    # Example 2: Override specific defaults
    custom_stripe = PaymentProvider.from_name("stripe", api_key="sk_live_real_key")
    print(f"Custom Stripe provider: {custom_stripe!r}")
    print()

    # Example 3: PayPal with partial override
    custom_paypal = PaymentProvider.from_name("paypal", secret="production-secret")
    print(f"Custom PayPal provider: {custom_paypal!r}")


if __name__ == "__main__":
    main()
