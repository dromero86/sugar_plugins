# Extract Table Selenium Plugin

A powerful Sugar plugin for extracting data from HTML tables using Selenium WebDriver. This plugin provides advanced table extraction capabilities with support for dynamic content, JavaScript-rendered tables, and complex table structures.

## Features

- **Dynamic Content Support**: Extract data from JavaScript-rendered tables
- **Complex Table Structures**: Handle colspan, rowspan, and multi-header tables
- **Advanced Filtering**: Filter rows and columns based on various criteria
- **Data Transformations**: Transform extracted data with built-in functions
- **Pagination Support**: Extract data from multi-page tables
- **Validation**: Validate extracted data with custom rules
- **Multiple Browser Support**: Chrome, Firefox, and Edge
- **Headless Mode**: Run browsers in headless mode for automation

## Installation

### Prerequisites

- Python 3.7 or higher
- Sugar Language framework
- Web browser (Chrome, Firefox, or Edge)

### Install Dependencies

```bash
pip install selenium>=4.0.0 webdriver-manager>=3.8.0
```

### Plugin Installation

1. Copy the `extract_table_selenium` folder to your Sugar plugins directory
2. The plugin will be automatically discovered by Sugar's plugin manager

## Usage

### Basic Table Extraction

```json
{
    "task": [
        {
            "plugin": {
                "name": "extract_table_selenium",
                "command": "extract_table",
                "config": {
                    "url": "https://example.com/table-page",
                    "selector": "table",
                    "config": {
                        "headers": "first_row",
                        "format": "objects",
                        "scope": "tbody"
                    },
                    "result": "table_data"
                }
            }
        },
        {
            "print": {
                "text": "Extracted data: {{table_data}}"
            }
        }
    ]
}
```

### Advanced Configuration

```json
{
    "task": [
        {
            "plugin": {
                "name": "extract_table_selenium",
                "command": "extract_table",
                "config": {
                    "url": "https://example.com/products",
                    "selector": ".product-table",
                    "config": {
                        "headers": ["Product", "Price", "Stock", "Category"],
                        "format": "objects",
                        "scope": "tbody"
                    },
                    "filters": {
                        "skip_rows": 1,
                        "max_rows": 50,
                        "skip_columns": [0],
                        "row_condition": "{{row.Price}} > 10"
                    },
                    "transform": {
                        "columns": {
                            "Price": "parse_currency(USD)",
                            "Stock": "parse_int"
                        },
                        "custom": {
                            "ID": "generate_uuid()",
                            "Discount": "{{row.Price}} * 0.1"
                        }
                    },
                    "validation": {
                        "required": ["Product", "Price"],
                        "types": {
                            "Price": "number",
                            "Stock": "integer"
                        },
                        "on_error": "skip_row"
                    },
                    "result": "products_data"
                }
            }
        }
    ]
}
```

## Configuration Options

### Table Configuration (`config`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headers` | string/array | `"first_row"` | Header configuration |
| `format` | string | `"objects"` | Output format |
| `scope` | string | `"tbody"` | Table scope |

**Header Options:**
- `"first_row"`: Use first row as headers
- `"none"`: No headers, use numeric indices
- `"skip"`: Skip header row
- `["col1", "col2"]`: Custom header array

**Format Options:**
- `"objects"`: Array of objects (default)
- `"arrays"`: Array of arrays
- `"key_value"`: Object with primary key

**Scope Options:**
- `"tbody"`: Table body only
- `"thead"`: Table headers only
- `"tfoot"`: Table footer only
- `"all"`: Entire table
- `".custom-class"`: Custom CSS selector

### Filters (`filters`)

| Option | Type | Description |
|--------|------|-------------|
| `skip_rows` | integer | Rows to skip from start |
| `max_rows` | integer | Maximum rows to extract |
| `skip_footer` | integer | Rows to skip from end |
| `skip_columns` | array | Column indices to skip |
| `required_columns` | array | Required column indices |
| `row_condition` | string | Filter rows by condition |
| `row_index` | string | Filter by row position |
| `min_columns` | integer | Minimum columns per row |

### Transformations (`transform`)

| Option | Type | Description |
|--------|------|-------------|
| `columns` | object | Column-specific transformations |
| `custom` | object | Custom field transformations |
| `rename` | object | Column renaming |

**Available Transform Functions:**
- `parse_int`: Convert to integer
- `parse_float`: Convert to float
- `parse_currency(USD)`: Parse currency
- `parse_date(%Y-%m-%d)`: Parse date
- `trim`: Remove whitespace
- `lowercase`: Convert to lowercase
- `uppercase`: Convert to uppercase
- `regex_replace(pattern)`: Regex replacement
- `substring(start,end)`: Extract substring
- `default(value)`: Set default value

### Pagination (`pagination`)

| Option | Type | Description |
|--------|------|-------------|
| `next_page` | string | CSS selector for next button |
| `max_pages` | integer | Maximum pages to process |
| `page_load_wait` | integer | Wait time between pages |
| `stop_condition` | string | Condition to stop pagination |

