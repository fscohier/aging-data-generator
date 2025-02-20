import random
import csv
from datetime import datetime, timedelta

# Common variable
num_companies = 100

# Variables for customer table
regions = ["Benelux", "DACH", "France", "Italy", "Nordics", "Spain"]
region_distribution = {"Benelux": 0.15, "DACH": 0.25,
                       "France": 0.20, "Italy": 0.10, "Nordics": 0.15, "Spain": 0.15}
payment_terms = [30, 60]
customers = []
customer_id = 10000

# Variables for invoice table
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
invoices = []
credit_notes = []
document_id = 1000000
min_invoices = 30
max_invoices = 100

# Functions
# Random date


def generate_random_date(start, end):
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)

# Random company names


def generate_companies(file_path, num_names):
    dinosaur_names = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)  # read the file
        next(reader)  # skip the header
        dinosaur_names = [row[0] for row in reader]

    suffixes = ["LLC", "Inc.", "Co.", "Ltd", "Tech", "Enterprises",
                "Group", "Corp.", "Corporation", "Holdings", "Partners", "Solutions"]
    adjectives = ["Innovative", "Bold", "Modern", "Visionary", "Creative", "Strategic", "Pioneering",
                  "Global", "Dynamic", "Leading", "Authentic", "Premium", "Revolutionary", "Ethical"]

    company_set = set()
    while len(company_set) < num_names:
        dino_name = random.choice(dinosaur_names)
        adjective = random.choice(adjectives)
        suffix = random.choice(suffixes)
        company_name = f"{adjective} {dino_name} {suffix}"
        company_set.add(company_name)

    company_list = list(company_set)
    return company_list

# Probability of late payments depending on region


def calculate_late_payment_probability(region):
    if region in ["Benelux", "DACH", "Nordics"]:
        return 0.05  # 5% probability of late payment
    elif region == "France":
        return 0.10
    else:
        return 0.25  # 25% for Spain and Italy


# Generating customer table
# This is to make sure that the names are picked up one by one in the company list
company_index = 0
companies = generate_companies(
    "./company_list.csv", num_companies)
for region, region_ratio in region_distribution.items():
    num_region_customers = round(region_ratio * num_companies)
    for _ in range(num_region_customers):
        customers.append({
            "Customer ID": customer_id,
            "Customer Name": companies[company_index],
            "Region": region,
            "Payment Terms": random.choice(payment_terms)
        })
        customer_id += 1
        company_index += 1

# Generating invoice table
for customer in customers:
    # we pick a random number of invoices for each customer
    num_invoices = random.randint(min_invoices, max_invoices)
    late_payment_probability = calculate_late_payment_probability(
        customer["Region"])

    for _ in range(num_invoices):
        document_date = generate_random_date(start_date, end_date)
        due_date = document_date + timedelta(days=customer["Payment Terms"])

        dispute = "Yes" if random.random() < 0.15 else "No"
        dispute_date = generate_random_date(document_date + timedelta(
            days=5), due_date) if dispute == "Yes" else ""
        dispute_reason = random.choice(
            ["Billing", "Delivery", "Pricing", "Product Defect"]) if dispute == "Yes" else ""
        dispute_resolution_date = dispute_date + \
            timedelta(days=random.randint(5, 100)) if dispute == "Yes" else ""
        dispute_resolution_time = (
            dispute_resolution_date - dispute_date).days if dispute == "Yes" else ""

        if dispute == "Yes":
            payment_date = dispute_resolution_date + \
                timedelta(days=random.randint(1, 5))
        else:
            is_late = random.random() < late_payment_probability
            if is_late:
                payment_date = due_date + timedelta(days=random.randint(1, 60))
            else:
                payment_date = due_date - timedelta(days=random.randint(0, 15))

        arrear_days = (payment_date - due_date).days

        invoices.append({
            "Customer ID": customer["Customer ID"],
            "Document Type": "Invoice",
            "Document ID": document_id,
            "Reference": document_id,
            "Document Date": document_date.strftime("%d-%m-%Y"),
            "Due Date": due_date.strftime("%d-%m-%Y"),
            "Payment Date": payment_date.strftime("%d-%m-%Y"),
            "Arrear Days": arrear_days,
            "Amount": round(random.uniform(100, 10000), 2),
            "Currency": "EUR",
            "Dispute": dispute,
            "Dispute Date": dispute_date.strftime("%d-%m-%Y") if dispute == "Yes" else "",
            "Dispute Reason": dispute_reason,
            "Dispute Resolution Date": dispute_resolution_date.strftime("%d-%m-%Y") if dispute == "Yes" else "",
            "Dispute Resolution Time": dispute_resolution_time
        })

        document_id += 1

# Adding credit notes to a certain amount of disputed invoices
for invoice in invoices:
    if invoice["Dispute"] == "Yes" and random.random() > 0.6:
        credit_note_date = invoice["Dispute Resolution Date"]

        credit_notes.append({
            "Customer ID": invoice["Customer ID"],
            "Document Type": "Credit Note",
            "Document ID": document_id,
            "Reference": invoice["Document ID"],
            "Document Date": credit_note_date,
            "Due Date": credit_note_date,
            "Payment Date": credit_note_date,
            "Arrear Days": 0,
            "Amount": -invoice["Amount"],
            "Currency": "EUR",
            "Dispute": "No",
            "Dispute Date": "",
            "Dispute Reason": "",
            "Dispute Resolution Date": "",
            "Dispute Resolution Time": ""
        })

        document_id += 1

invoices.extend(credit_notes)

# Sorting the table by Customer ID and then document date
invoices.sort(key=lambda x: (
    int(x["Customer ID"]), datetime.strptime(x["Document Date"], "%d-%m-%Y")))

# Saving the output to CSV files
with open("customer_data.csv", "w", newline="") as customer_file:
    writer = csv.DictWriter(customer_file, fieldnames=customers[0].keys())
    writer.writeheader()
    writer.writerows(customers)

with open("aging_report_2023-2024.csv", "w", newline="") as aging_file:
    writer = csv.DictWriter(aging_file, fieldnames=invoices[0].keys())
    writer.writeheader()
    writer.writerows(invoices)

print("Customer data and Aging Report generated.")
print(f"Number of customers: {len(customers)}.")
print(f"Number of invoices: {len(invoices)}.")
