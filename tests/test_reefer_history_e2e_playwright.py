import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)

BASE_URL = "https://awsqa2.tms-orbcomm.com"

# Self-healing selector lists — tries each in order until one works
USERNAME_SELECTORS = [
    (By.CSS_SELECTOR, "#txtUserName"),
    (By.CSS_SELECTOR, "input[name='UserName']"),
    (By.CSS_SELECTOR, "input[placeholder='Username']"),
    (By.CSS_SELECTOR, "input[aria-label='Username']"),
    (By.XPATH, "//input[@type='text'][1]"),
]

PASSWORD_SELECTORS = [
    (By.CSS_SELECTOR, "#txtPassWord"),
    (By.CSS_SELECTOR, "input[aria-label='Password field']"),
    (By.CSS_SELECTOR, "input[type='password']"),
    (By.CSS_SELECTOR, "input[name='Password']"),
    (By.CSS_SELECTOR, "input[placeholder='Password']"),
]

SIGN_IN_SELECTORS = [
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.XPATH, "//button[contains(text(),'Sign In')]"),
    (By.CSS_SELECTOR, "button.btn-primary"),
    (By.CSS_SELECTOR, "button[aria-label='Sign In']"),
]

ASSET_ID_SELECTORS = [
    (By.CSS_SELECTOR, "textarea[placeholder='Asset ID(s)']"),
    (By.CSS_SELECTOR, "#AdvanceSearch textarea"),
    (By.XPATH, "//textarea[contains(@placeholder,'Asset')]"),
    (By.CSS_SELECTOR, "input[aria-label='Asset ID(s)']"),
    (By.CSS_SELECTOR, "input[placeholder*='Asset']"),
]

SEARCH_BTN_SELECTORS = [
    (By.XPATH, "//form[@id='AdvanceSearch']//button[text()='Search']"),
    (By.XPATH, "//div[@id='AdvanceSearch']//button[text()='Search']"),
    (By.XPATH, "(//button[text()='Search'])[1]"),
]

REEFER_GRID_SELECTORS = [
    (By.XPATH, "//div[contains(@class,'ag-cell') and contains(text(),'GRJT0000001')]"),
    (By.XPATH, "//div[@role='gridcell' and contains(text(),'GRJT0000001')]"),
    (By.XPATH, "//*[@role='gridcell'][contains(.,'GRJT0000001')]"),
    (By.XPATH, "//span[contains(text(),'GRJT0000001')]"),
]

# HISTORY_TITLE_SELECTORS = [
#     (By.XPATH, "//*[contains(text(),'Trace of GRJT0000001')]"),
#     (By.XPATH, "//*[contains(text(),'Reefer History') and contains(text(),'GRJT0000001')]"),
#     (By.XPATH, "//div[contains(@class,'widget')]//*[contains(text(),'GRJT0000001')]"),
#     (By.XPATH, "//*[@id='ReeferHistoryGrid']//*[contains(text(),'GRJT0000001')]"),
# ]

HISTORY_ROWS_SELECTORS = [
    (By.CSS_SELECTOR, "#ReeferHistoryGrid .ag-center-cols-container .ag-row"),
    (By.CSS_SELECTOR, "#ReeferHistoryGrid .ag-body-viewport .ag-row"),
    (By.XPATH, "//div[@id='ReeferHistoryGrid']//div[contains(@class,'ag-row')]"),
    (By.CSS_SELECTOR, "#ReeferHistoryGrid [role='row'][row-index]"),
]


def find_element_self_healing(driver, selectors, wait_time=15, description="element"):
    """Try multiple selectors until one works. Returns the element found."""
    ignored = (NoSuchElementException, StaleElementReferenceException)
    for by, selector in selectors:
        try:
            element = WebDriverWait(driver, wait_time, ignored_exceptions=ignored).until(
                EC.presence_of_element_located((by, selector))
            )
            print(f"  [HEAL] Found '{description}' using: ({by}, {selector!r})")
            return element
        except TimeoutException:
            continue
    raise TimeoutException(
        f"Self-healing failed: could not locate '{description}' with any selector.\n"
        f"Tried: {selectors}"
    )


def find_clickable_self_healing(driver, selectors, wait_time=15, description="element"):
    """Try multiple selectors until a clickable element is found."""
    ignored = (NoSuchElementException, StaleElementReferenceException)
    for by, selector in selectors:
        try:
            element = WebDriverWait(driver, wait_time, ignored_exceptions=ignored).until(
                EC.element_to_be_clickable((by, selector))
            )
            print(f"  [HEAL] Clickable '{description}' using: ({by}, {selector!r})")
            return element
        except TimeoutException:
            continue
    raise TimeoutException(
        f"Self-healing failed: could not click '{description}' with any selector.\n"
        f"Tried: {selectors}"
    )


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # uncomment for CI
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()


