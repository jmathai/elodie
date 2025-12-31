"""
Immich plugin for albums and favorites sync.
Enables albums and favorites to be managed through Immich's UI while ensuring:
- All metadata is persisted in the photo itself  
- Elodie remains the canonical organizer
- File moves do not break album or favorite state

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

import json
import os
import requests
import time
from datetime import datetime, timedelta
from os.path import basename, dirname, isfile

from elodie.media.photo import Photo
from elodie.media.video import Video  
from elodie.media.base import Base, get_all_subclasses
from elodie.plugins.plugins import PluginBase
from elodie.filesystem import FileSystem

class ImmichApiClient(object):
    """Client for interacting with Immich API"""
    
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })


    def get_all_albums(self):
        """Get all albums from Immich"""
        url = f"{self.api_url}/albums"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get albums: {e}")
    
    def get_album_by_id(self, album_id):
        """Get a specific album by ID with its assets"""
        url = f"{self.api_url}/albums/{album_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get album {album_id}: {e}")
            
    def search_assets_by_metadata(self, original_file_name=None, original_path=None, is_favorite=None):
        """Search for assets by original filename and path"""
        url = f"{self.api_url}/search/metadata"
        payload = {}
        
        if original_file_name:
            payload['originalFileName'] = original_file_name
        if original_path:
            payload['originalPath'] = original_path
        if is_favorite is not None:
            payload['isFavorite'] = is_favorite
            
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to search assets: {e} (Status: {response.status_code if 'response' in locals() else 'unknown'})")

    def create_album(self, album_name, description=""):
        """Create a new album in Immich"""
        url = f"{self.api_url}/albums"
        payload = {
            'albumName': album_name,
            'description': description
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to create album {album_name}: {e}")

    def add_assets_to_album(self, album_id, asset_ids):
        """Add assets to an album"""
        url = f"{self.api_url}/albums/{album_id}/assets"
        payload = {
            'ids': asset_ids
        }
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to add assets to album: {e}")

    def get_asset_by_id(self, asset_id):
        """Get detailed asset information by ID"""
        url = f"{self.api_url}/assets/{asset_id}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get asset {asset_id}: {e}")

    def search_assets_updated_since(self, timestamp):
        """Search for assets updated since a specific timestamp"""
        url = f"{self.api_url}/search/metadata"
        payload = {
            'updatedAfter': timestamp
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to search assets: {e}")

    def update_asset(self, asset_id, is_favorite=None, description=None, file_created_at=None, latitude=None, longitude=None):
        """Update an asset (favorite status, description, date/time, location)"""
        url = f"{self.api_url}/assets/{asset_id}"  # Fixed: should be /assets/{id}
        payload = {}
        
        if is_favorite is not None:
            payload['isFavorite'] = is_favorite
        if description is not None:
            payload['description'] = description
        if file_created_at is not None:
            payload['fileCreatedAt'] = file_created_at
        if latitude is not None:
            payload['latitude'] = latitude
        if longitude is not None:
            payload['longitude'] = longitude
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            # PUT returns 204 with empty body
            return True
        except requests.RequestException as e:
            raise Exception(f"Failed to update asset: {e}")


class Immich(PluginBase):
    """A class to execute Immich plugin actions.
       
       Requires a config file with the following configurations set:
       api_url:
            The API URL of your Immich instance (e.g., https://immich.mydomain.com/api)
       api_key:
            Your Immich API key for authentication
       external_library_path:
            The base path for all photos that Elodie will organize into
    """

    __name__ = 'Immich'

    def __init__(self):
        super(Immich, self).__init__()
        
        # Get configuration from config.ini
        self.api_url = None
        if 'api_url' in self.config_for_plugin:
            self.api_url = self.config_for_plugin['api_url']
        
        self.api_key = None
        if 'api_key' in self.config_for_plugin:
            self.api_key = self.config_for_plugin['api_key']
            
        self.external_library_path = None
        if 'external_library_path' in self.config_for_plugin:
            self.external_library_path = self.config_for_plugin['external_library_path']
            
        # Initialize API client if we have required config
        self.client = None
        if self.api_url and self.api_key:
            self.client = ImmichApiClient(self.api_url, self.api_key)
        
        self.filesystem = FileSystem()

    def after(self, file_path, destination_folder, final_file_path, metadata):
        """Called after a file is processed"""
        # File move tracking is now handled in batch() where we have asset IDs
        pass

    def prune_immich_states(self):
        """Prune plugin state to reflect what's in immich database"""
        try:
            # Get all current assets from Immich
            search_results = self.client.search_assets_updated_since('2020-01-01T00:00:00.000Z')
            assets_data = search_results.get('assets', {})
            all_assets = assets_data.get('items', [])
            current_asset_ids = {asset['id'] for asset in all_assets}
            
            self.log(f"Found {len(all_assets)} current assets in Immich")
            self.log(f"Current asset IDs: {list(current_asset_ids)}")
            
            # Check which tracked asset IDs are stale (no longer exist in Immich)
            immich_states = self.db.get('immich_states') or {}
            tracked_asset_ids = set(immich_states.keys())
            stale_asset_ids = tracked_asset_ids - current_asset_ids
            
            if stale_asset_ids:
                self.log(f"Found {len(stale_asset_ids)} stale asset IDs: {list(stale_asset_ids)}")
                
                # Remove stale entries from immich_states
                for stale_id in stale_asset_ids:
                    if stale_id in immich_states:
                        del immich_states[stale_id]
                        self.log(f"Removed stale asset ID {stale_id} from immich_states")
                
                # Save cleaned immich_states back to database
                self.db.set('immich_states', immich_states)
                
                # Clean up expired file move records
                self._cleanup_expired_file_moves()
                self.log("State reconciliation completed - removed stale entries")
            else:
                self.log("No stale asset IDs found - state is current")
                
        except Exception as e:
            self.log(f"Error during state reconciliation: {e}")

    def batch(self):
        """Main batch processing method - handles sync operations"""
        if not self.client:
            self.display('Immich plugin not configured properly. Check api_url and api_key in config.')
            return (False, 0)
            
        if not self.external_library_path:
            self.display('Immich plugin missing external_library_path configuration.')
            return (False, 0)
            
        try:
            # First prune our state to match current Immich assets
            self.prune_immich_states()
            
            # Check if bootstrap has been completed
            bootstrap_completed = self.db.get('bootstrap_completed')
            
            if not bootstrap_completed:
                self.display('Running initial bootstrap sync from Elodie to Immich...')
                result = self._bootstrap_elodie_to_immich()
                if result[0]:  # If successful
                    self.db.set('bootstrap_completed', True)
                    self.display('Bootstrap completed successfully')
                return result
            else:
                self.display('Running incremental sync from Immich to Elodie...')
                return self._sync_immich_to_elodie()
                
        except Exception as e:
            self.display(f'Immich sync failed: {str(e)}')
            return (False, 0)

    def before(self, file_path, destination_folder):
        """Called before a file is processed"""
        # We don't need to do anything before individual file processing
        pass

    def _bootstrap_elodie_to_immich(self):
        """Bootstrap sync: Elodie → Immich (one-time setup)"""
        count = 0
        errors = 0
        
        try:
            # Get or initialize processed files list for resume capability
            processed_files = set(self.db.get('bootstrap_processed_files') or [])
            total_processed = len(processed_files)
            
            if total_processed > 0:
                self.log(f'Resuming bootstrap - {total_processed} files already processed')
            
            # Get all albums that exist in Immich for mapping
            immich_albums = self.client.get_all_albums()
            album_name_to_id = {album['albumName']: album['id'] for album in immich_albums}
            
            # Iterate through all files in the external library path
            all_files = list(self.filesystem.get_all_files(self.external_library_path))
            total_files = len(all_files)
            self.log(f'Bootstrap processing {total_files} total files ({total_processed} already completed)')
            
            for file_path in all_files:
                # Skip files already processed
                if file_path in processed_files:
                    continue
                try:
                    # Get media object and metadata
                    media = Base.get_class_by_file(file_path, get_all_subclasses())
                    if not media:
                        continue
                        
                    metadata = media.get_metadata()
                    if not metadata:
                        continue
                    
                    # Find corresponding Immich asset using both filename and path for uniqueness
                    original_filename = basename(file_path)
                    original_path = file_path
                    search_results = self.client.search_assets_by_metadata(
                        original_file_name=original_filename,
                        original_path=original_path
                    )
                    
                    # Get assets from the correct part of the response structure
                    assets_data = search_results.get('assets', {})
                    assets = assets_data.get('items', [])
                    if not assets:
                        self.log(f'No Immich asset found for {file_path} (filename: {original_filename})')
                        continue
                        
                    asset = assets[0]  # Take first match
                    asset_id = asset['id']
                    
                    # Use refactored sync method
                    if self._sync_single_file_to_immich(file_path, asset_id, album_name_to_id):
                        count += 1
                        
                        # Track this file as processed and save immediately for resume capability
                        processed_files.add(file_path)
                        self.db.set('bootstrap_processed_files', list(processed_files))
                        
                        # Log progress every 100 files
                        if len(processed_files) % 100 == 0:
                            progress_pct = (len(processed_files) / total_files) * 100
                            self.log(f'Bootstrap progress: {len(processed_files)}/{total_files} files ({progress_pct:.1f}%)')
                    
                except Exception as e:
                    self.log(f'Error processing {file_path}: {str(e)}')
                    self.log(f'Exception type: {type(e).__name__}')
                    errors += 1
                    continue
                    
        except Exception as e:
            self.display(f'Bootstrap sync failed: {str(e)}')
            return (False, count)
        
        # Log completion and clean up progress tracking
        final_progress_pct = (len(processed_files) / total_files) * 100 if total_files > 0 else 0
        self.display(f'Bootstrap completed: {count} files processed, {errors} errors')
        self.log(f'Final progress: {len(processed_files)}/{total_files} files ({final_progress_pct:.1f}%)')
        
        # Clean up bootstrap progress tracking since we're done
        self.db.set('bootstrap_processed_files', None)
        
        return (True, count)

    def _sync_immich_to_elodie(self):
        """Incremental sync: Immich → Elodie"""
        count = 0
        errors = 0
        self.safe_to_update_assets = set()  # Track assets safe to update state for
        
        try:
            # Get assets updated since last sync
            last_sync_timestamp = self.db.get('last_sync_timestamp')
            if last_sync_timestamp:
                search_results = self.client.search_assets_updated_since(last_sync_timestamp)
                updated_assets = search_results.get('assets', {}).get('items', [])
            else:
                # First run - get all assets (fallback to current behavior)
                search_results = self.client.search_assets_by_metadata()
                updated_assets = search_results.get('assets', {}).get('items', [])
            
            self.log(f'Found {len(updated_assets)} assets updated since last sync')
            
            # Get detailed info for each updated asset
            detailed_assets = {}
            for asset in updated_assets:
                asset_id = asset['id']
                try:
                    detailed_asset = self.client.get_asset_by_id(asset_id)
                    detailed_assets[asset_id] = detailed_asset
                except Exception as e:
                    self.log(f'Failed to get details for asset {asset_id}: {e}')
            
            # Get current album membership from Immich (for state comparison)
            all_albums = self.client.get_all_albums()
            current_membership = {}  # asset_id -> [album_names]
            
            # Fetch each album individually to get its assets
            for album_summary in all_albums:
                album_id = album_summary.get('id')
                album_name = album_summary.get('albumName')
                
                # Get full album data with assets
                album_detail = self.client.get_album_by_id(album_id)
                album_assets = album_detail.get('assets', [])
                
                self.log(f'Album "{album_name}" has {len(album_assets)} assets')
                
                for album_asset in album_assets:
                    asset_id = album_asset.get('id')
                    if asset_id:
                        if asset_id not in current_membership:
                            current_membership[asset_id] = []
                        current_membership[asset_id].append(album_name)
            
            # Get current favorite state from Immich using search
            current_favorites = {}  # asset_id -> is_favorite
            
            # Get favorited assets - all others are implicitly not favorited
            favorite_search = self.client.search_assets_by_metadata(is_favorite=True)
            favorite_assets = favorite_search.get('assets', {}).get('items', [])
            self.log(f'Found {len(favorite_assets)} favorite assets')
            for asset in favorite_assets:
                asset_id = asset.get('id')
                if asset_id:
                    current_favorites[asset_id] = True
            
            # Store current Immich states for reverse lookup (we'll populate this as we process assets)
            immich_states = self.db.get('immich_states') or {}
            
            # Get previous state from plugin database
            previous_membership = self.db.get('album_membership') or {}
            previous_favorites = self.db.get('favorite_state') or {}
            
            self.log(f'Current membership has {len(current_membership)} assets, previous had {len(previous_membership)}')
            
            # Find assets with changed album membership or favorite status
            all_asset_ids = set(current_membership.keys()) | set(previous_membership.keys()) | set(current_favorites.keys()) | set(previous_favorites.keys())
            changed_assets = []
            
            for asset_id in all_asset_ids:
                current_albums = set(current_membership.get(asset_id, []))
                previous_albums = set(previous_membership.get(asset_id, []))
                current_favorite = current_favorites.get(asset_id, False)
                previous_favorite = previous_favorites.get(asset_id, False)
                
                album_changed = current_albums != previous_albums
                favorite_changed = current_favorite != previous_favorite
                
                if album_changed or favorite_changed:
                    changed_assets.append(asset_id)
                    if album_changed:
                        self.log(f'Album change detected for asset {asset_id}: {sorted(previous_albums)} -> {sorted(current_albums)}')
                    if favorite_changed:
                        self.log(f'Favorite change detected for asset {asset_id}: {previous_favorite} -> {current_favorite}')
            
            # Build asset info lookup for changed assets
            asset_info_lookup = {}
            
            # Get asset info from albums
            for album_summary in all_albums:
                album_id = album_summary.get('id')
                album_detail = self.client.get_album_by_id(album_id)
                for album_asset in album_detail.get('assets', []):
                    asset_id = album_asset.get('id')
                    if asset_id:
                        asset_info_lookup[asset_id] = album_asset
            
            # Also get asset info from favorite assets (for assets not in any album)
            for asset in favorite_assets:
                asset_id = asset.get('id')
                if asset_id and asset_id not in asset_info_lookup:
                    asset_info_lookup[asset_id] = asset
            
            self.log(f'Asset info lookup has {len(asset_info_lookup)} assets')
            
            # Debug: Show current asset IDs and paths in Immich
            current_assets_debug = []
            for album_summary in all_albums:
                album_detail = self.client.get_album_by_id(album_summary.get('id'))
                for asset in album_detail.get('assets', []):
                    current_assets_debug.append({
                        'id': asset.get('id'),
                        'path': asset.get('originalPath'),
                        'filename': asset.get('originalFileName')
                    })
            self.log(f'Current assets in Immich: {current_assets_debug}')
            
            # Bootstrap moved files that haven't been processed yet
            self._bootstrap_moved_files()
            
            # Add assets with album/favorite changes to the processing list
            for asset_id in changed_assets:
                if asset_id not in detailed_assets and asset_id in asset_info_lookup:
                    # Get detailed asset info for this changed asset
                    try:
                        detailed_asset = self.client.get_asset_by_id(asset_id)
                        detailed_assets[asset_id] = detailed_asset
                    except Exception as e:
                        self.log(f'Could not get detailed info for changed asset {asset_id}: {e}')
            
            # Process all assets (both updated from search and changed from membership)
            for asset_id, detailed_asset in detailed_assets.items():
                try:
                    # Use detailed asset info
                    asset_info = detailed_asset
                    exif_info = detailed_asset.get('exifInfo', {})
                    
                    # Store/update asset info in immich_states for reverse lookup
                    immich_states[asset_id] = {
                        'originalPath': asset_info.get('originalPath'),
                        'originalFileName': asset_info.get('originalFileName'),
                        'albums': current_membership.get(asset_id, []),
                        'isFavorite': asset_info.get('isFavorite', False),
                        'description': exif_info.get('description'),
                        'latitude': exif_info.get('latitude'),
                        'longitude': exif_info.get('longitude')
                    }
                    
                    if not asset_info:
                        self.log(f'Could not find asset info for {asset_id}')
                        continue
                    
                    self.log(f'Processing asset: {asset_id} - {asset_info.get("originalFileName", "unknown")}')
                    self.log(f'Available asset fields: {list(asset_info.keys())}')
                    
                    # Find the corresponding file in Elodie
                    file_path = self._find_file_for_asset(asset_info)
                    if not file_path:
                        self.log(f'Could not find file for asset {asset_id}')
                        self.log(f'Asset originalPath: {asset_info.get("originalPath")}')
                        self.log(f'Asset originalFileName: {asset_info.get("originalFileName")}')
                        continue
                        
                    # Get media object
                    media = Base.get_class_by_file(file_path, get_all_subclasses())
                    if not media:
                        continue
                        
                    updated = False
                    
                    # Apply album changes
                    current_albums = set(current_membership.get(asset_id, []))
                    previous_albums = set(previous_membership.get(asset_id, []))
                    
                    album_changed = False
                    if current_albums != previous_albums:
                        if current_albums:
                            # Join multiple albums with semicolon separator
                            album_string = ';'.join(sorted(current_albums))
                            media.set_album(album_string)
                            self.log(f'Updated albums for {file_path} to: {sorted(current_albums)}')
                        updated = True
                        album_changed = True
                    
                    # Apply favorite changes  
                    # TODO: Consider using exifInfo.rating instead of isFavorite to streamline API calls
                    current_favorite = current_favorites.get(asset_id, False)
                    previous_favorite = previous_favorites.get(asset_id, False)
                    
                    if current_favorite != previous_favorite:
                        if current_favorite:
                            media.set_rating(5)
                        else:
                            media.set_rating('')
                        self.log(f'Updated favorite for {file_path} to: {current_favorite}')
                        updated = True
                    
                    # Apply description changes
                    current_description = exif_info.get('description')
                    previous_immich_states = self.db.get('immich_states') or {}
                    previous_description = previous_immich_states.get(asset_id, {}).get('description')
                    
                    if current_description != previous_description:
                        media.set_description(current_description or '')
                        self.log(f'Updated description for {file_path} to: {current_description}')
                        updated = True
                    
                    # Note: Date/time synchronization is disabled to avoid timezone issues
                    # that cause endless file rename cycles
                    
                    # Apply location changes
                    current_lat = exif_info.get('latitude')
                    current_lng = exif_info.get('longitude') 
                    previous_lat = previous_immich_states.get(asset_id, {}).get('latitude')
                    previous_lng = previous_immich_states.get(asset_id, {}).get('longitude')
                    
                    location_changed = False
                    if (current_lat != previous_lat or current_lng != previous_lng) and current_lat is not None and current_lng is not None:
                        media.set_location(current_lat, current_lng)
                        self.log(f'Updated location for {file_path} to: {current_lat}, {current_lng}')
                        updated = True
                        location_changed = True
                        
                    # Only reprocess file for changes that affect file path (album or location changes)
                    # Description and favorite changes don't require file moves
                    if album_changed or location_changed:
                        updated_media = Base.get_class_by_file(file_path, get_all_subclasses())
                        new_path = self.filesystem.process_file(
                            file_path, 
                            self.external_library_path, 
                            updated_media,
                            move=True
                        )
                        if new_path and new_path != file_path:
                            # File was moved - record the asset ID translation
                            file_moves = self.db.get('file_moves') or {}
                            file_moves[asset_id] = {
                                'old_path': file_path,
                                'new_path': new_path,
                                'new_asset_id': None,  # Will be populated when Immich processes the move
                                'timestamp': datetime.utcnow().isoformat() + 'Z'
                            }
                            self.db.set('file_moves', file_moves)
                            self.display(f'Recorded file move: asset {asset_id} {file_path} -> {new_path}')
                            
                            # Clean up empty directories after moving files
                            import os
                            old_directory = os.path.dirname(file_path)
                            self.filesystem.delete_directory_if_empty(old_directory)
                            # Also try parent directory in case it's also empty
                            self.filesystem.delete_directory_if_empty(os.path.dirname(old_directory))
                        else:
                            # No file move needed - changes were applied successfully
                            self.log(f'Changes applied successfully to {file_path}')
                            
                            # Update our stored state immediately since changes were successful
                            if asset_id in immich_states:
                                # Update album membership
                                current_membership[asset_id] = immich_states[asset_id]['albums']
                                
                                # Update favorites
                                is_fav = immich_states[asset_id]['isFavorite']
                                if is_fav:
                                    current_favorites[asset_id] = True
                                else:
                                    current_favorites.pop(asset_id, None)
                            
                        count += 1
                        
                except Exception as e:
                    self.log(f'Error processing asset {asset_id}: {str(e)}')
                    errors += 1
                    continue
            
            # Save updated immich states
            self.db.set('immich_states', immich_states)
            
            # Simple state management: store current state after successful changes
            # (current_membership and current_favorites have been updated above for successful changes)
            self.db.set('album_membership', current_membership)
            self.db.set('favorite_state', current_favorites)
                    
            # Update last sync timestamp
            self.db.set('last_sync_timestamp', datetime.utcnow().isoformat() + 'Z')
            
        except Exception as e:
            self.display(f'Incremental sync failed: {str(e)}')
            return (False, count)
            
        self.display(f'Incremental sync completed: {count} files updated, {errors} errors')
        return (True, count)

    def _find_asset_id_for_path(self, file_path):
        """Find the asset ID for a given file path from stored Immich state"""
        immich_states = self.db.get('immich_states') or {}
        for asset_id, asset_info in immich_states.items():
            if asset_info.get('originalPath') == file_path:
                return asset_id
        return None
    
    def _find_file_for_asset(self, asset):
        """Find the local file path for an Immich asset using translation layer"""
        asset_id = asset['id']
        original_path = asset.get('originalPath')
        
        # First check if this asset was moved and we have a translation
        file_moves = self.db.get('file_moves') or {}
        if asset_id in file_moves:
            move_info = file_moves[asset_id]
            new_path = move_info['new_path']
            if new_path and isfile(new_path):
                return new_path
                
        # If no move recorded, try the original path from Immich
        if original_path and isfile(original_path):
            return original_path
                    
        return None

    def _bootstrap_moved_files(self):
        """Bootstrap album/favorite state for files that were moved but not yet processed by Immich"""
        file_moves = self.db.get('file_moves') or {}
        updated_moves = {}
        
        for old_asset_id, move_info in file_moves.items():
            # Skip if already bootstrapped (has new_asset_id)
            if move_info.get('new_asset_id'):
                updated_moves[old_asset_id] = move_info
                continue
                
            new_path = move_info['new_path']
            self.log(f'Attempting to bootstrap moved file: {new_path}')
            
            try:
                # Search for asset at the new path
                search_results = self.client.search_assets_by_metadata(
                    original_file_name=basename(new_path),
                    original_path=new_path
                )
                
                assets = search_results.get('assets', {}).get('items', [])
                if not assets:
                    self.log(f'No asset found for moved file {new_path}')
                    self.log(f'  - Searched by filename: {basename(new_path)}')
                    self.log(f'  - Searched by path: {new_path}')
                    self.log(f'  - Old asset ID was: {old_asset_id}')
                    updated_moves[old_asset_id] = move_info
                    continue
                    
                asset = assets[0]
                new_asset_id = asset['id']
                self.log(f'Found new asset ID {new_asset_id} for moved file {new_path}')
                
                # Read EXIF metadata from the file
                media = Base.get_class_by_file(new_path, get_all_subclasses())
                if not media:
                    self.log(f'Could not create media object for {new_path}')
                    updated_moves[old_asset_id] = move_info
                    continue
                    
                metadata = media.get_metadata()
                if not metadata:
                    self.log(f'Could not get metadata for {new_path}')
                    updated_moves[old_asset_id] = move_info
                    continue
                
                # Sync Elodie metadata to Immich for this moved file
                all_albums = self.client.get_all_albums()
                album_name_to_id = {album['albumName']: album['id'] for album in all_albums}
                self._sync_single_file_to_immich(new_path, new_asset_id, album_name_to_id)
                
                # Update the file move record with new asset ID
                move_info['new_asset_id'] = new_asset_id
                updated_moves[old_asset_id] = move_info
                self.log(f'Successfully bootstrapped moved file: {old_asset_id} -> {new_asset_id}')
                
            except Exception as e:
                self.log(f'Error bootstrapping moved file {new_path}: {str(e)}')
                updated_moves[old_asset_id] = move_info
                
        # Save updated file moves
        self.db.set('file_moves', updated_moves)

    def _restore_album_membership_after_move(self, old_asset_id, new_asset_id, file_path, metadata):
        """Restore album memberships after a file move to match EXIF data"""
        try:
            # Get album names from EXIF metadata
            album_string = metadata.get('album')
            if not album_string:
                self.log(f'No album data in EXIF for {file_path}')
                return
                
            exif_albums = set(name.strip() for name in album_string.split(';') if name.strip())
            self.log(f'Restoring albums from EXIF for {file_path}: {sorted(exif_albums)}')
            
            # Get all albums and create mapping
            all_albums = self.client.get_all_albums()
            album_name_to_id = {album['albumName']: album['id'] for album in all_albums}
            
            # Restore all EXIF albums to Immich
            for album_name in exif_albums:
                try:
                    # Create album if it doesn't exist
                    if album_name not in album_name_to_id:
                        self.log(f'Creating missing album: {album_name}')
                        new_album = self.client.create_album(album_name)
                        album_name_to_id[album_name] = new_album['id']
                        
                    # Add asset to album
                    album_id = album_name_to_id[album_name]
                    self.log(f'Adding asset {new_asset_id} to album {album_name}')
                    self.client.add_assets_to_album(album_id, [new_asset_id])
                    
                except Exception as e:
                    self.log(f'Error restoring album {album_name} for asset {new_asset_id}: {e}')
            
            # Update tracking with the restored albums
            album_membership = self.db.get('album_membership') or {}
            album_membership[new_asset_id] = list(exif_albums)
            
            # Remove old asset ID from tracking
            if old_asset_id in album_membership:
                del album_membership[old_asset_id]
                
            self.db.set('album_membership', album_membership)
            self.log(f'Updated album membership tracking for asset {new_asset_id}: {sorted(exif_albums)}')
            
        except Exception as e:
            self.log(f'Error in _restore_album_membership_after_move: {e}')

    def _sync_single_file_to_immich(self, file_path, asset_id, album_name_to_id):
        """Sync a single file's metadata from Elodie to Immich"""
        try:
            # Get media object and metadata
            media = Base.get_class_by_file(file_path, get_all_subclasses())
            if not media:
                return False
                
            metadata = media.get_metadata()
            if not metadata:
                return False
            
            # Handle album sync
            album_string = metadata.get('album')
            if album_string:
                albums = [name.strip() for name in album_string.split(';') if name.strip()]
                
                for album in albums:
                    # Ensure album exists in Immich
                    if album not in album_name_to_id:
                        new_album = self.client.create_album(album)
                        album_name_to_id[album] = new_album['id']
                        
                    # Add asset to album
                    self.client.add_assets_to_album(album_name_to_id[album], [asset_id])
                
            # Handle favorite sync
            rating = metadata.get('rating')
            is_favorite = rating == 5 if rating else False
            self.client.update_asset(asset_id, is_favorite=is_favorite)
            
            return True
            
        except Exception as e:
            self.log(f'Error syncing {file_path}: {str(e)}')
            return False

    def _cleanup_expired_file_moves(self):
        """Remove file move records older than 14 days"""
        try:
            file_moves = self.db.get('file_moves') or {}
            moves_to_remove = []
            cutoff_time = datetime.utcnow() - timedelta(days=14)
            
            for move_key, move_data in file_moves.items():
                move_timestamp_str = move_data.get('timestamp')
                if move_timestamp_str:
                    try:
                        # Parse ISO format timestamp
                        move_timestamp = datetime.fromisoformat(move_timestamp_str.replace('Z', '+00:00'))
                        if move_timestamp.replace(tzinfo=None) < cutoff_time:
                            moves_to_remove.append(move_key)
                    except (ValueError, AttributeError) as e:
                        self.log(f"Invalid timestamp in move record {move_key}: {move_timestamp_str}")
            
            if moves_to_remove:
                for move_key in moves_to_remove:
                    del file_moves[move_key]
                    self.log(f"Removed expired file move entry {move_key} (older than 14 days)")
                
                self.db.set('file_moves', file_moves)
                self.log(f"Cleaned up {len(moves_to_remove)} expired file move records")
            
        except Exception as e:
            self.log(f'Error cleaning up expired file moves: {e}')