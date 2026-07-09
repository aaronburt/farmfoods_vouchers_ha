# Farmfoods Vouchers — Home Assistant Integration

> **Disclaimer:** This is an unofficial, community-maintained project and is not affiliated with, endorsed by, or associated with Farmfoods Ltd in any way. Use at your own risk. The Farmfoods name and logo are trademarks of their respective owners.

Scrapes your personal Farmfoods voucher page and exposes a combined sensor entity of all active vouchers, with companion services to mark individual vouchers as used.

## Features

- Exposes a single sensor containing the list of active vouchers and their details
- The sensor state displays the count of active, unused vouchers
- Sensor carries attributes: `vouchers` (a list of all active vouchers), `total_vouchers`, and `unused_vouchers`
- Each voucher in the list includes: `id`, `code`, `discount`, `valid_from`, `expires`, `used`
- Companion services: `farmfoods_vouchers.mark_used` and `farmfoods_vouchers.mark_unused` to track voucher usage
- The `used` flag status is restored and persists across Home Assistant restarts
- Vouchers are automatically removed when they are no longer active/scraped on the Farmfoods website
- Includes custom brand logo and icon support for the Home Assistant dashboard
- Refreshes every 12 hours

## Requirements

- Home Assistant 2024.1.0 or newer
- [HACS](https://hacs.xyz/) installed

## Installation

1. In HACS, go to **Integrations** → three-dot menu → **Custom repositories**
2. Add this repository URL with category **Integration**
3. Find **Farmfoods Vouchers** in HACS and install it
4. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Farmfoods Vouchers**
3. Paste the full voucher URL from your Farmfoods email, e.g.:
   ```
   https://www.farmfoods.co.uk/Vouchers?campaign_id=...&id=...&email_address=...
   ```
4. Click **Submit** — the integration validates the URL live before saving

## Entities

One sensor entity is created per configured email address:

| Entity | Type | Example State |
|--------|------|---------------|
| `sensor.farmfoods_email_address_com_vouchers` | Sensor | `3` (count of unused vouchers) |

### Sensor attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `vouchers` | List of active vouchers | `[{"id": "...", "code": "...", "discount": "...", "valid_from": "...", "expires": "...", "used": false}]` |
| `total_vouchers` | Total number of active vouchers | `3` |
| `unused_vouchers` | Count of active, unused vouchers | `3` |

## Services

### Service `farmfoods_vouchers.mark_used`
Marks a specific Farmfoods voucher as used.

Parameters:
- `code` (Optional): The voucher code (e.g., `IJ-YP-GB-41`).
- `id` (Optional): The unique ID of the voucher.
*(Note: At least one of `code` or `id` must be provided.)*

### Service `farmfoods_vouchers.mark_unused`
Marks a previously used Farmfoods voucher as unused.

Parameters:
- `code` (Optional): The voucher code (e.g., `IJ-YP-GB-41`).
- `id` (Optional): The unique ID of the voucher.
*(Note: At least one of `code` or `id` must be provided.)*

## Example automation

You can use templates to loop through the vouchers. For example, to notify when a new voucher is available:

```yaml
automation:
  - alias: Notify all active Farmfoods vouchers
    trigger:
      - platform: state
        entity_id: sensor.farmfoods_aaron_gmail_com_vouchers
    action:
      - service: notify.mobile_app
        data:
          title: "Farmfoods Vouchers Update 🛒"
          message: >
            Here are your active vouchers:
            {% for voucher in state_attr('sensor.farmfoods_aaron_gmail_com_vouchers', 'vouchers') or [] %}
              - {{ voucher.discount }} (Code: {{ voucher.code }}, Expires: {{ voucher.expires }}, Used: {{ voucher.used }})
            {% endfor %}
```

## Legal Disclaimer

This project is an unofficial, community-maintained integration and is **not affiliated with, endorsed by, or associated with Farmfoods Ltd** in any way. 

By using this software, you agree to the following:
*   **Use at your own risk:** This software is provided "as is", without warranty of any kind. The maintainers assume no liability for any issues, account bans, or consequences resulting from its use.
*   **Web Scraping:** This integration automates the retrieval of your personal voucher data from the Farmfoods website. You are solely responsible for ensuring that your use of this integration complies with the Farmfoods website Terms of Service.
*   **Trademarks:** The "Farmfoods" name, logos, and related trademarks are the property of Farmfoods Ltd or their respective owners. They are used here strictly for descriptive and identification purposes.
*   **AI Assistance:** Parts of this project's code and documentation were generated with the assistance of AI to boost productivity. While reviewed for quality, please keep this in mind when using or contributing to the project.
