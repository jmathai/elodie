# Immich Plugin

This plugin enables albums and favorites to be managed through Immich's UI while ensuring:

* All metadata is **persisted in the photo itself**
* Elodie remains the **canonical organizer**
* File moves do not break album or favorite state

Immich is treated as both an **intent source** (albums, favorites) and a **materialized view target** (albums rebuilt from metadata).

## Requirements

The Immich plugin requires the `requests` library. Install it using:

```bash
pip install requests
```

## Configuration

Add the following section to your `config.ini` file:

```ini
[Plugins]
plugins=Immich

[Plugin Immich]
api_url=https://immich.mydomain.com/api
api_key=your_immich_api_key_here
external_library_path=/path/to/your/photo/library
```

### Configuration Options

* **api_url**: The API URL of your Immich instance (e.g., https://immich.mydomain.com/api)
* **api_key**: Your Immich API key for authentication
* **external_library_path**: The base path for all photos that Elodie will organize into

## Usage

The plugin is automatically triggered when you run:

```bash
./elodie.py batch
```

### First Run (Bootstrap)

On the first run, the plugin will perform a **bootstrap sync** from Elodie to Immich:

* Scans all files in your photo library
* Reads album and rating metadata from photos
* Updates Immich albums and favorites to match
* Marks bootstrap as completed

### Subsequent Runs (Incremental Sync)

After bootstrap, all runs perform **incremental sync** from Immich to Elodie:

* Fetches only assets updated since last sync
* Updates photo metadata for album and favorite changes
* Triggers Elodie file organization if metadata changed
* Updates last sync timestamp

## Metadata Contracts

### Albums

Uses existing Elodie album metadata:
* `XMP-xmpDM:Album` (preferred)
* `XMP:Album` (fallback)

Exactly **one album per photo** is supported.

### Favorites

Maps Immich favorites to XMP ratings:
* Immich `isFavorite = true` → `XMP:Rating = 5`
* Immich `isFavorite = false` → removes `XMP:Rating`

## Album Conflict Resolution

If an asset is moved from Album A to Album B in Immich:
* Album B becomes authoritative
* Photo's album metadata is updated
* Elodie moves the photo to the new album folder

## Error Handling

The plugin logs but does not crash on:
* Missing files
* Assets no longer managed by Elodie
* Album conflicts
* API failures

Summary output includes:
* Metadata updates
* Album moves
* Favorites set and cleared
* Error counts

## Limitations

* Immich asset IDs are not preserved across file moves
* Only supports single album per photo
* No real-time or webhook-based sync
* Requires manual `./elodie.py batch` execution

## API Endpoints Used

The plugin uses the following Immich API endpoints:
* `GET /assets` - Get all assets (with optional updatedSince filter)
* `GET /albums` - Get all albums ([docs](https://api.immich.app/endpoints/albums/getAllAlbums))
* `POST /search/metadata` - Search assets by originalFileName and originalPath ([docs](https://api.immich.app/endpoints/search/searchAssets))
* `POST /albums` - Create new album
* `PUT /albums/{id}/assets` - Add assets to album
* `PUT /assets/{id}` - Update asset (set favorite status)