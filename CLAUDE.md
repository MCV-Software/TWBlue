# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TWBlue is an accessible desktop Mastodon client for Windows, built with Python 3.10 and wxPython. It provides two specialized interfaces optimized for screen reader users to interact with Mastodon instances. The application emphasizes accessibility-first design with keyboard navigation, audio feedback, and screen reader integration.

## Development Commands

### Running from Source
```bash
cd src
python main.py
```

For development from source, VLC dependencies are loaded from `../windows-dependencies/{arch}/` where arch is x86 or x64.

### Installing Dependencies
```bash
# Install all Python dependencies
pip install -r requirements.txt

# Initialize git submodules for Windows dependencies
git submodule init
git submodule update
```

### Building
```bash
# Build binary distribution (from src/ directory)
python setup.py build

# Output will be in src/dist/
```

### Testing
```bash
# Run tests using pytest
pytest

# Tests are located in src/test/
```

### Generating Documentation
```bash
cd doc
python documentation_importer.py
python generator.py
# Copy generated language folders to src/documentation/
# Copy license.txt to src/documentation/
```

### Translation Management
```bash
# Extract translation strings (from doc/ directory)
pybabel extract -o twblue.pot --msgid-bugs-address "manuel@manuelcortez.net" --copyright-holder "MCV software" --input-dirs ../src

# Note: Translations managed via Weblate at https://weblate.mcvsoftware.com
```

## Architecture Overview

TWBlue follows an MVC architecture with distinct separation between data access (Sessions), business logic (Controllers), and presentation (wxUI).

### Core Components

#### 1. Session Layer (`src/sessions/`)
Sessions represent authenticated connections to Mastodon instances. They manage API interactions, OAuth2 authentication, and persistent data storage.

- **Base Session** (`sessions/base.py`): Abstract base class with configuration management, SQLiteDict persistence, and decorators for login/configuration checks
- **Mastodon Session** (`sessions/mastodon/session.py`): Implements Mastodon.py API wrapper, OAuth2 flow, and account credential management
- **Streaming** (`sessions/mastodon/streaming.py`): Real-time event listener that publishes to pub/sub system

Key patterns:
- Sessions use `@_require_login` and `@_require_configuration` decorators
- Configuration files stored as INI format via configobj in `config/{session_id}/session.conf`
- Persistent data (caches, user lists) stored in `config/{session_id}/cache.db` using SQLiteDict
- Each session has its own sound system instance

#### 2. Buffer System (`src/controller/buffers/`)
Buffers are the primary data structures for displaying social media content (timelines, mentions, notifications, conversations, etc.).

**Base Buffer** (`controller/buffers/base/base.py`):
- Links buffer UI (wxPanel) with session (API access) and compose functions (data rendering)
- Handles keyboard events (F5/F6 for volume, Delete for item removal, Return for URLs)
- Manages periodic updates via `start_stream()` function
- Each buffer has a `compose_function` that formats API data for display

**Mastodon Buffers** (`controller/buffers/mastodon/`):
- `base.py`: Mastodon-specific base buffer with timeline pagination
- `users.py`: Home timeline, mentions buffer
- `community.py`: Local/federated timelines
- `notifications.py`: System notifications
- `conversations.py`: Direct message threads
- `search.py`: Search results

Buffer lifecycle:
1. Created by mainController when session initializes
2. Added to view (wx.Treebook)
3. Periodically updated via `start_stream()` or real-time via pub/sub events
4. Destroyed when session ends or buffer removed

#### 3. Controller Layer (`src/controller/`)
Controllers orchestrate application logic and coordinate between sessions, buffers, and UI.

**Main Controller** (`controller/mainController.py`):
- Manages all active buffers and sessions
- Binds keyboard shortcuts to actions
- Handles pub/sub event subscriptions
- Periodically calls `start_stream()` on visible buffers
- Provides buffer search methods: `search_buffer()`, `get_current_buffer()`, `get_best_buffer()`

