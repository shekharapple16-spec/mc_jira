# dom_extractor.py
from playwright.async_api import async_playwright

async def extract_dom_and_locators(url: str):
    """
    Opens the URL with Playwright asynchronously, extracts DOM elements,
    and generates Selenium + Playwright locators.
    """

    locator_data = []

    async with async_playwright() as p:
        # Await the async launch properly
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        elements = await page.query_selector_all("*")

        for el in elements[:200]:  # limit to avoid overload
            try:
                tag = await el.evaluate("e => e.tagName.toLowerCase()")
                id_attr = await el.get_attribute("id")
                cls = await el.get_attribute("class")
                role = await el.get_attribute("role")
                text = await el.inner_text()

                playwright_locators = []
                selenium_locators = []

                if id_attr:
                    playwright_locators.append(f"page.locator('#{id_attr}')")
                    selenium_locators.append(f"driver.find_element(By.ID, '{id_attr}')")

                if cls:
                    cls_clean = ".".join(cls.split())
                    playwright_locators.append(f"page.locator('css={tag}.{cls_clean}')")
                    selenium_locators.append(f"driver.find_element(By.CSS_SELECTOR, '{tag}.{cls_clean}')")

                if text and len(text.strip()) < 40:
                    playwright_locators.append(f"page.get_by_text('{text.strip()}')")
                    selenium_locators.append(f"driver.find_element(By.XPATH, \"//*[text()='{text.strip()}']\")")

                locator_data.append({
                    "tag": tag,
                    "text": text.strip() if text else None,
                    "id": id_attr,
                    "class": cls,
                    "role": role,
                    "playwright": playwright_locators,
                    "selenium": selenium_locators,
                })

            except Exception:
                continue

        await browser.close()

    return locator_data
