# User Story: Find the Playwright Getting Started Guide

## Story

As a developer new to Playwright,  
I want to open the Playwright documentation and navigate to the Getting Started guide,  
so that I can find the instructions for setting up my first browser test.

## Context

- **Application:** Playwright documentation website
- **Starting URL:** <https://playwright.dev/>
- **Browser coverage:** Chromium, Firefox, and WebKit
- **User state:** No account or prior setup required

## Acceptance Criteria

### 1. Open the documentation home page

**Given** I am using a supported browser  
**When** I open the starting URL  
**Then** the page title identifies Playwright  
**And** the home page is displayed.

### 2. Navigate to the Getting Started guide

**Given** the Playwright documentation home page is displayed  
**When** I select the “Get started” link  
**Then** I am taken to the Getting Started documentation  
**And** a heading named “Installation” is visible.

### 3. Keep navigation accessible

**Given** the documentation home page is displayed  
**When** I navigate the page using accessible roles and names  
**Then** the “Get started” link can be located as a link  
**And** it can be activated without relying on positional selectors.

## Test Notes

- Prefer role-based locators, such as `getByRole('link', { name: 'Get started' })`.
- Assert user-visible outcomes rather than implementation details.
- Do not depend on a logged-in account, browser storage, or test ordering.
- These checks require access to the public Playwright documentation website.
