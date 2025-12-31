# Immich Plugin (experimental)

This plugin enables albums, descriptions, location and favorites to be managed through Immich's UI while ensuring:

* All metadata is **persisted in the photo itself**
* Elodie remains the **canonical organizer**
* File moves do not break album or favorite state

Immich is treated as both an **intent source** (albums, descriptions, location favorites) and a **materialized view target** (albums rebuilt from metadata).

## Requirements

Install the plugin's requirements.

```bash
pip install -r elodie/plugins/immich/requirements.txt
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

### Configuration

* **api_url**: The API URL of your Immich instance (e.g., https://immich.mydomain.com/api)
* **api_key**: Your Immich API key for authentication. [Learn more](https://api.immich.app/authentication).
* **external_library_path**: The full path to your external library. [Learn more](https://docs.immich.app/guides/external-library).

## Usage

The plugin is automatically triggered when you run:

```bash
./elodie.py batch
```

Note: use the `--debug` flag to get verbose logs for troubleshooting.

### First Run (Bootstrap)

On the first run, the plugin will perform a **bootstrap sync** from Elodie to Immich:

* Scans all files in your photo library
* Reads album, description and rating metadata from photos
* Updates Immich albums, descriptions and favorites to match
* Marks bootstrap as completed

### Subsequent Runs (Incremental Sync)

After bootstrap, all runs perform **incremental sync** from Immich to Elodie:

* Fetches only assets updated since last sync
* Updates photo metadata for album and favorite changes
* Triggers Elodie file organization if metadata changed
* Updates last sync timestamp

Some updates result in Elodie renaming and moving files. This is translated by Immich as deleting a file and uploading a new one. In order to handle this gracefully, this plugin will wait until the new file is added to Immich's database and resolve the file move (i.e. adding the new file to albums the old file was in). Of course, it does all of this by using EXIF in the photo itself.

## Metadata Contracts

Metadata changes sync bidirectionally between your photos and Immich.

1. Updating fields through Immich will write them to the photo EXIF.
2. Updating a photo's EXIF will populate Immich.

The general intent of this plugin is that most metadata changes would happen through Immich and this plugin will ensure they get synced to the photo's EXIF.

### Albums

Uses existing Elodie album metadata:
* `XMP-xmpDM:Album` (preferred)
* `XMP:Album` (fallback)

#### Multiple Albums

Since Elodie translates an album to a folder, photos cannot exist in multiple albums.

However, Immich is able to support a photo belonging to multiple albums. And that's a great feature.

Here's how this plugin enables a single photo to be in multiple albums.
1. The XMP album field can contain multiple albums delimited by `;`.
2. If album is part of the folder path it will be named the `;` delimited value. For example, the album in EXIF and and name of the folder might be `Album 1;Album 2`.
3. The EXIF will be used to restore album memberships if the file gets moved.

### Favorites

Maps Immich favorites to XMP ratings:
* Immich `isFavorite = true` → `XMP:Rating = 5`
* Immich `isFavorite = false` → removes `XMP:Rating`

### Description

Description is stored in `XMP:Description` and maps the description field in Immich.

### Location

Location is stored in `XMP:GPSLatitude` and `XMP:GPSLongitude` and maps to the latitude and longitude fields in Immich.

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
* No real-time or webhook-based sync
* Requires scheduled `./elodie.py batch` execution

## API Endpoints Used

The plugin uses the following Immich API endpoints:
* `GET /albums` - Get all albums ([docs](https://api.immich.app/endpoints/albums/getAllAlbums))
* `GET /albums/{id}` - Get album details with assets ([docs](https://api.immich.app/endpoints/albums/getAlbumInfo))
* `POST /albums` - Create new album ([docs](https://api.immich.app/endpoints/albums/createAlbum))
* `PUT /albums/{id}/assets` - Add assets to album ([docs](https://api.immich.app/endpoints/albums/addAssetsToAlbum))
* `POST /search/metadata` - Search assets by metadata ([docs](https://api.immich.app/endpoints/search/searchAssets))
* `GET /assets/{id}` - Get detailed asset information ([docs](https://api.immich.app/endpoints/assets/getAssetInfo))
* `PUT /assets/{id}` - Update asset (favorite status, description, location) ([docs](https://api.immich.app/endpoints/assets/updateAsset))
