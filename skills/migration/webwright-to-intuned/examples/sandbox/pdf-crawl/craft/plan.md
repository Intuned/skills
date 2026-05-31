# Critical Points
- [ ] CP1: Open the Intuned sandbox PDFs page at the provided start URL and show the products table is visible.
- [ ] CP2: Extract every row's product name and manufacturer from the table together with the corresponding "Specs file" PDF URL.
- [ ] CP3: Crawl all available pagination if present, or explicitly log that no pagination controls/pages were found.
- [ ] CP4: De-duplicate the collected PDF URLs so the final result list contains unique PDF documents only.
- [ ] CP5: Produce and log the complete final list of records with product name, manufacturer, and PDF URL, plus the total count.

# Parameters
- start_url (str): The PDFs listing page to crawl — from task phrase "Go to the Intuned sandbox PDFs page (https://sandbox.intuned.dev/pdfs)" — default `https://sandbox.intuned.dev/pdfs`
- max_pages (int): Maximum number of listing pages to crawl as a safety bound when pagination is present — from task phrase "Crawl the page (and any pagination if present)" — default `25`

# Fixed (NOT parameterised)
- Site domain and table-based extraction strategy stay hard-coded because they are intrinsic to this specific Intuned sandbox page structure.
- Screenshot naming, run folder structure, and log file instrumentation stay fixed to satisfy the benchmark's verification requirements.
