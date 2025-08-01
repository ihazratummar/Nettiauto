# 🚗 Nettiauto Bot User Guide 🚗

Welcome to the Nettiauto Bot! This guide will help you understand how to use the bot to find car listings from Nettiauto.com directly in your Discord server.

---

## A. Getting Started (Admin Only)

Before anyone can use the bot, an administrator needs to invite it to your Discord server.



---

## B. How the Bot Works

The bot works in two main ways:

1.  **Scheduled Alerts:** It automatically checks Nettiauto.com every hour for new car listings that match your server's saved criteria.
2.  **Manual Scraping:** You can also trigger a manual search at any time using a command.

---

## C. Manual Scraping: `/scrap`

Want to check for new cars right now? Use the `/scrap` command!

*   **Command:** `/scrap`
*   **What it does:** Triggers an immediate search for cars based on your server's configured filters.
---

## D. Understanding Car Alerts

When the bot finds a car that matches your criteria, it will post a detailed message (called an "embed") in your notification channel.


Each alert will include:
*   **Title:** The make and model of the car.
*   **Price:** How much the car costs.
*   **Location:** Where the car is located.
*   **Year:** The car's model year.
*   **Mileage:** How many kilometers the car has driven.
*   **Engine Size:** The size of the car's engine.
*   **Fuel Type:** The type of fuel the car uses (e.g., Bensiini, Diesel).
*   **Link:** A direct link to the car's listing on Nettiauto.com.
*   **Image:** A picture of the car.

---

## E. Configuration Commands (Admin Only)

These commands allow server administrators to customize what cars the bot searches for and where it posts them.


### 1. `/show_config`
*   **Description:** Displays the current scraping and filtering settings for your server.
*   **Usage:** `/show_config`

### 2. `/set_channel`
*   **Description:** Sets the Discord channel where the bot will post car alerts.
*   **Usage:** `/set_channel channel: #your-alerts-channel`
*   **Example:** `/set_channel channel: #car-deals`

### 3. `/add_url`
*   **Description:** Adds a Nettiauto.com search URL for the bot to monitor.
*   **Usage:** `/add_url url: <your_nettiauto_search_url>`
*   **Example:** `/add_url url: https://www.nettiauto.com/hakutulokset?haku=P123456789`

### 4. `/remove_url`
*   **Description:** Removes a previously added search URL.
*   **Usage:** `/remove_url url: <your_nettiauto_search_url>`
*   **Example:** `/remove_url url: https://www.nettiauto.com/hakutulokset?haku=P123456789`

### 5. `/set_filter_range`
*   **Description:** Sets minimum and maximum values for numeric filters like year, price, mileage (km), or engine size.
*   **Usage:** `/set_filter_range filter_name: <filter_name> min_value: <min> max_value: <max>`
*   **`filter_name` options:** `year`, `price`, `km`, `engine_size`
*   **Examples:**
    *   `/set_filter_range filter_name: year min_value: 2000 max_value: 2015`
    *   `/set_filter_range filter_name: price min_value: 500 max_value: 5000`
    *   `/set_filter_range filter_name: km min_value: 10000 max_value: 150000`
    *   `/set_filter_range filter_name: engine_size min_value: 1.0 max_value: 2.5`

### 6. `/add_filter_item`
*   **Description:** Adds an item to a list-based filter, such as engine type or location.
*   **Usage:** `/add_filter_item filter_name: <filter_name> item: <item_to_add>`
*   **`filter_name` options:** `engine_type`, `location`
*   **Examples:**
    *   `/add_filter_item filter_name: engine_type item: Bensiini`
    *   `/add_filter_item filter_name: location item: Salo`
    *   `/add_filter_item filter_name: location item: Pori`

### 7. `/remove_filter_item`
*   **Description:** Removes an item from a list-based filter.
*   **Usage:** `/remove_filter_item filter_name: <filter_name> item: <item_to_remove>`
*   **`filter_name` options:** `engine_type`, `location`
*   **Examples:**
    *   `/remove_filter_item filter_name: engine_type item: Diesel`
    *   `/remove_filter_item filter_name: location item: Helsinki`

### 8. `/set_interval`
*   **Description:** Sets how often the bot automatically checks for new listings (in seconds).
*   **Usage:** `/set_interval interval: <seconds>`
*   **Example:** `/set_interval interval: 3600` (for every 1 hour)

---

## F. Important Notes

*   **Permissions:** Only users with the `Manage Guild` permission in Discord can use the configuration commands.
*   **Restart Bot:** After making changes to the configuration using commands, the bot might need a restart (by its owner) for some changes (like the scraping interval) to take full effect.
*   **Filtering Logic:** The bot will only post cars that match *all* the filters you set. If you set too many strict filters, you might not get any results!
*   **Troubleshooting:** If the bot isn't posting anything, check your `/show_config` to ensure your filters are not too restrictive and that the URLs are correct.

---

Enjoy finding your next car with the Nettiauto Bot!