**Specialized Controllers**:
- `settings.py`: Settings dialog management
- `userAlias.py` / `userList.py`: User management features
- `mastodon/handler.py`: Mastodon-specific operations (filters, etc.)

#### 4. GUI Layer (`src/wxUI/`)
wxPython-based interface with menu-driven navigation and list controls.

- **Main Frame** (`wxUI/view.py`): Primary window with wx.Treebook for buffers, menu system, system tray integration
- **Buffer Panels** (`wxUI/buffers/`): Panel implementations for each buffer type
- **Dialogs** (`wxUI/dialogs/`): Post composition, settings, user profiles, filters

#### 5. Pub/Sub Event System
Decoupled communication using PyPubSub 4.0.3.

Key events:
- `mastodon.status_received`: New post received via streaming
- `mastodon.status_updated`: Post edited
- `mastodon.notification_received`: New notification
- `mastodon.conversation_received`: New DM

Event flow:
1. Streaming listener receives API event
2. Publishes to topic via `pub.sendMessage()`
3. mainController subscribes to topics and routes to appropriate buffer
4. Buffer updates its display

#### 6. Session Manager (`src/sessionmanager/`)
Manages session lifecycle (creation, configuration, activation, deletion).

- `sessionManager.py`: UI for managing multiple accounts
- `manager.py`: Persists session list to global config
- Handles OAuth2 authorization flow for new accounts
- Loads saved sessions on startup

#### 7. Configuration System (`src/config.py`, `src/config_utils.py`)
Hierarchical configuration with defaults and user overrides.

- Global config: `config/app-configuration.conf` (defaults in `src/app-configuration.defaults`)
- Session configs: `config/{session_id}/session.conf` (defaults in `src/mastodon.defaults`)
- Keymaps in `src/keymaps/`
- Sound packs in `src/sounds/`

**Path Management** (`src/paths.py`):
- Portable mode: Config/logs in application directory
- Installed mode: Config/logs in AppData
- Detects installation by presence of `Uninstall.exe`

#### 8. Accessibility Features
Built for screen reader users from the ground up.

- `accessible_output2`: Multi-screen reader support (NVDA, JAWS, SAPI, etc.)
- `sound_lib`: Accessible audio playback with spatial audio
- `platform_utils`: OS-specific accessibility hooks
- `output.py`: Unified interface for speech output
- `sound.py`: Sound system with volume control and sound pack management

#### 9. Keyboard Handling (`src/keyboard_handler/`)
Cross-platform keyboard input with global hotkey support.

- `wx_handler.py`: wxPython integration
- `global_handler.py`: System-wide hotkeys
- Platform implementations: `windows.py`, `osx.py`, `linux.py`
- `keystrokeEditor/`: UI for customizing shortcuts

### Application Initialization Flow

From `src/main.py`:
1. Setup logging to temp directory, then move to permanent location
2. Initialize language handler
3. Load global configuration
4. Setup sound system
5. Setup accessibility output
6. Initialize session manager
7. Load saved sessions or prompt for account creation
8. Create main controller
9. Start main event loop

### Data Flow Patterns

#### Real-time Update Flow
```
Mastodon Streaming API
  → sessions/mastodon/streaming.py (StreamListener)
  → pub.sendMessage("mastodon.status_received", ...)
  → controller/mainController.py (subscriber)
  → buffer.add_new_item()
  → compose_function(item)
  → wxUI update
```

#### User Action Flow
```
Keyboard input
  → wx event handler
  → buffer.get_event()
  → buffer action method (e.g., open_status())
  → session.api_call()
  → UI update or pub/sub event
```

#### Periodic Update Flow
```
RepeatingTimer (every N seconds)
  → mainController calls buffer.start_stream()
  → session.get_timeline_data()
  → buffer.put_items_on_list()
  → compose_function for each item
  → wxUI list control update
```

## Key Design Patterns and Conventions

