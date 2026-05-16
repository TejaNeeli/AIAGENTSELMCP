from pages.home_page import HomePage


class TestHomePage:
    """Sample tests for the home page."""

    def test_page_title(self, driver):
        page = HomePage(driver)
        page.open_home()
        assert "Example" in page.title

    def test_heading_text(self, driver):
        page = HomePage(driver)
        page.open_home()
        assert page.get_heading_text() == "Example Domain"
