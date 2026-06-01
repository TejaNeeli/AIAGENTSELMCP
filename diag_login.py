"""Diagnostic script to inspect dashboard elements after login."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

options = webdriver.ChromeOptions()
options.add_argument("--ignore-certificate-errors")
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://awsqa2.tms-orbcomm.com/")
time.sleep(5)

# Login
driver.find_element(By.CSS_SELECTOR, "#txtUserName").send_keys("FO_CROWLEY")
driver.find_element(By.CSS_SELECTOR, "#txtPassWord").send_keys("test@123")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

WebDriverWait(driver, 20).until(EC.url_contains("/home"))
print("=== Logged in. URL:", driver.current_url)
time.sleep(15)  # Dashboard widgets load asynchronously

# Check for iframes
print("\n=== Checking for iframes:")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
print(f"  Found {len(iframes)} iframes")
for i, frame in enumerate(iframes):
    src = frame.get_attribute("src")
    fid = frame.get_attribute("id")
    print(f"  iframe[{i}]: id={fid} src={src}")

# Check page source for key elements
src = driver.page_source
print(f"\n=== Page source length: {len(src)} chars")
if "AdvanceSearch" in src or "advanceSearch" in src or "advance-search" in src:
    print("  'AdvanceSearch' FOUND in page source")
    idx = src.lower().find("advancesearch")
    print(f"  Context: ...{src[max(0,idx-50):idx+100]}...")
else:
    print("  'AdvanceSearch' NOT in page source")
    
if "Asset ID" in src:
    print("  'Asset ID' FOUND in page source")
    idx = src.find("Asset ID")
    print(f"  Context: ...{src[max(0,idx-50):idx+100]}...")
else:
    print("  'Asset ID' NOT in page source")

if "ReeferGrid" in src or "reefer-grid" in src:
    print("  'ReeferGrid' FOUND in page source")
else:
    print("  'ReeferGrid' NOT in page source")

# Try finding elements by class
print("\n=== Checking for widgets by class/text:")
widgets = driver.find_elements(By.XPATH, "//*[contains(text(),'Asset Search')]")
print(f"  Elements containing 'Asset Search': {len(widgets)}")
for w in widgets[:5]:
    print(f"    tag={w.tag_name} class={w.get_attribute('class')} id={w.get_attribute('id')}")

# Check total DOM element count
total = driver.execute_script("return document.querySelectorAll('*').length")
print(f"\n=== Total DOM elements: {total}")

# Check if app is inside a root element
root = driver.find_elements(By.CSS_SELECTOR, "#root, #app, .app-container")
print(f"  Root containers: {len(root)}")
for r in root:
    children = r.find_elements(By.XPATH, "./*")
    print(f"    tag={r.tag_name} id={r.get_attribute('id')} children={len(children)}")

# Find Asset Search inputs
print("\n=== Looking for Asset Search widget inputs:")
inputs = driver.find_elements(By.TAG_NAME, "input")
for inp in inputs[:30]:
    t = inp.get_attribute("type")
    n = inp.get_attribute("name")
    i = inp.get_attribute("id")
    al = inp.get_attribute("aria-label")
    ph = inp.get_attribute("placeholder")
    if al or ph or "asset" in (n or "").lower() or "asset" in (i or "").lower():
        print(f"  type={t} | name={n} | id={i} | aria-label={al} | placeholder={ph}")

print("\n=== Looking for Search buttons:")
buttons = driver.find_elements(By.TAG_NAME, "button")
for btn in buttons:
    txt = btn.text.strip()
    if "search" in txt.lower() or "Search" in txt:
        i = btn.get_attribute("id")
        cl = btn.get_attribute("class")
        parent_id = driver.execute_script("return arguments[0].closest('[id]')?.id", btn)
        print(f"  text={txt!r} | id={i} | class={cl} | parent_id={parent_id}")

print("\n=== Checking #AdvanceSearch existence:")
adv = driver.find_elements(By.CSS_SELECTOR, "#AdvanceSearch")
print(f"  Found {len(adv)} elements with id=AdvanceSearch")

print("\n=== Checking for Reefer Grid:")
rg = driver.find_elements(By.CSS_SELECTOR, "#ReeferGrid")
print(f"  Found {len(rg)} elements with id=ReeferGrid")

rh = driver.find_elements(By.CSS_SELECTOR, "#ReeferHistoryGrid")
print(f"  Found {len(rh)} elements with id=ReeferHistoryGrid")

# Enter asset ID and search
asset_input = driver.find_elements(By.CSS_SELECTOR, "input[aria-label='Asset ID(s)']")
if not asset_input:
    asset_input = driver.find_elements(By.XPATH, "//input[contains(@placeholder,'Asset')]")
if not asset_input:
    asset_input = driver.find_elements(By.XPATH, "//input[contains(@aria-label,'Asset')]")
    
if asset_input:
    print(f"\n=== Found Asset ID input: aria-label={asset_input[0].get_attribute('aria-label')}")
    asset_input[0].clear()
    asset_input[0].send_keys("DFRD0000027")
    time.sleep(1)
    
    # Click search
    search_btns = driver.find_elements(By.CSS_SELECTOR, "#AdvanceSearch button.btn-primary")
    if not search_btns:
        search_btns = driver.find_elements(By.XPATH, "//button[text()='Search']")
    if search_btns:
        print(f"  Found {len(search_btns)} Search buttons, clicking first one")
        search_btns[0].click()
        time.sleep(8)
        
        # Check what's on the page after search
        print("\n=== After search - checking for grid cells:")
        cells = driver.find_elements(By.XPATH, "//*[contains(text(),'DFRD0000027')]")
        print(f"  Elements containing 'DFRD0000027': {len(cells)}")
        for c in cells[:10]:
            tag = c.tag_name
            role = c.get_attribute("role")
            cls = c.get_attribute("class")
            parent_tag = driver.execute_script("return arguments[0].parentElement.tagName", c)
            parent_cls = driver.execute_script("return arguments[0].parentElement.className", c)
            print(f"    tag={tag} role={role} class={cls!r} | parent: {parent_tag} class={parent_cls!r}")
        
        # Also check ag-grid specific selectors
        print("\n=== ag-grid cells:")
        ag_cells = driver.find_elements(By.CSS_SELECTOR, ".ag-cell")
        print(f"  Total .ag-cell elements: {len(ag_cells)}")
        if ag_cells:
            for cell in ag_cells[:5]:
                txt = cell.text
                cls = cell.get_attribute("class")
                col = cell.get_attribute("col-id")
                print(f"    text={txt!r} col-id={col}")
        
        # Check ag-row
        ag_rows = driver.find_elements(By.CSS_SELECTOR, ".ag-row")
        print(f"  Total .ag-row elements: {len(ag_rows)}")
else:
    print("\n=== Could NOT find Asset ID input!")

driver.quit()
print("\n=== DONE ===")
