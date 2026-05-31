# Critical Points
- [ ] CP1: Open the Books to Scrape homepage at `https://books.toscrape.com/` and show the catalogue listing page.
- [ ] CP2: Identify individual book cards on a catalogue listing page and extract their detail page links.
- [ ] CP3: Follow the visible `next` pagination control from one listing page to the subsequent catalogue page.
- [ ] CP4: Continue pagination until the final catalogue page where no further `next` control is available.
- [ ] CP5: Produce a complete de-duplicated list of individual book detail page URLs gathered from all catalogue listing pages.
- [ ] CP6: Report the final total count of unique book detail page URLs.
- [ ] CP7: Save screenshots and action-log evidence showing the homepage, at least one intermediate pagination step, the final page state, and the final collected-result summary.

# Parameters
- start_url (str): Starting catalogue URL to begin crawling from — from task phrase "starting from the homepage" — default `https://books.toscrape.com/`
- output_json_name (str): Filename for the JSON artifact containing the complete de-duplicated list and total count — from task phrase "Return the complete, de-duplicated list of book detail page URLs along with the total count" — default `book_urls.json`

# Fixed (NOT parameterised)
- Site domain and Browserbase session usage stay hard-coded because the benchmark requires Books to Scrape and Browserbase cloud sessions.
- Extraction strategy using book-card anchors and the visible `next` pagination control stays hard-coded because it is the site-specific mechanism being validated.
- Run-folder logging and screenshot naming stay hard-coded because the benchmark requires specific artifact locations and instrumentation.
