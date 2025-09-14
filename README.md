# Trello Integration for Home Assistant

A complete Home Assistant integration for Trello that provides enhanced board monitoring, card management, and visual board display capabilities.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/SebastianZ84/ha-trello)](https://github.com/SebastianZ84/ha-trello/releases)
[![GitHub](https://img.shields.io/github/license/SebastianZ84/ha-trello)](LICENSE)

## Features

- 🔗 **Full Trello API Integration** - Monitor multiple boards with real-time updates
- 🎯 **Card Management Services** - Move, create, and update cards programmatically  
- 📊 **Rich Sensor Data** - Board info, list details, card counts, and metadata
- 🏷️ **Smart Filtering** - Track cards by labels, due dates, members, and more
- 🔄 **Real-time Updates** - Automatic polling with configurable intervals
- 🎨 **Visual Board Display** - Works with [Trello Board Card](https://github.com/SebastianZ84/ha-trello-card) for full Kanban UI
- ⚡ **Performance Optimized** - Efficient API usage with intelligent caching
- 🛠️ **Developer Friendly** - Comprehensive services and event system

## Visual Board Display

This integration pairs perfectly with the [Trello Board Card](https://github.com/SebastianZ84/ha-trello-card) for a complete visual Kanban experience:

- Interactive drag & drop card movement
- Add new cards directly from Home Assistant
- Beautiful theming system with Mushroom design
- Real-time synchronization with Trello

![Trello Board Example](https://github.com/SebastianZ84/ha-trello-card/raw/main/example.png)

## Prerequisites

Before setting up this integration, you need to get credentials by creating an Integration in Trello's Power-Up Admin Portal.

Before installing, you'll need:

1. A Trello account
2. Trello API credentials (API Key and Token)
3. Home Assistant 2023.1 or later

## Getting Trello API Credentials

### Step 1: Get Your API Key

1. **Log into Trello** at [trello.com](https://trello.com)
2. **Visit the Developer API Keys page**: https://trello.com/app-key
3. **Copy your API Key** - this will be your `api_key` in Home Assistant

### Step 2: Generate an API Token

1. **On the same page**, click the **"Token"** link next to "You can manually generate a Token"
2. **Or visit directly**: https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key=YOUR_API_KEY
   - Replace `YOUR_API_KEY` with the key from Step 1
3. **Click "Allow"** to grant permissions
4. **Copy the token** - this will be your `api_token` in Home Assistant

### Step 3: Find Your Board IDs

You'll need the Board ID for each board you want to monitor:

1. **Open a Trello board** in your browser
2. **Look at the URL**: `https://trello.com/b/BOARD_ID/board-name`
3. **Copy the BOARD_ID** part (e.g., `5f4d2e1a3b8c7d9f`)
4. **Repeat for all boards** you want to monitor

**Alternative method using Trello API:**
```bash
curl "https://api.trello.com/1/members/me/boards?key=YOUR_API_KEY&token=YOUR_API_TOKEN"
```

## Installation

### Via HACS (Recommended)

1. **Open HACS** in Home Assistant
2. **Go to Integrations**
3. **Click the three dots menu** → **Custom repositories**
4. **Add repository**: `https://github.com/SebastianZ84/ha-trello`
5. **Select category**: Integration
6. **Click "Download"**
7. **Restart Home Assistant**

### Manual Installation

1. **Download the latest release** from [Releases](https://github.com/SebastianZ84/ha-trello/releases)
2. **Extract to your Home Assistant**: `custom_components/trello/`
3. **Restart Home Assistant**

## Configuration

### Via Home Assistant UI (Recommended)

1. **Go to Settings** → **Devices & Services**
2. **Click "Add Integration"** 
3. **Search for "Trello"**
4. **Enter your credentials**:
   - **API Key**: From Step 1 above
   - **API Token**: From Step 2 above
   - **Board IDs**: Comma-separated list from Step 3 above
5. **Click "Submit"**

### Via configuration.yaml (Legacy)

```yaml
# Not recommended - use UI configuration instead
sensor:
  - platform: trello
    api_key: YOUR_API_KEY
    api_token: YOUR_API_TOKEN
    board_ids:
      - "5f4d2e1a3b8c7d9f"  # Board 1
      - "6g5e3f2b4c9d8e1a"  # Board 2
```

## Available Sensors

After configuration, you'll get sensors for each board:

- `sensor.trello_board_[board_name]` - Main board sensor with all data
- Rich attributes include:
  - Board information (name, description, url)
  - All lists with cards
  - Card details (name, description, due date, labels, members)
  - Statistics (total cards, cards per list)

## Services

The integration provides powerful services for card management:

### `trello.move_card`
Move a card to a different list.

```yaml
service: trello.move_card
data:
  card_id: "5f4d2e1a3b8c7d9f"
  target_list_id: "6g5e3f2b4c9d8e1a"
```

### `trello.create_card`
Create a new card in a list.

```yaml
service: trello.create_card
data:
  list_id: "6g5e3f2b4c9d8e1a"
  name: "New Task"
  description: "Task description here"
```

### `trello.update_card`
Update a card's name and description.

```yaml
service: trello.update_card
data:
  card_id: "5f4d2e1a3b8c7d9f"
  name: "Updated Task Name"
  description: "Updated description"
```

## Example Automations

### Notify when high-priority cards are due

```yaml
automation:
  - alias: "Trello: High Priority Due Soon"
    trigger:
      - platform: time
        at: "09:00:00"
    condition:
      - condition: template
        value_template: >
          {% set cards = state_attr('sensor.trello_board_project_board', 'cards') %}
          {{ cards | selectattr('labels', 'search', 'Priority: High') 
                   | selectattr('due_date', 'defined') 
                   | list | length > 0 }}
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "High Priority Cards Due"
          message: "You have high priority cards due today!"
```

### Auto-move completed cards

```yaml
automation:
  - alias: "Trello: Move Completed Cards"
    trigger:
      - platform: webhook
        webhook_id: trello_webhook
    condition:
      - condition: template
        value_template: "{{ 'card' in trigger.json.action.type }}"
    action:
      - service: trello.move_card
        data:
          card_id: "{{ trigger.json.action.data.card.id }}"
          target_list_id: "{{ states('input_text.done_list_id') }}"
```

## Authentication Details

The integration uses **Trello's API Key + Token authentication method**, which is:

- ✅ **Officially supported** by Atlassian/Trello
- ✅ **Simple and reliable** - no complex OAuth flows
- ✅ **Secure** - tokens can be revoked anytime
- ✅ **Perfect for Home Assistant** - no callback URLs needed

**Note**: Trello does not support OAuth 2.0. The available options are API Key + Token (recommended) or OAuth 1.0a (more complex).

## Rate Limits

Trello API has the following rate limits:
- **300 requests per 10 seconds** per API key
- **100 requests per 10 seconds** per token

The integration respects these limits with intelligent caching and efficient API usage.

## Troubleshooting

### Common Issues

**"Invalid API key or token"**
- Verify your API key and token are correct
- Make sure the token has read/write permissions
- Check if the token has expired (use `expiration=never`)

**"Board not found"**
- Verify the board ID is correct
- Make sure you have access to the board
- Check if the board is archived

**"Integration not loading"**
- Check Home Assistant logs for errors
- Restart Home Assistant after installation
- Verify all board IDs are valid

### Enable Debug Logging

```yaml
logger:
  default: warning
  logs:
    custom_components.trello: debug
    trello: debug
```

## Visual Board Card

For the complete Trello experience, install the companion [Trello Board Card](https://github.com/SebastianZ84/ha-trello-card):

```yaml
type: custom:trello-board
board_id: "your_board_id_here"
show_header: true
show_card_counts: true
styles:
  card:
    background: "linear-gradient(45deg, #1e3c72, #2a5298)"
  board_title:
    color: "#ffffff"
    font-size: "24px"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

- **Issues**: [GitHub Issues](https://github.com/SebastianZ84/ha-trello/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/SebastianZ84/ha-trello/discussions)
- **Home Assistant Community**: [Home Assistant Forum](https://community.home-assistant.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- 🚀 Initial release
- 📋 Complete board monitoring with real-time updates  
- 🎯 Card management services (move, create, update)
- 🔗 Integration with visual Trello Board Card
- 📊 Rich sensor data with full board information
- ⚡ Performance optimized with intelligent API usage

## Author

**Sebastian Zabel** - [@SebastianZ84](https://github.com/SebastianZ84)

---

⭐ If you find this integration helpful, please give it a star on GitHub!