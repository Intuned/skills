# Critical Points
- [ ] CP1: Open the TechCrunch Startups category page so the scrape is performed on the correct TechCrunch startup-news listing.
- [ ] CP2: Show visible startup news results on the Startups page, including article titles and timestamps.
- [ ] CP3: Extract startup news entries from TechCrunch and filter them to only items whose published datetime is within the last 7 days from the run time.
- [ ] CP4: Save the scraped last-7-days startup news records to a structured output file in the run folder.
- [ ] CP5: Record the resolved CLI parameter values in `final_script_log.txt` as `step 0 params: ...` and log each critical action.
- [ ] CP6: Save verification screenshots in the run folder that show the Startups page and visible dated results used for the scrape.
- [ ] CP7: Write the final response summary, including the number of matching startup news items scraped, into `final_script_log.txt` and stdout.

# Parameters
- days_back (int): Number of trailing calendar days of startup news to include — from task phrase "last 7 days" — default `7`
- category_url (str): TechCrunch listing URL to scrape for startup news — from task phrase "TechCrunch startup news" — default `https://techcrunch.com/category/startups/`
- output_filename (str): Structured output filename for scraped records in the run folder — from task phrase "Scrape ... news" — default `startup_news_last_7_days.json`

# Fixed (NOT parameterised)
- Site name is TechCrunch — fixed by the task.
- Selector strategy for the current TechCrunch Startups listing DOM — fixed implementation detail.
- Screenshot directory and log file naming conventions — fixed by benchmark instrumentation requirements.
