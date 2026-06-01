import pytest
from selenium import webdriver


def pytest_addoption(parser):
    parser.addoption(
        "--browser_name",action="store",default = "chrome"
    )
driver = None

@pytest.fixture(scope="session")
def driver(request):
    global driver
    Chrome_options = webdriver.ChromeOptions()
    Chrome_options.add_argument("--ignore-certificate-errors")
    Edge_options = webdriver.EdgeOptions()
    Edge_options.add_argument("--ignore-certificate-errors")
    browsername = request.config.getoption("browser_name")
    if browsername == "chrome":
        driver = webdriver.Chrome(options = Chrome_options)
    elif browsername == "firefox":
        driver = webdriver.Firefox()
    elif browsername == "edge":
        driver = webdriver.Edge(options = Edge_options)
    driver.get("https://awsqa2.tms-orbcomm.com/home")
    driver.maximize_window()
    # driver.implicitly_wait(120)
    request.cls.driver = driver
    yield
    driver.quit()