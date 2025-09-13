# Trello Enhanced - Installation Guide

This is an enhanced version of the Home Assistant Trello integration that adds visual board display and card movement capabilities.

## Installation via HACS (Local Repository)

### Step 1: Add Local Repository to HACS

1. Open Home Assistant
2. Go to **HACS** → **Integrations**
3. Click the **three dots menu** (⋮) in the top right
4. Select **Custom repositories**
5. Add this repository:
   - **Repository**: `file:///path/to/ha-trello-local` (use your actual path)
   - **Category**: `Integration`
6. Click **Add**

### Step 2: Install the Integration

1. In HACS → Integrations, search for "**Trello Enhanced**"
2. Click **Download**
3. Restart Home Assistant

### Step 3: Configure the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Trello" and select it
4. Enter your Trello API credentials:
   - **API Key**: Get from [Trello Power-Up Admin Portal](https://trello.com/power-ups/admin/)
   - **API Token**: Generate from the same portal
5. Select the boards you want to monitor

## What's New in the Enhanced Version

### 🎯 **Visual Board Display**
- Interactive Kanban board view in Home Assistant
- See all your cards and lists in a familiar Trello-style layout

### 🎯 **Drag & Drop Card Movement**  
- Move cards between lists by dragging and dropping
- Real-time updates and synchronization

### 🎯 **Card Creation**
- Add new cards directly from Home Assistant
- Click the "+" button in any list

### 🎯 **Enhanced Data**
- Card details include descriptions and due dates
- Complete card information available in sensor attributes

## Using the Board Display

### Step 1: Ensure Frontend Files are Loaded

If you get "Custom element not found: trello-board" error, manually add frontend resources:

**Configuration.yaml:**
```yaml
frontend:
  extra_module_url:
    - /local/community/trello_enhanced/trello-board-card.js
    - /local/community/trello_enhanced/trello-board-card-editor.js
```

**Or manually copy files:**
1. Copy `www/trello-board-card.js` to `/config/www/trello-board-card.js`
2. Copy `www/trello-board-card-editor.js` to `/config/www/trello-board-card-editor.js`
3. Add to configuration.yaml:
```yaml
frontend:
  extra_module_url:
    - /local/trello-board-card.js
    - /local/trello-board-card-editor.js
```

**Restart Home Assistant** after adding frontend resources.

### Step 2: Add to Dashboard

Add this card to your Lovelace dashboard:

```yaml
type: custom:trello-board
board_id: "your_board_id_here"
```

### Finding Your Board ID

1. Go to **Developer Tools** → **States**
2. Find any `sensor.trello_*` entity
3. Look for the `board_id` attribute
4. Copy this value for your dashboard configuration

## Services Available

### Move Card Between Lists
```yaml
service: trello.move_card
data:
  card_id: "card_id_here"
  target_list_id: "target_list_id_here"
```

### Create New Card
```yaml
service: trello.create_card  
data:
  list_id: "list_id_here"
  name: "Card Name"
  description: "Optional description"
```

## Features

✅ **Interactive Board View**: Visual Kanban board display  
✅ **Drag & Drop**: Move cards between lists  
✅ **Card Creation**: Add new cards with + button  
✅ **Real-time Sync**: Changes update immediately  
✅ **Theme Support**: Matches your HA theme  
✅ **Card Details**: View descriptions and due dates  
✅ **Service Integration**: Use in automations and scripts  

## Troubleshooting

### Board Not Loading
- Check that your board ID is correct in the card configuration
- Verify the Trello integration is configured and working
- Check Home Assistant logs for any API errors

### Cards Not Moving
- Ensure your Trello API token has write permissions
- Check that both source and target lists exist
- Verify internet connectivity to Trello API

### Frontend Not Loading
- Clear your browser cache
- Check that JavaScript files are installed in `/config/www/community/trello/`
- Restart Home Assistant after installation

## Support

For issues with this enhanced version, check:
1. Home Assistant logs for integration errors
2. Browser console for frontend errors  
3. Verify all files are installed correctly

Original integration by [@scottg489](https://github.com/ScottG489/ha-trello)  
Enhanced with board display and card movement capabilities.