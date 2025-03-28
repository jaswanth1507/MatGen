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

# Import from the matgen module we created
from app.matgen import MaterialVAE, StructureRecovery

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
        self.max_materials = 1000
        self.logger = logging.getLogger(__name__)
        
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
    def _validate_material_properties(self, material, constraints, strictness=1.0):
        """
        Validate if a material meets the specified property constraints.

        Args:
            material (dict): Material with properties
            constraints (dict): Property constraints
            strictness (float): 0.0 to 1.0, how strictly to enforce constraints
                               (1.0 = exact, 0.0 = ignore constraints)

        Returns:
            tuple: (meets_constraints, score)
        """
        if strictness <= 0.0:
            return True, 0.0  # If strictness is 0, accept anything

        # Get target property ranges
        target_bg_min = constraints.get('band_gap', {}).get('min', 0.0)
        target_bg_max = constraints.get('band_gap', {}).get('max', 10.0)
        target_fe_min = constraints.get('formation_energy', {}).get('min', -20.0)
        target_fe_max = constraints.get('formation_energy', {}).get('max', 5.0)
        target_bm_min = constraints.get('bulk_modulus', {}).get('min', 1.0)
        target_bm_max = constraints.get('bulk_modulus', {}).get('max', 400.0)

        # Widen ranges based on strictness (1.0 = exact range, 0.0 would be infinite range)
        relaxation_factor = 1.0 + (3.0 * (1.0 - strictness))  # 1.0 at strictness=1.0, 4.0 at strictness=0.0

        # Widen min and max by the relaxation factor
        bg_min = target_bg_min / relaxation_factor if target_bg_min > 0 else target_bg_min * relaxation_factor
        bg_max = target_bg_max * relaxation_factor
        fe_min = target_fe_min * relaxation_factor if target_fe_min < 0 else target_fe_min / relaxation_factor
        fe_max = target_fe_max * relaxation_factor if target_fe_max < 0 else target_fe_max / relaxation_factor
        bm_min = target_bm_min / relaxation_factor
        bm_max = target_bm_max * relaxation_factor

        # Actual properties (use target properties as fallback)
        actual_bg = float(material.get('target_properties', [0, 0, 0])[0])
        actual_fe = float(material.get('target_properties', [0, 0, 0])[1])
        actual_bm = float(material.get('target_properties', [0, 0, 0])[2])

        # Try to get properties from the structure file if available
        if 'band_gap' in material:
            actual_bg = material['band_gap']

        if 'formation_energy_per_atom' in material:
            actual_fe = material['formation_energy_per_atom']

        if 'bulk_modulus' in material:
            actual_bm = material['bulk_modulus']

        # Check if properties are within the relaxed ranges
        meets_bg = bg_min <= actual_bg <= bg_max
        meets_fe = fe_min <= actual_fe <= fe_max
        meets_bm = bm_min <= actual_bm <= bm_max

        # Calculate compliance score (0 to 1, higher is better)
        bg_score = 1.0 - min(1.0, max(0, abs(actual_bg - (target_bg_min + target_bg_max) / 2) / 
                               max(0.01, (target_bg_max - target_bg_min))))
        fe_score = 1.0 - min(1.0, max(0, abs(actual_fe - (target_fe_min + target_fe_max) / 2) / 
                               max(0.01, (target_fe_max - target_fe_min))))
        bm_score = 1.0 - min(1.0, max(0, abs(actual_bm - (target_bm_min + target_bm_max) / 2) / 
                               max(0.01, (target_bm_max - target_bm_min))))

        # Average score
        compliance_score = (bg_score + fe_score + bm_score) / 3.0

        # With strictness=1.0, all conditions must be met
        if strictness >= 1.0:
            meets_constraints = meets_bg and meets_fe and meets_bm
        else:
            # With lower strictness, we give some leeway based on overall compliance score
            meets_constraints = compliance_score >= strictness

        # Log the validation results
        self.logger.debug(f"Material validation: BG={actual_bg:.2f} ({meets_bg}), " +
                         f"FE={actual_fe:.2f} ({meets_fe}), BM={actual_bm:.2f} ({meets_bm}), " +
                         f"Score={compliance_score:.2f}, Meets={meets_constraints}")

        return meets_constraints, compliance_score
    
    def generate_materials(self, constraints, n_samples=5, temperature=1.2, strictness=0.8):
        """
        Generate materials based on constraints.

        Args:
            constraints (dict): Property constraints
            n_samples (int): Number of materials to generate
            temperature (float): Sampling temperature
            strictness (float): 0.0 to 1.0, how strictly to enforce constraints

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
        logger.info(f"Using temperature={temperature:.2f}, strictness={strictness:.2f}")

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

            # Track rejected materials for logging purposes
            rejected_materials = []

            # We might need to generate more candidates to meet our strictness requirements
            max_attempts = max(10, n_samples * 3)  # Allow up to 3x more attempts than requested samples
            attempt = 0

            while len(generated_materials) < n_samples and attempt < max_attempts:
                attempt += 1
                remaining = n_samples - len(generated_materials)

                # Generate for all remaining samples in one batch
                batch_indices = range(min(remaining, n_samples))

                for i in batch_indices:
                    logger.info(f"Attempt {attempt}: Generating material {len(generated_materials)+1}/{n_samples}")
                    logger.info(f"Target properties: Band Gap = {target_props_real[i, 0]:.2f} eV, "
                             f"Formation Energy = {target_props_real[i, 1]:.2f} eV/atom, "
                             f"Bulk Modulus = {target_props_real[i, 2]:.2f} GPa")

                    # Generate multiple features per target for more diversity
                    # Increase number of samples for higher strictness to improve chances of finding matches
                    candidate_samples = max(3, int(5 * strictness))
                    gen_features = vae.generate(target_props_norm[i].reshape(1, -1), 
                                                n_samples=candidate_samples, 
                                                temperature=temperature)

                    # Recover structures with diversity improvement
                    candidates_list = recovery.recover_structures(gen_features, return_multiple=True, diversity_weight=0.7)

                    # Flatten the candidates list for easier selection
                    all_candidates = []
                    for candidate_group in candidates_list:
                        all_candidates.extend(candidate_group)

                    if not all_candidates:
                        logger.warning(f"No candidate structures found for target {i+1}")
                        continue
                    
                    # Filter candidates based on property constraints and sort by compliance score
                    valid_candidates = []
                    for candidate in all_candidates:
                        # Add target properties to the candidate for validation
                        candidate_with_props = candidate.copy()
                        candidate_with_props['target_properties'] = target_props_real[i]

                        # Validate against constraints
                        meets_constraints, score = self._validate_material_properties(
                            candidate_with_props, constraints, strictness)

                        if meets_constraints:
                            # Add score to candidate for sorting
                            candidate['compliance_score'] = score
                            valid_candidates.append(candidate)
                        else:
                            # Track rejected materials
                            formula = candidate['structure'].composition.reduced_formula
                            rejected_materials.append({
                                'formula': formula,
                                'score': score,
                                'material_id': candidate.get('material_id', '')
                            })

                    # Sort by compliance score (higher is better)
                    valid_candidates.sort(key=lambda x: x.get('compliance_score', 0), reverse=True)

                    if valid_candidates:
                        # Among valid candidates, prefer those not used before
                        used_formulas = [m.get('formula', '') for m in generated_materials]

                        selected_candidate = None
                        for candidate in valid_candidates:
                            formula = candidate['structure'].composition.reduced_formula
                            if formula not in used_formulas:
                                selected_candidate = candidate
                                break
                            
                        # If all formulas have been used, select the best one
                        if selected_candidate is None and valid_candidates:
                            selected_candidate = valid_candidates[0]
                            logger.info("Using best candidate despite formula repetition")

                        if selected_candidate:
                            # Store information
                            generated_materials.append({
                                'target_properties': target_props_real[i],
                                'material_id': selected_candidate.get('material_id', f"gen_{len(generated_materials)}"),
                                'structure': selected_candidate['structure'],
                                'formula': selected_candidate['structure'].composition.reduced_formula,
                                'distance': selected_candidate.get('distance', 0),
                                'compliance_score': selected_candidate.get('compliance_score', 0)
                            })

                            logger.info(f"Generated material: {selected_candidate['structure'].composition.reduced_formula} " +
                                       f"(Score: {selected_candidate.get('compliance_score', 0):.2f})")
                    else:
                        logger.warning(f"No valid candidates found for target {i+1} that meet constraints with strictness={strictness:.2f}")
                        # If we're on our last attempt, try with reduced strictness
                        if attempt == max_attempts - 1 and strictness > 0.2:
                            reduced_strictness = max(0.2, strictness * 0.5)
                            logger.info(f"Relaxing strictness to {reduced_strictness:.2f} for final attempt")
                            strictness = reduced_strictness

            # If we couldn't generate enough materials with the given strictness,
            # include the best rejected materials to meet the sample count
            if len(generated_materials) < n_samples and rejected_materials:
                logger.warning(f"Could only generate {len(generated_materials)}/{n_samples} materials that " +
                             f"strictly meet constraints. Adding best alternatives.")

                # Sort rejected materials by score (higher is better)
                rejected_materials.sort(key=lambda x: x.get('score', 0), reverse=True)

                # Add best rejected materials until we reach n_samples
                used_formulas = [m.get('formula', '') for m in generated_materials]

                for rejected in rejected_materials:
                    if rejected['formula'] not in used_formulas and len(generated_materials) < n_samples:
                        # Find the original candidate with this formula
                        for candidate_group in candidates_list:
                            for candidate in candidate_group:
                                if (candidate['structure'].composition.reduced_formula == rejected['formula'] and
                                    candidate.get('material_id', '') == rejected.get('material_id', '')):

                                    generated_materials.append({
                                        'target_properties': target_props_real[len(generated_materials) % len(target_props_real)],
                                        'material_id': candidate.get('material_id', f"gen_{len(generated_materials)}"),
                                        'structure': candidate['structure'],
                                        'formula': candidate['structure'].composition.reduced_formula,
                                        'distance': candidate.get('distance', 0),
                                        'compliance_score': rejected.get('score', 0),
                                        'warning': "Does not fully meet constraints"
                                    })

                                    used_formulas.append(rejected['formula'])
                                    logger.warning(f"Added alternative material: {rejected['formula']} " +
                                                 f"(Score: {rejected.get('score', 0):.2f})")
                                    break
                                
            logger.info(f"Generated {len(generated_materials)}/{n_samples} materials")
            return generated_materials

        except Exception as e:
            logger.error(f"Error generating materials: {str(e)}")
            return []