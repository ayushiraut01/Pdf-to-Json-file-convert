# Pdf-to-Json-file-convert

Initialization of the process.
System prepares for PDF processing.
Load PDF Files

Scan Directory for PDFs: The system looks into a specified directory (e.g., data/) for PDF files.
Extract Text from Each PDF: Once the PDF files are located, they are opened and processed to extract the text.
Extract Text

Use smalot/pdfparser: A Python or Laravel-based parser (such as smalot/pdfparser or a similar library) is used to extract raw text from the PDF file, preserving the structure, such as headers, tables, paragraphs, and other relevant data.
Send Data to OpenAI

Format the Extracted Text in a Prompt: The extracted text is carefully structured into a format that GPT-4 can process efficiently. This includes preparing the prompt to request a structured JSON output.
Send the Prompt to the OpenAI API: The formatted text prompt is sent via an API request to OpenAI's GPT-4 model, which is capable of converting the extracted text into structured data.
Receive JSON Response

Parse the OpenAI Response as JSON: Once OpenAI processes the request, the response is received in JSON format, which may contain structured data such as invoice details, items, totals, etc.
Validate & Clean Data

Ensure All Required Fields Are Present: The system checks if the response contains all required fields (like invoice_number, customer_name, items, totals).
Handle Missing or Invalid Data: If fields are missing or invalid, additional validation or cleanup procedures may be triggered to ensure data consistency.
Save JSON to File

Save the Structured JSON to an Output Folder: After validation, the clean JSON data is saved to a designated output directory (e.g., output/) in a .json file format.
