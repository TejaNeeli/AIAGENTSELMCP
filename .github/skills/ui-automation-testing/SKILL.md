---
name: ui-automation-testing
description: >
  Use this skill for automating UI tests on web applications using the Selenium MCP server
  integrated in VS Code. Triggers when the user asks to test a web page, verify UI behavior,
  run browser automation, check form submissions, validate navigation flows, test login/logout,
  verify element visibility, or automate any interaction with a web application. Use this skill
  whenever the user mentions "test this page", "automate UI", "check if X works", "run browser
  tests", "validate the UI", or wants to click/type/assert anything in a browser — even if they
  don't explicitly say "Selenium" or "automation testing".
compatibility:
  tools:
    - selenium (MCP server — must be connected in VS Code Insiders)
  requires: Selenium MCP server running and connected
---

# UI Automation Testing with Selenium MCP

A skill for automating UI testing of web applications using the Selenium MCP server in VS Code Insiders.

---

## Overview

This skill guides Claude to plan, execute, and report on UI automation tests using Selenium MCP tools. It covers navigation, element interaction, assertions, form testing, and structured test reporting.

---

## Core Testing Workflow

Always follow this sequence for every test session:

```
1. Understand the test goal (what to verify)
2. Start the browser session
3. Navigate to the target URL
4. Interact with elements (click, type, select)
5. Assert expected outcomes (text, visibility, URL)
6. Capture screenshots at key checkpoints
7. Close the session
8. Report results clearly
```

---

## Step-by-Step Instructions

### Step 1 — Clarify the Test Scope

Before touching any Selenium tool, ask (if not already specified):
- What is the URL of the application?
- What scenario or user flow needs to be tested?
- What is the expected outcome (pass/fail criteria)?

If the user provides a URL and a task (e.g., "test the login page"), proceed directly.

---

### Step 2 — Start a Browser Session

Always start with `selenium:start_browser`. Default to `headless: false` so the user can watch.

```
Tool: selenium:start_browser
Parameters:
  browser: chrome        # or firefox
  headless: false        # true for CI/automated pipelines
```

---

### Step 3 — Navigate to the URL

```
Tool: selenium:navigate
Parameters:
  url: "https://example.com/login"
```

Take a screenshot immediately after navigation to confirm the page loaded.

```
Tool: selenium:take_screenshot
```

---

### Step 4 — Interact with Elements

Use CSS selectors or XPath. Prefer CSS selectors for brevity.

**Typing into an input:**
```
Tool: selenium:send_keys
Parameters:
  selector: "#username"        # CSS selector
  text: "FO_CROWLEY"
  selector: "#password"        # CSS selector
  text: "test@123"
```

**Clicking a button:**
```
Tool: selenium:interact
Parameters:
  selector: "button[type='submit']"
  action: click
```

**Getting element text (for assertions):**
```
Tool: selenium:get_element_text
Parameters:
  selector: ".error-message"
```

**Getting an attribute:**
```
Tool: selenium:get_element_attribute
Parameters:
  selector: "input#email"
  attribute: "placeholder"
```

---

### Step 5 — Assert Outcomes

Selenium MCP doesn't have a built-in assert tool. Claude performs assertions by:

1. Fetching element text or attribute with `get_element_text` / `get_element_attribute`
2. Comparing the value against the expected result
3. Marking the test PASS ✅ or FAIL ❌ in the final report

**Assertion patterns:**

| What to verify | Tool to use | What to check |
|---|---|---|
| Page title / heading | `get_element_text` on `h1` | Matches expected string |
| Error/success message | `get_element_text` on alert/toast | Contains expected text |
| URL after redirect | `execute_script` → `return window.location.href` | Equals expected URL |
| Button enabled/disabled | `get_element_attribute` → `disabled` | null = enabled, "true" = disabled |
| Element visible | `get_element_text` or `interact` — if it throws, element is absent | No error = visible |

---

### Step 6 — Handle Alerts and Popups

```
Tool: selenium:alert
Parameters:
  action: accept     # or dismiss / getText
```

---

### Step 7 — Switch Frames (if needed)

```
Tool: selenium:frame
Parameters:
  action: switch
  identifier: "iframe#content"   # CSS selector or index
```

To go back to the main page:
```
Tool: selenium:frame
Parameters:
  action: default
```

---

### Step 8 — Capture Screenshots

Take screenshots at every major checkpoint:
- After page load
- After form submission
- After navigation
- On assertion failure

```
Tool: selenium:take_screenshot
```

Name/describe each screenshot in the report so the user knows what it shows.

---

### Step 9 — Close the Session

Always close the session when done.

```
Tool: selenium:close_session
```

---

### Step 10 — Report Results

After every test run, produce a structured report (see Report Format below).

---

## Test Scenario Templates

