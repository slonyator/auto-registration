from payment import PaymentProvider


def main() -> None:
    # Pretend this comes from a config file:
    provider_name = "stripe"

    provider = PaymentProvider.from_name(provider_name, api_key="sk_test_123")

    result = provider.charge(amount=29.99, currency="USD", source="4242 4242 4242 4242")

    print("Charge result:", result)


if __name__ == "__main__":
    main()