### Compose Functions
Buffers use compose functions to render API objects as user-readable strings. Located in `sessions/mastodon/compose.py`:

```python
compose_function(item, db, relative_times, show_screen_names=False, session=None)
# Returns a string representation of the item for display
```

### Session Decorators
Sessions use decorators to enforce prerequisites:

```python
@baseSession._require_login
def post_status(self, text):
    # Only executes if self.logged == True
    pass

@baseSession._require_configuration
def get_timeline(self):
    # Only executes if self.settings != None
    pass
```

### Buffer Naming Convention
Buffers have both a `name` (internal identifier) and `account` (associated username):
- `name`: e.g., "home_timeline", "mentions", "notifications"
- `account`: e.g., "user@mastodon.social"
- Buffers are uniquely identified by (name, account) tuple

### Configuration Hierarchy
1. Default values in `src/*.defaults` files
2. User overrides in `config/*.conf` files
3. Runtime modifications via settings dialogs
4. Written back to user config files on change

## Important Caveats

### Platform-Specific Code
- VLC paths must be set via environment variables when running from source (see `main.py`)
- Windows-specific: pywin32, win-inet-pton, winpaths dependencies
- Accessibility output works best on Windows with NVDA/JAWS

### Threading and Event Handling
- API calls often wrapped in `call_threaded()` to avoid blocking UI
- Streaming runs in background thread and publishes to main thread via pub/sub
- wx events must be handled on main thread

### Session Lifecycle
- Sessions must be logged in before buffer creation
- Buffers maintain references to sessions via `self.session`
- Destroying a session should destroy all associated buffers
- Session settings auto-save on write via `settings.write()`

### Buffer Visibility
- Buffers have `invisible` flag for internal/system buffers
- Main controller distinguishes between visible buffers (shown in tree) and invisible buffers (used for data access)
- Empty buffers serve as account placeholders in tree structure

### Logging and Debugging
- Logs written to temp directory on startup, then moved to permanent location
- Binary builds redirect stdout/stderr to `logs/` directory
- Source builds use console output
- Use `logging.getLogger("module.name")` pattern throughout

## Build System Details

### cx_Freeze Configuration (`src/setup.py`)
- Target: Win32GUI (suppresses console window)
- Includes: keymaps, locales, sounds, documentation, icon, config defaults
- Architecture-specific: Loads x86 or x64 dependencies from windows-dependencies submodule
- Special handling for enchant dictionaries, VLC plugins, VC++ redistributables

### NSIS Installer (`scripts/twblue.nsi`)
- Expects binary distribution in `scripts/twblue64/`
- Creates Start Menu shortcuts, Desktop shortcut (optional)
- Registers uninstaller
- Checks for running instances before install/uninstall

### CI/CD (`.github/workflows/release.yml`)
- Triggers on version tags (v20*)
- Builds on Windows-latest with Python 3.10
- Creates both installer (EXE) and portable (ZIP) distributions
- Uploads to GitHub releases

## Mastodon API Integration

### Authentication
OAuth2 flow implemented in `sessions/mastodon/session.py`:
1. Create application credentials for instance
2. Request OAuth authorization URL
3. User authorizes in browser
4. Exchange code for access token
5. Store credentials in session config

### API Client
Uses Mastodon.py 2.1.4 library:
- Instance created with base URL and access token
- Methods: `status_post()`, `timeline()`, `account()`, etc.
- Rate limiting handled by library
- Supports multiple instances simultaneously

### Streaming API
Real-time updates via `sessions/mastodon/streaming.py`:
- Inherits from `Mastodon.StreamListener`
- Connects to user, public, or hashtag streams
- Runs in background thread
- Events published to main thread via pub/sub

## Localization

TWBlue supports 23 languages:
- Translation files in `src/locales/{lang}/LC_MESSAGES/twblue.mo`
- Uses gettext with `_()` function throughout codebase
- Language selection in settings, stored in global config
- Babel for extraction and compilation
- Weblate for translation management