def test_login(driver):
    """Scenario 1: Login to Maritime Platform"""
    driver.get(f"{BASE_URL}/")
    time.sleep(3)  # Allow initial page load

    # Enter credentials with self-healing selectors
    username_field = find_element_self_healing(driver, USERNAME_SELECTORS, description="Username")
    username_field.clear()
    username_field.send_keys("FO_APPLE")

    password_field = find_element_self_healing(driver, PASSWORD_SELECTORS, description="Password")
    password_field.clear()
    password_field.send_keys("test@123")

    # Click Sign In
    sign_in_btn = find_clickable_self_healing(driver, SIGN_IN_SELECTORS, description="Sign In")
    sign_in_btn.click()

    # Assert redirect to /home
    WebDriverWait(driver, 20).until(EC.url_contains("/home"))
    assert "/home" in driver.current_url
    print("  [PASS] Login successful — redirected to /home")


def test_reefer_search_and_history(driver):
    """Scenarios 1-8: Full E2E - Login, Search, Grid, Click, History"""
    # --- Scenario 1: Login ---
    driver.get(f"{BASE_URL}/")
    time.sleep(3)

    username_field = find_element_self_healing(driver, USERNAME_SELECTORS, description="Username")
    username_field.clear()
    username_field.send_keys("FO_APPLE")

    password_field = find_element_self_healing(driver, PASSWORD_SELECTORS, description="Password")
    password_field.clear()
    password_field.send_keys("test@123")

    sign_in_btn = find_clickable_self_healing(driver, SIGN_IN_SELECTORS, description="Sign In")
    sign_in_btn.click()

    WebDriverWait(driver, 20).until(EC.url_contains("/home"))
    assert "/home" in driver.current_url
    print("  [PASS] Scenario 1: Login successful")

    # --- Scenario 5: Asset Search ---
    # Wait for the Asset Search form to be present in DOM
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#AdvanceSearch"))
    )
    time.sleep(2)
    asset_id_input = find_element_self_healing(
        driver, ASSET_ID_SELECTORS, wait_time=20, description="Asset ID(s)"
    )
    time.sleep(3)
    asset_id_input.clear()
    asset_id_input.send_keys("GRJT0000001")
    print("  [PASS] Scenario 5: Asset ID entered")

    time.sleep(2)
    # Click Search button
    search_btn = find_clickable_self_healing(
        driver, SEARCH_BTN_SELECTORS, description="Search button"
    )
    search_btn.click()
    print("  [PASS] Scenario 5: Search clicked")

    # --- Scenario 6: Verify Reefer in Grid ---
    time.sleep(10)  # Allow grid to load results
    reefer_grid = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Reefer Grid')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", reefer_grid)
    time.sleep(2)
    reefer_cell = find_element_self_healing(
        driver, REEFER_GRID_SELECTORS, wait_time=20, description="GRJT0000001 in Reefer Grid"
    )
    assert "GRJT0000001" in reefer_cell.text, f"Expected GRJT0000001 but got: {reefer_cell.text}"
    print("  [PASS] Scenario 6: Reefer visible in grid")

    # --- Scenario 7: Click on Reefer Record ---
    reefer_cell.click()
    print("  [PASS] Scenario 7: Clicked reefer record")

    # --- Scenario 8: Verify Reefer History ---
    time.sleep(5)  # Allow history to load

    # Verify history title updated with asset ID
    # history_title = find_element_self_healing(
    #     driver, HISTORY_TITLE_SELECTORS, wait_time=20, description="Reefer History title"
    # )
    # assert "Reefer History" in history_title.text
    # print("  [PASS] Scenario 8: History title contains 'Reefer History'")

    # Verify history rows are present
    reefer_history_grid = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Reefer History Grid ')]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", reefer_history_grid)
    time.sleep(2)
    history_rows = None
    for by, selector in HISTORY_ROWS_SELECTORS:
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((by, selector))
            )
            history_rows = driver.find_elements(by, selector)
            if history_rows:
                break
        except TimeoutException:
            continue

    assert history_rows and len(history_rows) > 0, "Reefer history records not found"
    time.sleep(3)
    print(f"  [PASS] Scenario 8: Reefer history visible with {len(history_rows)} records")
