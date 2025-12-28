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
from datetime import datetime
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

    def update_asset(self, asset_id, is_favorite=None):
        """Update an asset (e.g., set favorite status)"""
        url = f"{self.api_url}/assets/{asset_id}"
        payload = {}
        
        if is_favorite is not None:
            payload['isFavorite'] = is_favorite
        
        try:
            response = self.session.put(url, json=payload)
            response.raise_for_status()
            return response.json()
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

    def batch(self):
        """Main batch processing method - handles sync operations"""
        if not self.client:
            self.display('Immich plugin not configured properly. Check api_url and api_key in config.')
            return (False, 0)
            
        if not self.external_library_path:
            self.display('Immich plugin missing external_library_path configuration.')
            return (False, 0)
            
        try:
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
            # Get all albums that exist in Immich for mapping
            immich_albums = self.client.get_all_albums()
            album_name_to_id = {album['albumName']: album['id'] for album in immich_albums}
            
            # Iterate through all files in the external library path
            for file_path in self.filesystem.get_all_files(self.external_library_path):
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
                    
                    # Handle album sync - parse semicolon-separated album names
                    album_string = metadata.get('album')
                    if album_string:
                        # Split on semicolon to get multiple albums
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
                    
                    count += 1
                    
                except Exception as e:
                    self.log(f'Error processing {file_path}: {str(e)}')
                    self.log(f'Exception type: {type(e).__name__}')
                    errors += 1
                    continue
                    
        except Exception as e:
            self.display(f'Bootstrap sync failed: {str(e)}')
            return (False, count)
        
        self.display(f'Bootstrap completed: {count} files processed, {errors} errors')
        return (True, count)

    def _sync_immich_to_elodie(self):
        """Incremental sync: Immich → Elodie"""
        count = 0
        errors = 0
        self.safe_to_update_assets = set()  # Track assets safe to update state for
        
        try:
            # Get current album membership from Immich
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
            
            # Bootstrap moved files that haven't been processed yet
            self._bootstrap_moved_files()
            
            # Process changed assets
            for asset_id in changed_assets:
                try:
                    asset_info = asset_info_lookup.get(asset_id)
                    
                    # Store/update asset info in immich_states for reverse lookup
                    if asset_info:
                        immich_states[asset_id] = {
                            'originalPath': asset_info.get('originalPath'),
                            'originalFileName': asset_info.get('originalFileName'),
                            'albums': current_membership.get(asset_id, []),
                            'isFavorite': current_favorites.get(asset_id, False)
                        }
                    
                    if not asset_info:
                        self.log(f'Could not find asset info for {asset_id}')
                        continue
                    
                    self.log(f'Processing asset: {asset_id} - {asset_info.get("originalFileName", "unknown")}')
                    
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
                    
                    if current_albums != previous_albums:
                        if current_albums:
                            # Join multiple albums with semicolon separator
                            album_string = ';'.join(sorted(current_albums))
                            media.set_album(album_string)
                            self.log(f'Updated albums for {file_path} to: {sorted(current_albums)}')
                        updated = True
                    
                    # Apply favorite changes  
                    current_favorite = current_favorites.get(asset_id, False)
                    previous_favorite = previous_favorites.get(asset_id, False)
                    
                    if current_favorite != previous_favorite:
                        if current_favorite:
                            media.set_rating(5)
                        else:
                            media.set_rating('')
                        self.log(f'Updated favorite for {file_path} to: {current_favorite}')
                        updated = True
                        
                    # If metadata was updated, reprocess the file to handle potential moves
                    if updated:
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
                
                # Restore album memberships from EXIF
                album_string = metadata.get('album')
                if album_string:
                    albums = [name.strip() for name in album_string.split(';') if name.strip()]
                    self.log(f'Restoring albums {albums} for asset {new_asset_id}')
                    
                    # Ensure albums exist and add asset to them
                    all_albums = self.client.get_all_albums()
                    album_name_to_id = {album['albumName']: album['id'] for album in all_albums}
                    
                    for album_name in albums:
                        if album_name not in album_name_to_id:
                            # Create album if it doesn't exist
                            new_album = self.client.create_album(album_name)
                            album_name_to_id[album_name] = new_album['id']
                            
                        # Add asset to album
                        self.client.add_assets_to_album(album_name_to_id[album_name], [new_asset_id])
                
                # Restore favorite status from EXIF  
                rating = metadata.get('rating')
                if rating == 5:
                    self.log(f'Restoring favorite status for asset {new_asset_id}')
                    self.client.update_asset(new_asset_id, is_favorite=True)
                
                # Update the file move record with new asset ID
                move_info['new_asset_id'] = new_asset_id
                updated_moves[old_asset_id] = move_info
                self.log(f'Successfully bootstrapped moved file: {old_asset_id} -> {new_asset_id}')
                
            except Exception as e:
                self.log(f'Error bootstrapping moved file {new_path}: {str(e)}')
                updated_moves[old_asset_id] = move_info
                
        # Save updated file moves
        self.db.set('file_moves', updated_moves)