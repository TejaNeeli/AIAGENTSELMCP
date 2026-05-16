from selenium.webdriver.common.by import By
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for https://www.example.com (replace with your target URL)."""

    URL = "https://www.example.com"

    # Locators
    HEADING = (By.TAG_NAME, "h1")

    def open_home(self):
        self.open(self.URL)

    def get_heading_text(self):
        return self.get_text(self.HEADING)
