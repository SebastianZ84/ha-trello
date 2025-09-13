# Trello Board Display Enhancement

This enhancement adds visual board display and card movement capabilities to the Home Assistant Trello integration.

## Features Added

### 1. Enhanced Data Model
- **Card Details**: Sensors now include full card information (name, description, due date)
- **Card Lists**: Each list contains the actual cards, not just counts

### 2. Services for Card Management
- **move_card**: Move cards between lists with drag-and-drop support
- **create_card**: Create new cards directly from Home Assistant

### 3. Custom Lovelace Card
- **Visual Board**: Display Trello boards as interactive Kanban boards
- **Drag & Drop**: Move cards between lists visually
- **Card Creation**: Add new cards using the "+" button

## Installation

1. **Backend**: The enhanced Python integration is automatically loaded
2. **Frontend**: Copy the JavaScript files to your `www` folder:
   ```
   /config/www/community/ha-trello/
   ├── trello-board-card.js
   └── trello-board-card-editor.js
   ```

## Usage

### Services

#### Move Card
```yaml
service: trello.move_card
data:
  card_id: "card_id_here"
  target_list_id: "target_list_id_here"
```

#### Create Card
```yaml
service: trello.create_card
data:
  list_id: "list_id_here"
  name: "Card Name"
  description: "Optional description"
```

### Lovelace Card

Add to your dashboard:

```yaml
type: custom:trello-board
board_id: "your_board_id_here"
```

To find your board ID, check the attributes of any Trello sensor entity.

## Features

- **Interactive Board**: Visual representation of your Trello board
- **Drag & Drop**: Click and drag cards between lists
- **Real-time Updates**: Changes sync automatically 
- **Card Creation**: Click "+" button to add new cards
- **Responsive Design**: Adapts to Home Assistant themes

## Getting Board IDs

1. Go to Developer Tools > States
2. Find any `sensor.trello_*` entity
3. Look for the `board_id` attribute
4. Use this value in your Lovelace card configuration

## Troubleshooting

- Ensure your Trello API credentials have write permissions
- Check Home Assistant logs for any API errors
- Verify the board ID is correct in your card configuration
- Make sure JavaScript files are in the correct `www` folder location