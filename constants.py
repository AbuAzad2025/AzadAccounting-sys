from decimal import Decimal

DEFAULT_CURRENCY = "ILS"

CURRENCY_CHOICES = [
    ("ILS", "شيكل إسرائيلي"), 
    ("USD", "دولار أمريكي"), 
    ("EUR", "يورو"), 
    ("JOD", "دينار أردني"), 
    ("AED", "درهم إماراتي"), 
    ("SAR", "ريال سعودي"),
    ("EGP", "جنيه مصري"),
    ("GBP", "جنيه إسترليني")
]

# Common decimal constants
CENT = Decimal("0.01")
TWOPLACES = Decimal("0.01")
ZERO_PLACES = Decimal("1")
