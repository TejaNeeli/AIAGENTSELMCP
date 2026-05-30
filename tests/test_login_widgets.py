import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://awsqa2.tms-orbcomm.com"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # uncomment for CI
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


EXPECTED_WIDGETS = [
    "Asset Search",
    "Asset Map",
    "Reefers with Alarms – Fleet",
    "Reefer Fleet Overview",
    "Reefer Grid",
    "Reefer History Grid",
    "PTI Results",
    "CargoCare Alerts - Fleet",
    "Dry Grid",
    "Total Drys",
    "Dry History Grid",
    "Dry Fleet Overview",
]


def test_login_and_orbcomm_maritime_title(driver):
    """Test that login succeeds and ORBCOMM MARITIME title is displayed."""
    # Step 1 - Navigate to login page
    driver.get(f"{BASE_URL}/")

    # Step 2 - Assert ORBCOMM MARITIME brand on login page
    wait = WebDriverWait(driver, 15)
    maritime_brand = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.navbar-brand"))
    )
    assert "MARITIME" in maritime_brand.text, (
        f"Expected 'MARITIME' in brand text, got: '{maritime_brand.text}'"
    )

    # Step 3 - Enter credentials
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Username']").send_keys(
        "FO_CROWLEY"
    )
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']").send_keys(
        "test@123"
    )

    # Step 4 - Click Sign In
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Step 5 - Assert redirect to /home
    wait.until(EC.url_contains("/home"))
    assert "/home" in driver.current_url, (
        f"Expected URL to contain '/home', got: {driver.current_url}"
    )

    # Step 6 - Assert ORBCOMM MARITIME still visible in navbar post-login
    maritime_nav = driver.find_element(By.CSS_SELECTOR, "a.navbar-brand")
    assert "MARITIME" in maritime_nav.text, (
        f"Post-login: Expected 'MARITIME' in nav brand, got: '{maritime_nav.text}'"
    )


def test_all_widgets_loaded(driver):
    """Test that all expected widgets are present in the DOM after login."""
    # Step 1 - Login
    driver.get(f"{BASE_URL}/")
    wait = WebDriverWait(driver, 15)

    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Username']").send_keys(
        "FO_APPLE"
    )
    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Password']").send_keys(
        "test@123"
    )
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.url_contains("/home"))

    # Step 2 - Wait for the homepage grid to load
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".homepage-grid-container"))
    )

    # Step 3 - Collect all widget/panel header texts
    widget_headers = driver.find_elements(
        By.CSS_SELECTOR, "[class*='widget-header'], [class*='panel-header']"
    )
    found_titles = [h.text.strip() for h in widget_headers if h.text.strip()]

    # Step 4 - Assert each expected widget is present
    missing_widgets = []
    for expected in EXPECTED_WIDGETS:
        match = any(expected in title for title in found_titles)
        if not match:
            missing_widgets.append(expected)

    assert not missing_widgets, (
        f"The following widgets were NOT found on the home page:\n"
        + "\n".join(f"  - {w}" for w in missing_widgets)
        + f"\n\nFound widgets:\n"
        + "\n".join(f"  + {t}" for t in found_titles)
    )
