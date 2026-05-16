import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session")
def driver():
    """Session-scoped WebDriver fixture with automatic ChromeDriver management."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Uncomment for headless execution:
    # options.add_argument("--headless=new")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()
