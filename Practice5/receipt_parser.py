import re
import json

#Read receipt text
with open("raw.txt", "r", encoding="utf-8") as f:
    receipt_text = f.read()

#to convert price strings → float
def parse_price(price_str):
    return float(price_str.replace(" ", "").replace(",", "."))

#Extract products with number, name, quantity, unit price, total
pattern = re.compile(
    r'(\d+)\.\n'                       # product number
    r'(.*?)\n'                         # product name
    r'([\d, ]+)\s*x\s*([\d, ]+,\d{2})\n'  # quantity x unit price
    r'([\d, ]+,\d{2})\n'               # total
    r'Стоимость',                       # literal
    re.DOTALL
)

products = []
for match in pattern.finditer(receipt_text):
    number = int(match.group(1))
    name = match.group(2).strip()
    qty = parse_price(match.group(3))
    unit_price = parse_price(match.group(4))
    total = parse_price(match.group(5))
    
    products.append({
        "number": number,
        "name": name,
        "quantity": qty,
        "unit_price": unit_price,
        "total": total
    })

#Extract payment method
payment_method = None
if "Банковская карта" in receipt_text:
    payment_method = "Bank Card"
elif "Наличные" in receipt_text:
    payment_method = "Cash"

#Extract total amount (ИТОГО:)
total_match = re.search(r'ИТОГО:\s*([\d, ]+,\d{2})', receipt_text)
total_amount = parse_price(total_match.group(1)) if total_match else sum(p["total"] for p in products)

#Extract date and time (Время:)
date_time_match = re.search(r'Время:\s*([\d\.]+)\s+([\d:]+)', receipt_text)
date = date_time_match.group(1) if date_time_match else None
time = date_time_match.group(2) if date_time_match else None

#Create structured JSON output
receipt_data = {
    "products": products,
    "total": total_amount,
    "payment_method": payment_method,
    "date": date,
    "time": time
}


print(json.dumps(receipt_data, ensure_ascii=False, indent=4))