### Login Flow Test
```
1. Navigate to /login
2. Screenshot — login page loaded
3. send_keys → #username → valid email
4. send_keys → #password → valid password
5. interact → click → button[type=submit]
6. Screenshot — after submit
7. Assert: get_element_text → .welcome-message → contains "Welcome"
   OR execute_script → return window.location.href → equals /dashboard
8. PASS if assertion holds, FAIL with screenshot if not
```

### Form Validation Test
```
1. Navigate to the form page
2. interact → click → submit (without filling fields)
3. Screenshot — validation errors visible
4. Assert: get_element_text → .field-error → contains expected error text
5. Fill fields with invalid data, repeat assertions
6. Fill with valid data → submit → assert success state
```

### Navigation / Link Test
```
1. Navigate to homepage
2. interact → click → nav link (e.g., "About")
3. Assert URL changed: execute_script → return window.location.href
4. Assert heading: get_element_text → h1 → matches expected
```

### Element Visibility Test
```
1. Navigate to page
2. Attempt get_element_text on target element
3. If tool returns text → PASS (element visible)
4. If tool throws → FAIL (element absent/hidden)
```

---

## Common Selector Patterns

```css
/* By ID */
#login-btn

/* By class */
.submit-button

/* By attribute */
input[name="email"]
button[type="submit"]

/* By text content (XPath) */
//button[text()='Sign In']

/* Nested */
form#login-form input[type="password"]

/* nth child */
ul.menu > li:nth-child(2) > a
```

---

## Executing JavaScript

Use `selenium:execute_script` for anything not covered by standard tools:

```
Tool: selenium:execute_script
Parameters:
  script: "return document.title"
```

```
Tool: selenium:execute_script
Parameters:
  script: "window.scrollTo(0, document.body.scrollHeight)"
```

```
Tool: selenium:execute_script
Parameters:
  script: "return window.location.href"
```

---

## Diagnostics

If a test behaves unexpectedly, collect diagnostics before giving up:

```
Tool: selenium:diagnostics
Parameters:
  type: console_logs    # JS errors in browser console
```

```
Tool: selenium:diagnostics
Parameters:
  type: network         # Network requests (if available)
```

---

## Report Format

After every test run, output a report using this structure:

```
## UI Test Report
**Application:** <URL>
**Scenario:** <Test scenario name>
**Date/Time:** <timestamp>
**Browser:** Chrome / Firefox
**Status:** ✅ PASSED / ❌ FAILED

---

### Test Steps

| # | Step | Action | Expected | Actual | Status |
|---|------|--------|----------|--------|--------|
| 1 | Open login page | navigate | Page loads | Page loaded | ✅ |
| 2 | Enter username | send_keys | Field accepts input | Input accepted | ✅ |
| 3 | Submit form | click | Redirect to /dashboard | Redirected correctly | ✅ |

---

### Assertions

| Assertion | Expected | Actual | Result |
|-----------|----------|--------|--------|
| Welcome message visible | "Welcome, Test User" | "Welcome, Test User" | ✅ PASS |
| URL after login | /dashboard | /dashboard | ✅ PASS |

---

### Screenshots
- Screenshot 1: Login page loaded (step 1)
- Screenshot 2: Form submitted (step 3)
- Screenshot 3: Dashboard visible (step 4)

---

### Issues Found
- None  ← or describe bugs here

### Recommendations
- <Any follow-up tests or fixes suggested>
```

---

## Error Handling Rules

- If `selenium:navigate` fails → check the URL, try again, or report "page unreachable"
- If a selector doesn't find an element → try an alternate selector, then screenshot + report "element not found"
- If a test step throws unexpectedly → run `selenium:diagnostics` (console_logs), take a screenshot, and mark that step FAIL
- Always close the session even if a test fails midway (use `selenium:close_session` in a final step)

---

## Tips

- Always take a screenshot before and after the most critical assertion
- Prefer `id` or `data-testid` attributes as selectors — they're more stable than class names
- For SPAs (React/Vue/Angular), add a brief pause via `execute_script → setTimeout` or re-check after navigation if elements don't appear immediately
- If the app uses iframes (e.g., embedded payment forms), use `selenium:frame` to switch context before interacting

---

## Reference — Selenium MCP Tool Summary

| Tool | Purpose |
|---|---|
| `selenium:start_browser` | Open browser session |
| `selenium:navigate` | Go to a URL |
| `selenium:send_keys` | Type into an input field |
| `selenium:interact` | Click, hover, or other mouse action |
| `selenium:get_element_text` | Read visible text of an element |
| `selenium:get_element_attribute` | Read an HTML attribute |
| `selenium:execute_script` | Run arbitrary JavaScript |
| `selenium:take_screenshot` | Capture current screen |
| `selenium:alert` | Handle browser alerts/confirms |
| `selenium:frame` | Switch to/from iframes |
| `selenium:diagnostics` | Get console logs or network info |
| `selenium:close_session` | End the browser session |