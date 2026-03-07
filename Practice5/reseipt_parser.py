import re

with open("raw.txt", "r", encoding="utf-8") as file:
    text = file.read()

product_pattern = r"\d+\.\s*\n(.+)"
products = re.findall(product_pattern, text)

price_pattern = r"\d[\d ]*,\d{2}"
prices = re.findall(price_pattern, text)

total_match = re.search(r"ИТОГО:\s*\n([\d ]*,\d{2})", text)
total = total_match.group(1) if total_match else None

datetime_match = re.search(r"(\d{2}\.\d{2}\.\d{4})\s(\d{2}:\d{2}:\d{2})", text)

date = datetime_match.group(1) if datetime_match else None
time = datetime_match.group(2) if datetime_match else None

payment_match = re.search(r"(Банковская карта|Наличные)", text)
payment_method = payment_match.group(1) if payment_match else None

print("\nProducts:")
for i, product in enumerate(products, 1):
    print(f"{i}. {product}")
print()
print("\nPrices:")
for price in prices:
    print(price)
print()
print("Date:", date)
print("Time:", time)
print("Payment Method:", payment_method)
print("Total:", total)