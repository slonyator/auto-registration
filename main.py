from payment import PaymentProvider


def main() -> None:
    print("Available providers:", PaymentProvider.list_available())
    print()

    # Stripe provider
    stripe = PaymentProvider.from_name("stripe", api_key="sk_test_123")
    result = stripe.charge(amount=49.99, currency="USD", source="4242 4242 4242 4242")
    print("Stripe result:", result)
    print()

    # PayPal provider
    paypal = PaymentProvider.from_name(
        "paypal", client_id="my-app", secret="super-secret"
    )
    result = paypal.charge(amount=29.99, currency="EUR", source="user@example.com")
    print("PayPal result:", result)
    print()

    # Square provider (with overridden defaults)
    square = PaymentProvider.from_name("square", access_token="sq_live_token")
    result = square.charge(amount=19.99, currency="USD", source="card_nonce_xyz")
    print("Square result:", result)


if __name__ == "__main__":
    main()
