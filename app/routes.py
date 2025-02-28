"""
API routes for the Material Generator API.
"""

import os
import json
import time
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.models.nlp_processor import NLPProcessor
from app.models.material_generator import MaterialGenerator
from app.utils.structure_exporter import export_structures

# Create Blueprint
api_bp = Blueprint('api', __name__)

# Create model instances (loaded lazily)
nlp_processor = None
material_generator = None

def get_nlp_processor():
    """Get or initialize NLP processor"""
    global nlp_processor
    if nlp_processor is None:
        current_app.logger.info("Initializing NLP processor")
        nlp_processor = NLPProcessor(
            model_name=current_app.config['NLP_MODEL_NAME'],
            use_gpu=current_app.config['USE_GPU']
        )
    return nlp_processor

def get_material_generator():
    """Get or initialize material generator"""
    global material_generator
    if material_generator is None:
        current_app.logger.info("Initializing material generator")
        material_generator = MaterialGenerator(
            model_dir=current_app.config['MODEL_DIR'],
            use_gpu=current_app.config['USE_GPU']
        )
    return material_generator

# Initialize models at startup if configured
@api_bp.before_app_request
def initialize_models():
    if current_app.config['LOAD_MODELS_AT_STARTUP']:
        current_app.logger.info("Pre-loading models at startup")
        get_nlp_processor()
        get_material_generator()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Material Generator API is running'
    })

@api_bp.route('/generate', methods=['POST'])
def generate_materials():
    """Generate materials based on a natural language query"""
    try:
        # Get request data
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing query parameter'
            }), 400
        
        query = data['query']
        n_samples = int(data.get('n_samples', current_app.config['DEFAULT_SAMPLES']))
        temperature = float(data.get('temperature', current_app.config['DEFAULT_TEMPERATURE']))
        
        current_app.logger.info(f"Processing query: {query}")
        current_app.logger.info(f"Parameters: n_samples={n_samples}, temperature={temperature}")
        
        # Start timer
        start_time = time.time()
        
        # Step 1: Process query with NLP model
        processor = get_nlp_processor()
        constraints = processor.process_query(query)
        
        if not constraints:
            return jsonify({
                'success': False,
                'error': 'Failed to extract constraints from query'
            }), 400
        
        # Log extracted constraints
        current_app.logger.info(f"Extracted constraints: {constraints}")
        
        # Step 2: Generate materials
        generator = get_material_generator()
        materials = generator.generate_materials(
            constraints, 
            n_samples=n_samples, 
            temperature=temperature
        )
        
        if not materials:
            return jsonify({
                'success': False,
                'error': 'Failed to generate materials'
            }), 500
        
        # Step 3: Export structures
        output_dir = current_app.config['OUTPUT_FOLDER']
        exported_files = export_structures(materials, output_dir)
        
        # Step 4: Prepare response data
        response_materials = []
        
        for material in materials:
            formula = material['formula']
            props = material['target_properties']
            
            # Get file paths
            cif_path = None
            if formula in exported_files and 'cif' in exported_files[formula]:
                cif_path = os.path.basename(exported_files[formula]['cif'])
            
            # Create material response object
            material_data = {
                'formula': formula,
                'band_gap': float(props[0]),
                'formation_energy': float(props[1]),
                'bulk_modulus': float(props[2]),
                'material_id': material.get('material_id', ''),
                'cif_url': f"/api/structures/{cif_path}" if cif_path else None
            }
            
            response_materials.append(material_data)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Return success response
        return jsonify({
            'success': True,
            'query': query,
            'constraints': constraints,
            'materials': response_materials,
            'process_time': process_time
        })
    
    except Exception as e:
        current_app.logger.exception(f"Error generating materials: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/structures/<filename>', methods=['GET'])
def get_structure(filename):
    """Get a specific structure file"""
    try:
        # Get the output folder from config
        output_folder = current_app.config['OUTPUT_FOLDER']
        
        # Get absolute path to ensure proper resolution
        abs_output_folder = os.path.abspath(output_folder)
        abs_file_path = os.path.join(abs_output_folder, filename)
        
        # Enhanced logging
        current_app.logger.info(f"Structure file requested: {filename}")
        current_app.logger.info(f"Config OUTPUT_FOLDER: {output_folder}")
        current_app.logger.info(f"Absolute output folder: {abs_output_folder}")
        current_app.logger.info(f"Absolute file path: {abs_file_path}")
        
        # Check if the output directory exists
        if not os.path.exists(abs_output_folder):
            current_app.logger.error(f"Output directory doesn't exist: {abs_output_folder}")
            return jsonify({
                'success': False,
                'error': f"Output directory doesn't exist"
            }), 500
        
        # List all files in the directory for debugging
        dir_files = os.listdir(abs_output_folder)
        current_app.logger.info(f"Files in directory ({len(dir_files)}): {', '.join(dir_files[:10])}{'...' if len(dir_files) > 10 else ''}")
        
        # Check if the file exists
        if not os.path.exists(abs_file_path):
            current_app.logger.error(f"File not found: {abs_file_path}")
            
            # Look for similar filenames to help debug
            similar_files = [f for f in dir_files if filename.split('_')[0] in f or filename.split('_')[-1] in f]
            if similar_files:
                current_app.logger.info(f"Similar files found: {similar_files}")
            
            return jsonify({
                'success': False,
                'error': f"File not found: {filename}"
            }), 404
        
        # If the file exists, serve it
        current_app.logger.info(f"File found! Serving: {abs_file_path}")
        return send_from_directory(
            abs_output_folder, 
            filename, 
            as_attachment=True,
            mimetype='chemical/x-cif'
        )
    except Exception as e:
        current_app.logger.exception(f"Error retrieving structure file: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Error retrieving file: {filename} - {str(e)}"
        }), 500