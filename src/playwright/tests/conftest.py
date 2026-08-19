"""
Configuration for Playwright Plugin Tests
========================================

Pytest configuration and fixtures for testing the Playwright plugin.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the plugin path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def mock_output():
    """Mock the Output.Console to avoid actual logging during tests."""
    with patch('Sugar.Lang.Utils.Output.Output.Console') as mock:
        yield mock

@pytest.fixture
def mock_playwright():
    """Mock Playwright components for testing."""
    with patch('playwright.sync_api.sync_playwright') as mock:
        # Create a mock playwright instance
        mock_instance = Mock()
        mock.return_value.__enter__.return_value = mock_instance
        
        # Mock browser types
        mock_instance.chromium = Mock()
        mock_instance.firefox = Mock()
        mock_instance.webkit = Mock()
        
        # Mock browser launch
        mock_browser = Mock()
        mock_browser.version = "1.0.0"
        mock_instance.chromium.launch.return_value = mock_browser
        mock_instance.firefox.launch.return_value = mock_browser
        mock_instance.webkit.launch.return_value = mock_browser
        
        yield mock

@pytest.fixture
def mock_context():
    """Mock browser context for testing."""
    context = Mock()
    context.new_page.return_value = Mock()
    return context

@pytest.fixture
def mock_page():
    """Mock page for testing."""
    page = Mock()
    page.title.return_value = "Test Page"
    page.url = "https://example.com"
    page.goto.return_value = None
    page.click.return_value = None
    page.type.return_value = None
    page.fill.return_value = None
    page.screenshot.return_value = None
    page.evaluate.return_value = "test result"
    return page

@pytest.fixture
def plugin_instance():
    """Create a plugin instance for testing."""
    from PlaywrightPlugin import PlaywrightPlugin
    return PlaywrightPlugin()

@pytest.fixture
def browser_component(plugin_instance):
    """Create a browser component instance for testing."""
    return plugin_instance.browser

@pytest.fixture
def page_component(plugin_instance):
    """Create a page component instance for testing."""
    return plugin_instance.page

@pytest.fixture
def playwright_component(plugin_instance):
    """Create a playwright component instance for testing."""
    return plugin_instance.playwright

# Test data fixtures
@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "browser_type": "chromium",
        "headless": False,
        "slow_mo": 1000,
        "viewport": {
            "width": 1280,
            "height": 720
        }
    }

@pytest.fixture
def sample_navigation_config():
    """Sample navigation configuration."""
    return {
        "url": "https://example.com",
        "wait_until": "load",
        "timeout": 30000
    }

@pytest.fixture
def sample_click_config():
    """Sample click configuration."""
    return {
        "selector": "#button",
        "button": "left",
        "click_count": 1,
        "delay": 0
    }

@pytest.fixture
def sample_type_config():
    """Sample type configuration."""
    return {
        "selector": "#input",
        "text": "test text",
        "delay": 100
    }

@pytest.fixture
def sample_fill_config():
    """Sample fill configuration."""
    return {
        "selector": "#input",
        "value": "test value"
    }

@pytest.fixture
def sample_screenshot_config():
    """Sample screenshot configuration."""
    return {
        "path": "./screenshots/test.png",
        "full_page": False
    }

@pytest.fixture
def sample_evaluate_config():
    """Sample evaluate configuration."""
    return {
        "script": "return document.title;",
        "arg": None
    }

# Environment fixtures
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Create test directories
    os.makedirs("./screenshots", exist_ok=True)
    os.makedirs("./videos", exist_ok=True)
    os.makedirs("./downloads", exist_ok=True)
    
    yield
    
    # Cleanup test files (optional)
    # import shutil
    # if os.path.exists("./screenshots"):
    #     shutil.rmtree("./screenshots")
    # if os.path.exists("./videos"):
    #     shutil.rmtree("./videos")
    # if os.path.exists("./downloads"):
    #     shutil.rmtree("./downloads")

# Markers for different test types
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as requiring browser"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )

# Skip tests that require actual browser if not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip browser tests if needed."""
    skip_browser = pytest.mark.skip(reason="Browser tests require actual browser installation")
    
    for item in items:
        if "browser" in item.keywords and not has_browser_installed():
            item.add_marker(skip_browser)

def has_browser_installed():
    """Check if browsers are installed."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Try to launch a browser
            browser = p.chromium.launch(headless=True)
            browser.close()
            return True
    except Exception:
        return False