### Validation (`validation`)

| Option | Type | Description |
|--------|------|-------------|
| `required` | array | Required field names |
| `unique` | array | Fields that must be unique |
| `types` | object | Field type specifications |
| `on_error` | string | Error handling strategy |

**Error Handling Options:**
- `"skip_row"`: Skip invalid rows
- `"abort"`: Stop processing on error
- `"null_value"`: Set invalid values to null

### Complex Table Handling (`complex`)

| Option | Type | Description |
|--------|------|-------------|
| `colspan` | string | Handle colspan cells |
| `rowspan` | string | Handle rowspan cells |
| `header_depth` | integer | Multi-header levels |
| `multi_header_strategy` | string | Multi-header strategy |

## Browser Configuration

The plugin supports multiple browsers with configurable options:

```json
{
    "plugin_config": {
        "browser": "chrome",
        "headless": true,
        "timeout": 30,
        "implicit_wait": 10,
        "window_size": "1920x1080",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
}
```

**Supported Browsers:**
- `chrome`: Google Chrome
- `firefox`: Mozilla Firefox
- `edge`: Microsoft Edge

## Additional Commands

### Navigate to URL

```json
{
    "plugin": {
        "name": "extract_table_selenium",
        "command": "navigate_to",
        "config": {
            "url": "https://example.com",
            "wait": 5
        }
    }
}
```

### Wait for Element

```json
{
    "plugin": {
        "name": "extract_table_selenium",
        "command": "wait_for_element",
        "config": {
            "selector": ".table-container",
            "timeout": 30
        }
    }
}
```

### Take Screenshot

```json
{
    "plugin": {
        "name": "extract_table_selenium",
        "command": "take_screenshot",
        "config": {
            "filename": "table_screenshot.png"
        }
    }
}
```

### Close Browser

```json
{
    "plugin": {
        "name": "extract_table_selenium",
        "command": "close_browser"
    }
}
```

## Examples

### E-commerce Product Table

```json
{
    "task": [
        {
            "plugin": {
                "name": "extract_table_selenium",
                "command": "extract_table",
                "config": {
                    "url": "https://example-store.com/products",
                    "selector": "#products-table",
                    "config": {
                        "headers": "first_row",
                        "format": "objects",
                        "scope": "tbody"
                    },
                    "filters": {
                        "max_rows": 100,
                        "row_condition": "{{row.Stock}} > 0"
                    },
                    "transform": {
                        "columns": {
                            "Price": "parse_currency(USD)",
                            "Stock": "parse_int",
                            "Rating": "parse_float"
                        },
                        "custom": {
                            "Availability": "{{row.Stock}} > 0 ? 'In Stock' : 'Out of Stock'"
                        }
                    },
                    "validation": {
                        "required": ["Product", "Price"],
                        "types": {
                            "Price": "number",
                            "Stock": "integer",
                            "Rating": "number"
                        }
                    },
                    "result": "products"
                }
            }
        }
    ]
}
```

### Financial Data Table with Pagination

```json
{
    "task": [
        {
            "plugin": {
                "name": "extract_table_selenium",
                "command": "extract_table",
                "config": {
                    "url": "https://finance.example.com/stocks",
                    "selector": ".stock-table",
                    "config": {
                        "headers": ["Symbol", "Company", "Price", "Change", "Volume"],
                        "format": "objects",
                        "scope": "tbody"
                    },
                    "filters": {
                        "skip_rows": 1,
                        "row_condition": "{{row.Volume}} > 1000000"
                    },
                    "transform": {
                        "columns": {
                            "Price": "parse_currency(USD)",
                            "Change": "parse_float",
                            "Volume": "parse_int"
                        }
                    },
                    "pagination": {
                        "next_page": ".next-page-btn",
                        "max_pages": 5,
                        "page_load_wait": 3,
                        "stop_condition": "row_count_less_than_10"
                    },
                    "result": "stock_data"
                }
            }
        }
    ]
}
```

## Error Handling

The plugin provides comprehensive error handling:

- **WebDriver Errors**: Automatic retry and fallback mechanisms
- **Element Not Found**: Graceful handling with configurable timeouts
- **Data Validation**: Configurable error handling strategies
- **Network Issues**: Retry mechanisms for failed requests

## Performance Considerations

- Use `headless: true` for better performance in automation
- Set appropriate timeouts based on page load times
- Use specific CSS selectors for better performance
- Consider using `max_rows` to limit data extraction

## Troubleshooting

### Common Issues

1. **WebDriver not found**: Install webdriver-manager or download drivers manually
2. **Element not found**: Check CSS selectors and page structure
3. **Timeout errors**: Increase timeout values or check network connectivity
4. **Browser crashes**: Use headless mode or update browser drivers

### Debug Mode

Enable debug logging by setting the plugin configuration:

```json
{
    "plugin_config": {
        "debug": true,
        "headless": false
    }
}
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.