"""
Material generator for creating materials based on property constraints.
"""

import os
import json
import time
import pickle
import logging
import numpy as np
from pymatgen.core import Structure

logger = logging.getLogger(__name__)

class MaterialGenerator:
    def __init__(self, model_dir, use_gpu=True):
        """
        Initialize the material generator.
        
        Args:
            model_dir (str): Directory containing the MEGNet+VAE model
            use_gpu (bool): Whether to use GPU
        """
        self.model_dir = model_dir
        self.use_gpu = use_gpu
        self.model_components = None
        
        # Load the model if the directory exists
        if os.path.exists(model_dir):
            self._load_model()
        else:
            logger.error(f"Model directory not found: {model_dir}")
    
    def _load_model(self):
        """Load the MEGNet+VAE model"""
        if self.model_components is not None:
            return
            
        logger.info(f"Loading MEGNet+VAE model from: {self.model_dir}")
        start_time = time.time()
        
        try:
            # Load VAE configuration
            with open(os.path.join(self.model_dir, "vae_config.json"), 'r') as f:
                vae_config = json.load(f)
            
            # Create the VAE model
            from matgen import MaterialVAE
            
            vae = MaterialVAE(
                input_dim=vae_config['input_dim'],
                property_dim=vae_config['property_dim'],
                latent_dim=vae_config['latent_dim'],
                hidden_dims=vae_config['hidden_dims']
            )
            
            # Load weights
            vae_weights_path = os.path.join(self.model_dir, "vae.weights.h5")
            vae.load(vae_weights_path)
            
            # Load scalers
            with open(os.path.join(self.model_dir, "feature_scaler.pkl"), 'rb') as f:
                feature_scaler = pickle.load(f)
            
            with open(os.path.join(self.model_dir, "property_scaler.pkl"), 'rb') as f:
                property_scaler = pickle.load(f)
            
            # Load materials data
            filtered_materials = None
            if os.path.exists(os.path.join(self.model_dir, "materials_data.pkl")):
                with open(os.path.join(self.model_dir, "materials_data.pkl"), 'rb') as f:
                    materials_data = pickle.load(f)
                
                # Convert dictionaries back to Structure objects
                filtered_materials = []
                for mat in materials_data:
                    structure = Structure.from_dict(mat['structure'])
                    mat_dict = {
                        'material_id': mat['material_id'],
                        'structure': structure,
                        'band_gap': mat['band_gap'],
                        'formation_energy_per_atom': mat['formation_energy_per_atom'],
                        'energy_above_hull': mat.get('energy_above_hull', 0)
                    }
                    filtered_materials.append(mat_dict)
            
            # Load feature matrix and create recovery module
            recovery = None
            if os.path.exists(os.path.join(self.model_dir, "feature_matrix.npy")):
                feature_matrix = np.load(os.path.join(self.model_dir, "feature_matrix.npy"))
                
                if filtered_materials is not None:
                    from matgen import StructureRecovery
                    
                    recovery = StructureRecovery(feature_matrix, filtered_materials, feature_scaler)
            
            # Store model components
            self.model_components = {
                'vae': vae,
                'feature_scaler': feature_scaler,
                'property_scaler': property_scaler,
                'filtered_materials': filtered_materials,
                'recovery': recovery
            }
            
            load_time = time.time() - start_time
            logger.info(f"MEGNet+VAE model loaded successfully in {load_time:.2f} seconds")
        
        except Exception as e:
            logger.error(f"Error loading MEGNet+VAE model: {str(e)}")
            raise
    
    def generate_materials(self, constraints, n_samples=5, temperature=1.2):
        """
        Generate materials based on constraints.
        
        Args:
            constraints (dict): Property constraints
            n_samples (int): Number of materials to generate
            temperature (float): Sampling temperature
            
        Returns:
            list: Generated materials
        """
        # Ensure model is loaded
        if self.model_components is None:
            self._load_model()
            
            if self.model_components is None:
                logger.error("Failed to load model components")
                return []
        
        logger.info(f"Generating {n_samples} materials with constraints: {constraints}")
        
        try:
            vae = self.model_components['vae']
            property_scaler = self.model_components['property_scaler']
            recovery = self.model_components['recovery']
            
            # Create target properties within the constraints
            target_props_real = np.zeros((n_samples, 3))
            
            # Add some variance to the targets for better diversity
            for i in range(n_samples):
                target_props_real[i, 0] = np.random.uniform(
                    constraints['band_gap']['min'],
                    constraints['band_gap']['max']
                )
                target_props_real[i, 1] = np.random.uniform(
                    constraints['formation_energy']['min'],
                    constraints['formation_energy']['max']
                )
                target_props_real[i, 2] = np.random.uniform(
                    constraints['bulk_modulus']['min'],
                    constraints['bulk_modulus']['max']
                )
            
            # Scale properties to normalized space
            target_props_norm = property_scaler.transform(target_props_real)
            
            # Generate materials for each target with increased temperature for diversity
            generated_materials = []
            
            for i, target_norm in enumerate(target_props_norm):
                logger.info(f"Generating material {i+1}/{n_samples}")
                logger.info(f"Target properties: Band Gap = {target_props_real[i, 0]:.2f} eV, "
                           f"Formation Energy = {target_props_real[i, 1]:.2f} eV/atom, "
                           f"Bulk Modulus = {target_props_real[i, 2]:.2f} GPa")
                
                # Generate multiple features per target for more diversity
                gen_features = vae.generate(target_norm.reshape(1, -1), n_samples=3, temperature=temperature)
                
                # Recover structures with diversity improvement
                candidates_list = recovery.recover_structures(gen_features, return_multiple=True, diversity_weight=0.7)
                
                # Flatten the candidates list for easier selection
                all_candidates = []
                for candidate_group in candidates_list:
                    all_candidates.extend(candidate_group)
                
                # Select the best candidate that hasn't been used before, or the most diverse one
                selected_candidate = None
                used_formulas = [m.get('formula', '') for m in generated_materials]
                
                for candidate in all_candidates:
                    formula = candidate['structure'].composition.reduced_formula
                    if formula not in used_formulas:
                        selected_candidate = candidate
                        break
                
                # If all formulas have been used, select the first one
                if selected_candidate is None and all_candidates:
                    selected_candidate = all_candidates[0]
                
                if selected_candidate:
                    # Store information
                    generated_materials.append({
                        'target_properties': target_props_real[i],
                        'material_id': selected_candidate.get('material_id', f"gen_{i}"),
                        'structure': selected_candidate['structure'],
                        'formula': selected_candidate['structure'].composition.reduced_formula,
                        'distance': selected_candidate.get('distance', 0)
                    })
                    
                    logger.info(f"Generated material: {selected_candidate['structure'].composition.reduced_formula}")
                else:
                    logger.warning(f"Failed to generate material {i+1}")
            
            return generated_materials
        
        except Exception as e:
            logger.error(f"Error generating materials: {str(e)}")
            return []