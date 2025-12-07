from payment import PaymentProvider


def main() -> None:
    print("Available providers:", PaymentProvider.list_available())
    print()

    # ApplePay provider
    applepay = PaymentProvider.from_name("applepay", merchant_id="merchant.com.example")
    result = applepay.charge(amount=49.99, currency="USD", source="apple_pay_token")
    print("ApplePay result:", result)
    print()

    # PayPal provider
    paypal = PaymentProvider.from_name(
        "paypal", client_id="my-app", secret="super-secret"
    )
    result = paypal.charge(amount=29.99, currency="EUR", source="user@example.com")
    print("PayPal result:", result)
    print()

    # GooglePay provider (with overridden defaults)
    googlepay = PaymentProvider.from_name("googlepay", gateway="stripe")
    result = googlepay.charge(amount=19.99, currency="USD", source="google_pay_token")
    print("GooglePay result:", result)


if __name__ == "__main__":
    main()
