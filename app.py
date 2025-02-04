import os
import json
import openai
import fitz
from utils.pdf_parser import parse_pdf

# Configure OpenAI API
openai.api_key = "  "
def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num) 
        text += page.get_text("text") + "\n" 
    return text.strip()
def pdf_to_json(pdf_path, output_path):
    """Extract text from PDF and use OpenAI API to convert it into structured JSON."""
    
    # Extract text from multiple pages
    text = extract_text_from_pdf(pdf_path)

    # Define a clear prompt for JSON generation
    prompt = f"""
    Convert the following multi-page document text into a properly formatted JSON structure. Ensure the JSON is valid, complete, and properly formatted.
The document may span multiple pages, and all data across the pages should be included.
Extract the data from this invoice and convert it into structured JSON format. Ensure:
    - All items in the invoice are captured, including duplicates.
    - The JSON output includes exactly 31 items if present.
    - The table rows are well-structured with key-value pairs.
    Ensure that:
     -Ensure that both upper and lower case digits are captured accurately.
- Extract all rows from tables, including similar and duplicate data.
    -Extracted all the rows from a table and similar data also return into output extracted all data 
    - The JSON is valid and well-formatted.
    - All rows from the invoice table are extracted correctly.
    - Multiple pages and multi-line rows are handled properly.
    -Ensure that:
    - Extract all rows from tables, including similar and duplicate data.
    - Ensure multi-page and multi-line rows are handled properly.
    - Invoice details, customer details, supplier details, and totals are extracted correctly.
    - All 31 rows from the provided invoice table are extracted correctly.
    - Items should include:
         description, hsn_sac_code, cgst_rate, cgst_amount, sgst_rate, sgst_amount,
          MRP_amount, discount, quantity, rate, taxable_amount, net_taxable_amount, B.D /C %, A.D /C %, Aft D /C MRP,Campaign,
Discount ,IGST% ,IGST,UOM,Order ,GST %, GST Amt,Total_GST:total gst amount
Qty,Customer Price,GSTRate,Amount,Disc % ,Disc Amt ,Cess % ,Cess Amt
        - place_of_supply: The location where goods/services are supplied.
        - gst_number: The GST identification number of the customer or supplier.
        - remarks: Any remarks or notes related to the invoice.
        - counter_sale: Indicates if the sale was a counter sale (boolean or text).
        - tax_collection_at_source: If applicable, details regarding TCS (Tax Collected at Source).
    - supplier:
        - name: The name of the supplier.
        - address: The address of the supplier.
        - contact_number: The contact number of the supplier.
        - gst_registration_number: The GST registration number of the supplier.
    - items: quantity: The quantity of the item.
        - rate: The rate/price per item.
        - taxable_amount: The taxable amount for the item.
        - discount: The discount percentage (if applicable). Ensure that if two discount values appear (one under the other), both are captured.
        - part_total: The total price for the item after considering quantity and discount.
        Total Amt(Incl.Taxes):total Amt
        - Ensure that multiple similar items or rows in the table are captured properly, even if the rows span across multiple pages or lines.
    - totals:
        - net_total: The net total amount of the invoice before taxes.
        - cgst_total: The total CGST (Central GST) amount for the invoice.
        - sgst_total: The total SGST (State GST) amount for the invoice.
        - grand_total: The grand total, including taxes.
        -totaltax_amount:total
    - other_details:
        - payment_terms: Payment terms or due date for payment.
        - mode_of_payment: The method of payment used (e.g., Cash, Credit, etc.)
        
        - order_number: The order number associated with the invoice (if available).
        - delivery_date: The expected or actual delivery date of the goods or services.
        - gst_invoice_type: Whether the invoice is a GST-compliant invoice or not.
     Ensure there are no missing fields and that data from each page is included.

. **No Truncation**: 
- If the document has multiple pages, continue generating data from each page. Do not omit any rows or items, even if they are similar to previous ones.
- The result must not include "..." between rows or truncation in any field.

. **End of Output**: 
- When the entire document is processed, make sure all the data from all pages is captured in the final output.

    Text to convert:
    {text}
    """
    
    # Get the response from OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI that extracts and structures invoice data in JSON format."},
                {"role": "user", "content": prompt}
            ]
        )

        json_text = response["choices"][0]["message"]["content"].strip()

        # Save raw output in utf-8 encoding
        raw_output_path = os.path.join(output_folder, "raw_output.json")
        with open(raw_output_path, "w", encoding="utf-8") as raw_file:
            raw_file.write(json_text)

        # Logging raw response for debugging
        print("Raw OpenAI Response saved to file:")
        print(json_text)

        # Remove Markdown JSON code block formatting if present
        if json_text.startswith("```json"):
            json_text = json_text[7:]  # Remove "```json" prefix
        if json_text.endswith("```"):
            json_text = json_text[:-3]  # Remove "```" suffix

        # Try parsing the response as JSON
        try:
            json_data = json.loads(json_text)

            # Ensure the 'items' field is a list and includes all rows, even if from multiple pages
            if 'items' not in json_data:
                print("Error: 'items' not found in the response.")
            else:
                # If the items are not stored correctly, we might need to manually clean and restructure the list.
                items = json_data.get('items', [])
                expected_item_count = 31  # Update this based on your expected number of items
                if len(items) != expected_item_count:
                    print(f"Warning: Expected {expected_item_count} rows, but found {len(items)}")
                   
                    missing_rows = expected_item_count - len(items)
                    print(f"Warning: Missing {missing_rows} items.")
                    
                for item in items:
                    if "discount" in item and isinstance(item["discount"], list):
                        upper_discount, lower_discount = item["discount"]
                        item["upper_discount_percentage"] = upper_discount  # Store the upper discount value (percentage)
                        item["lower_discount_amount"] = lower_discount  # Store the lower discount value (amount)
                        del item["discount"]    
                # Save the corrected JSON output to a file in utf-8 encoding
                with open(output_path, "w", encoding="utf-8") as json_file:
                    json.dump(json_data, json_file, indent=4, ensure_ascii=False)

            print(f"Successfully converted {pdf_path} to {output_path}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for {pdf_path}. Raw OpenAI response:")
            print(json_text)
            print(f"JSON Decode Error: {e}")
            cleaned_json = json_text.replace("\n", " ").replace("  ", " ")  # Remove unnecessary spaces and line breaks
            try:
                json_data = json.loads(cleaned_json)
                # Save the cleaned output
                with open(output_path, "w", encoding="utf-8") as json_file:
                    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
            except json.JSONDecodeError as manual_error:
                 print(f"Manual cleanup failed: {manual_error}")

    except Exception as e:
        print(f"Error in API call or response for {pdf_path}: {str(e)}")

# Main execution
if __name__ == "__main__":
    # Define paths
    data_folder = "data"
    output_folder = "output"
    os.makedirs(output_folder, exist_ok=True)

    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each PDF in the data folder
    for filename in os.listdir(data_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(data_folder, filename)
            json_filename = filename.replace(".pdf", ".json")
            output_path = os.path.join(output_folder, json_filename)

            # Convert PDF to JSON
            pdf_to_json(pdf_path, output_path)
