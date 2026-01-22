from flask import Blueprint, jsonify, current_app, request, Response
from ...database import get_db
from ...models.gym_mongo import Gym
from ...models.user_mongo import User
import requests
from urllib.parse import quote

api_community = Blueprint('api_community', __name__)

@api_community.route('/proxy-image', methods=['GET'])
def proxy_image():
    """
    Proxy endpoint to fetch external images and serve them
    This solves CORS issues when loading images from external sources
    ---
    tags:
      - Utilities
    parameters:
      - name: url
        in: query
        type: string
        required: true
        description: URL of the image to proxy
    responses:
      200:
        description: Image data
      400:
        description: Missing URL parameter
    """
    try:
        image_url = request.args.get('url')
        if not image_url:
            return jsonify({'status': 'error', 'message': 'URL parameter is required'}), 400
        
        # Add headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://unsplash.com/',
        }
        
        # Fetch the image from the external URL
        response = requests.get(image_url, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # Return the image with appropriate headers
            return Response(
                response.content,
                mimetype=response.headers.get('Content-Type', 'image/jpeg'),
                headers={
                    'Cache-Control': 'public, max-age=86400',  # Cache for 24 hours
                    'Access-Control-Allow-Origin': '*'
                }
            )
        else:
            # Return a simple 1x1 transparent PNG as placeholder
            current_app.logger.warning(f"Failed to fetch image from {image_url}: {response.status_code}, returning placeholder")
            # 1x1 transparent PNG
            placeholder = b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15\\xc4\\x89\\x00\\x00\\x00\\nIDATx\\x9cc\\x00\\x01\\x00\\x00\\x05\\x00\\x01\\r\\n-\\xb4\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82'
            return Response(
                placeholder,
                mimetype='image/png',
                headers={
                    'Cache-Control': 'public, max-age=3600',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
    except Exception as e:
        current_app.logger.error(f"Error in proxy_image: {str(e)}")
        # Return placeholder on error
        placeholder = b'\\x89PNG\\r\\n\\x1a\\n\\x00\\x00\\x00\\rIHDR\\x00\\x00\\x00\\x01\\x00\\x00\\x00\\x01\\x08\\x06\\x00\\x00\\x00\\x1f\\x15\\xc4\\x89\\x00\\x00\\x00\\nIDATx\\x9cc\\x00\\x01\\x00\\x00\\x05\\x00\\x01\\r\\n-\\xb4\\x00\\x00\\x00\\x00IEND\\xaeB`\\x82'
        return Response(
            placeholder,
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',
                'Access-Control-Allow-Origin': '*'
            }
        )

@api_community.route('/gyms', methods=['GET'])
def get_gyms():
    """
    Get all gyms
    ---
    tags:
      - Gyms
    responses:
      200:
        description: List of gyms
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                $ref: '#/definitions/Gym'
      500:
        description: Internal Server Error
    """
    try:
        db = get_db()
        gyms = Gym.find_all(db)
        
        return jsonify({
            'status': 'success',
            'data': [gym.to_dict() for gym in gyms]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_community.get_gyms: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_community.route('/trainers', methods=['GET'])
def get_trainers():
    """
    Get all published trainers
    ---
    tags:
      - Trainers
    responses:
      200:
        description: List of expert trainers
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                $ref: '#/definitions/Trainer'
      500:
        description: Internal Server Error
    """
    try:
        db = get_db()
        trainers = User.find_all_trainers(db, published_only=True)
        return jsonify({
            'status': 'success',
            'data': [trainer.to_dict() for trainer in trainers]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_community.get_trainers: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_community.route('/gyms/<gym_id>', methods=['GET'])
def get_gym(gym_id):
    """
    Get single gym by ID
    ---
    tags:
      - Gyms
    parameters:
      - name: gym_id
        in: path
        type: string
        required: true
        description: ID of the gym
    responses:
      200:
        description: Gym details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              $ref: '#/definitions/Gym'
      404:
        description: Gym not found
    """
    try:
        db = get_db()
        gym = Gym.find_by_id(db, gym_id)
        if not gym:
            return jsonify({'status': 'error', 'message': 'Gym not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': gym.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_community.get_gym: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_community.route('/trainers/<trainer_id>', methods=['GET'])
def get_trainer(trainer_id):
    """
    Get single trainer by ID
    ---
    tags:
      - Trainers
    parameters:
      - name: trainer_id
        in: path
        type: string
        required: true
        description: ID of the trainer
    responses:
      200:
        description: Trainer profile details
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              $ref: '#/definitions/Trainer'
      404:
        description: Trainer not found
    """
    try:
        db = get_db()
        trainer = User.find_by_id(db, trainer_id)
        if not trainer or not trainer.is_trainer:
            return jsonify({'status': 'error', 'message': 'Trainer not found'}), 404
        return jsonify({
            'status': 'success',
            'data': trainer.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error in api_community.get_trainer: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
