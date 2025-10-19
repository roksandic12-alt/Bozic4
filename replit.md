# Overview

This is a Discord bot game called "Vilenjak" (Elf) that creates a Christmas-themed village simulation. Players become elves in Santa's village, complete tasks, earn snowflakes (currency), upgrade their workshops and homes, and develop crafting skills. The bot uses Discord.py for interaction and JSON-based file storage for persistence.

**Status**: Fully functional and running. Bot is online and ready to use.

**Last Updated**: October 19, 2025

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Discord.py with Commands Extension**: Uses the `commands.Bot` class for structured command handling with prefix-based commands (`!command`)
- **Intents Configuration**: Enables message content and member intents for reading messages and accessing user data
- **Async/Await Pattern**: Built on asyncio for handling Discord's event-driven architecture
- **Command Registration**: Module-level functions decorated with `@bot.command()` for proper Discord.py integration

## Data Model
- **Player Entity (Vilenjak Class)**: Represents each player with attributes including:
  - Identity: user_id, custom name
  - Progression: level, experience points
  - Economy: snowflakes currency
  - Assets: house type, workshop type
  - Skills: crafting abilities (toy making, decorating, wrapping, baking)
  - Inventory: decorations and tools collections

## Data Persistence
- **JSON File Storage**: Player data serialized to/from dictionaries for file-based persistence in `vilenjaci.json`
- **Global State**: Bot maintains runtime dictionary `vilenjaci_data` of active players
- **Serialization Methods**: `to_dict()` and `from_dict()` handle conversion between object and storage format
- **Load on Start**: `on_ready()` event loads all player data when bot connects

## Command Structure
- **Registration** (`!postani_vilenjak`): Initializes new player with 100 snowflakes and basic resources
- **Status** (`!mojstatus`): Displays player level, XP, snowflakes, house, workshop, and skills
- **Shop** (`!shop [category]`): Browse items in categories: alat (tools), dekoracije (decorations), nadogradnje (upgrades)
- **Purchase** (`!kupi [item]`): Buy items from shop using snowflakes
- **Tasks** (`!zadaci`): View available jobs with rewards and requirements
- **Work** (`!radi [task_id]`): Complete tasks to earn snowflakes, XP, and skill improvements
- **Leaderboard** (`!leaderboard`): Display top 10 players by level and XP

## UI Patterns
- **Discord Embeds**: Rich formatted messages with fields, colors, and emojis for visual presentation
- **Emoji Integration**: Thematic Christmas/winter emojis for enhanced user experience

## Game Mechanics Design
- **Level Progression**: Experience-based leveling system (100 XP per level implied)
- **Skill System**: Multi-dimensional skill tree with crafting specializations
- **Economy**: Snowflake currency for transactions and upgrades
- **Asset Upgrades**: Tiered house and workshop improvements

# External Dependencies

## Core Dependencies
- **discord.py**: Official Discord API wrapper for Python - handles all bot-to-Discord communication, command parsing, and event handling
- **Python Standard Library**:
  - `json`: Data serialization/deserialization for player persistence
  - `random`: Likely for task rewards, loot drops, or random events
  - `asyncio`: Asynchronous I/O for concurrent Discord operations
  - `os`: File system operations for data storage

## Discord Platform
- **Discord Bot Token**: Required environment variable for authentication
- **Discord Gateway**: WebSocket connection for real-time events
- **Discord Permissions**: Needs message read, message send, and embed links permissions

## Storage
- **Local File System**: JSON files stored locally (no external database)
- **No Cloud Services**: Currently uses file-based persistence without external storage backends