# app_sonic_fingerprint.py
from flask import Blueprint, jsonify, request, render_template
import logging

from tasks.sonic_fingerprint_manager import generate_sonic_fingerprint
from tasks.mediaserver import resolve_jellyfin_user # Import the new resolver function
from app import get_score_data_by_ids
from config import MEDIASERVER_TYPE, JELLYFIN_USER_ID, JELLYFIN_TOKEN, NAVIDROME_USER, NAVIDROME_PASSWORD # Import configs

logger = logging.getLogger(__name__)

# Create a blueprint for the new feature
sonic_fingerprint_bp = Blueprint('sonic_fingerprint_bp', __name__, template_folder='../templates')

@sonic_fingerprint_bp.route('/sonic_fingerprint', methods=['GET'])
def sonic_fingerprint_page():
    """
    Serves the frontend page for the Sonic Fingerprint feature.
    ---
    tags:
      - UI
    responses:
      200:
        description: HTML content of the Sonic Fingerprint page.
        content:
          text/html:
            schema:
              type: string
    """
    try:
        # The default user info will now be fetched by an API call from the frontend
        return render_template('sonic_fingerprint.html', mediaserver_type=MEDIASERVER_TYPE)
    except Exception as e:
         logger.error(f"Error rendering sonic_fingerprint.html: {e}", exc_info=True)
         return "Sonic Fingerprint page not implemented yet. Use the API at /api/sonic_fingerprint/generate"

@sonic_fingerprint_bp.route('/api/config/defaults', methods=['GET'])
def get_media_server_defaults():
    """
    Provides default credentials from the server configuration based on the media server type.
    This is intended for trusted network environments to pre-populate frontend forms.
    ---
    tags:
      - Configuration
    responses:
      200:
        description: A JSON object with default credentials for the configured media server.
        content:
          application/json:
            schema:
              type: object
    """
    # MODIFIED: Removed the security credentials from the response.
    # We only return the user ID/username to pre-fill forms, but not the tokens/passwords.
    if MEDIASERVER_TYPE == 'jellyfin':
        return jsonify({
            "default_user_id": JELLYFIN_USER_ID,
        })
    elif MEDIASERVER_TYPE == 'navidrome':
        return jsonify({
            "default_user": NAVIDROME_USER,
        })
    return jsonify({})


@sonic_fingerprint_bp.route('/api/sonic_fingerprint/generate', methods=['GET'])
def generate_sonic_fingerprint_endpoint():
    """
    Generates a sonic fingerprint based on a user's listening habits.
    ---
    tags:
      - Sonic Fingerprint
    parameters:
      - name: n
        in: query
        type: integer
        required: false
        description: The number of results to return. Overrides the server default.
      - name: jellyfin_user_identifier
        in: query
        type: string
        required: true
        description: The Jellyfin Username or User ID. Required if media server is Jellyfin.
      - name: jellyfin_token
        in: query
        type: string
        required: false
        description: The Jellyfin API Token (optional, defaults to server configuration).
      - name: navidrome_user
        in: query
        type: string
        required: true
        description: The Navidrome username. Required if media server is Navidrome.
      - name: navidrome_password
        in: query
        type: string
        required: false
        description: The Navidrome password (optional, defaults to server configuration).
    responses:
      200:
        description: A list of recommended tracks based on the sonic fingerprint.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  item_id:
                    type: string
                  title:
                    type: string
                  author:
                    type: string
                  distance:
                    type: number
      400:
        description: Bad Request - Missing necessary credentials for the configured media server.
      500:
        description: Server error during generation.
    """
    try:
        num_results = request.args.get('n', type=int)
        
        user_creds = {}
        if MEDIASERVER_TYPE == 'jellyfin':
            user_identifier = request.args.get('jellyfin_user_identifier')
            if not user_identifier:
                return jsonify({"error": "Jellyfin User Identifier is required."}), 400

            # MODIFIED: Get token from request args, if not provided, fall back to config
            token = request.args.get('jellyfin_token') or JELLYFIN_TOKEN
            
            if not token:
                return jsonify({"error": "Jellyfin API Token is required. Please set it in the server configuration."}), 400

            # --- Resolve username to User ID ---
            logger.info(f"Resolving Jellyfin user identifier: '{user_identifier}'")
            resolved_user_id = resolve_jellyfin_user(user_identifier, token)
            if not resolved_user_id:
                return jsonify({"error": f"Could not resolve Jellyfin user '{user_identifier}'."}), 400
            
            logger.info(f"Resolved Jellyfin user ID: '{resolved_user_id}'")
            user_creds['user_id'] = resolved_user_id
            user_creds['token'] = token

        elif MEDIASERVER_TYPE == 'navidrome':
            # MODIFIED: Get user and password from request args, but fall back to config
            user_creds['user'] = request.args.get('navidrome_user') or NAVIDROME_USER
            user_creds['password'] = request.args.get('navidrome_password') or NAVIDROME_PASSWORD
            if not user_creds['user'] or not user_creds['password']:
                return jsonify({"error": "Navidrome username and password are required. Please set them in the server configuration."}), 400
        
        fingerprint_results = generate_sonic_fingerprint(
            num_neighbors=num_results,
            user_creds=user_creds
        )

        if not fingerprint_results:
            return jsonify([])

        result_ids = [r['item_id'] for r in fingerprint_results]
        details_list = get_score_data_by_ids(result_ids)
        
        details_map = {d['item_id']: d for d in details_list}
        distance_map = {r['item_id']: r['distance'] for r in fingerprint_results}

        final_results = []
        for res_id in result_ids:
            if res_id in details_map:
                track_info = details_map[res_id]
                final_results.append({
                    "item_id": track_info['item_id'],
                    "title": track_info['title'],
                    "author": track_info['author'],
                    "distance": distance_map[res_id]
                })

        return jsonify(final_results)
    except Exception as e:
        logger.error(f"Error in sonic_fingerprint endpoint: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while generating the sonic fingerprint."}), 500
