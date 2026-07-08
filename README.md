# Farmfoods Vouchers — Home Assistant Integration

Scrapes your personal Farmfoods voucher page and exposes each active voucher as a Home Assistant sensor entity, with a companion button to mark each voucher as used.

## Features

- Active vouchers appear automatically as sensor entities (state = voucher code)
- Each sensor carries attributes: `discount`, `valid_from`, `expires`, `used`
- A **Mark as Used** button per voucher — press it after redeeming to track what you've used
- The `used` flag persists across Home Assistant restarts
- Vouchers are automatically removed from HA when the Farmfoods site marks them as redeemed
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

For each active voucher, two entities are created:

| Entity | Type | Example |
|--------|------|---------|
| `sensor.farmfoods_5_off_when_you_spend_60` | Sensor | State: `IJ-YP-GB-41` |
| `button.mark_as_used_5_off_when_you_spend_60` | Button | Press to mark as used |

### Sensor attributes

| Attribute | Example |
|-----------|---------|
| `discount` | `£5 off when you spend £60` |
| `valid_from` | `06/07/2026` |
| `expires` | `13/07/2026` |
| `used` | `false` |

## Example automation

```yaml
automation:
  - alias: Notify when new Farmfoods voucher arrives
    trigger:
      - platform: event
        event_type: state_changed
    condition:
      - condition: template
        value_template: >
          {{ trigger.event.data.entity_id | regex_search('sensor.farmfoods_') and
             trigger.event.data.new_state is not none and
             trigger.event.data.old_state is none }}
    action:
      - service: notify.mobile_app
        data:
          title: "New Farmfoods Voucher 🛒"
          message: >
            {{ state_attr(trigger.event.data.entity_id, 'discount') }}
            — Code: {{ states(trigger.event.data.entity_id) }}
            — Expires: {{ state_attr(trigger.event.data.entity_id, 'expires') }}
```
