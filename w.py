import csv

def validate_vat(vat_id, country):
    
    if not vat_id:
        return False
    
    if country == "PL":
        return len(vat_id) == 12 and vat_id.startswith("PL")
    
    return len(vat_id) > 3

def validate_email(email):
    return "@" in email and "." in email

def process_data(vendors):
    valid_records = []
    error_records = []
    
    for v in vendors:
        is_vat_ok = validate_vat(v.get('vat_id', ''), v.get('country', ''))
        is_email_ok = validate_email(v.get('email', ''))
        
        v["group"] = "DOMESTIC" if v.get("country") == "PL" else "INTERNATIONAL"
        
        if is_vat_ok and is_email_ok:
            valid_records.append(v)
        else:
            v['error_reason'] = f"VAT valid: {is_vat_ok}, Email valid: {is_email_ok}"
            error_records.append(v)
            
    return valid_records, error_records

def save_results(data, filename):
    
    if not data:
        print(f"No data to save for {filename}")
        return
    
    with open(filename, mode="w", newline="", encoding="UTF-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        print(f"Successfully saved {len(data)} records to: {filename}")
        
def main():
    
    raw_data = [
        
        {"id": 1001, "name": "Tech Corp", "vat_id": "PL1234567890", "email": "contact@tech.pl", "country": "PL"},
        {"id": 1002, "name": "Global Soft", "vat_id": "123", "email": "bad_mail.com", "country": "US"},
        {"id": 1003, "name": "Local Biz", "vat_id": "PL0987654321", "email": "", "country": "PL"},
        {"id": 1004, "name": "Berlin Bau", "vat_id": "DE987654321", "email": "info@berlin.de", "country": "DE"}

    ]
    
    print("Starting data audit...")
    correct, faulty = process_data(raw_data)
    
    print(f"Total processed: {len(correct) + len(faulty)}")
    print(f"Valid: {len(correct)} | Faulty: {len(faulty)}")

    if faulty:
        save_results(faulty, "audit_errors.csv")
    if correct:
        save_results(correct, "audit_correct.csv")

if __name__ == "__main__":
    main()