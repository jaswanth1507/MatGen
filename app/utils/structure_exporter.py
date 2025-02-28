"""
Utilities for exporting material structures to various formats.
"""

import os
import json
import logging
from pymatgen.io.cif import CifWriter
from pymatgen.io.xyz import XYZ

logger = logging.getLogger(__name__)

def export_structures(materials, output_dir, formats=["cif"]):
    """
    Export material structures to specified formats.
    
    Args:
        materials (list): List of generated materials
        output_dir (str): Output directory
        formats (list): List of formats to export (currently supports "cif" and "xyz")
        
    Returns:
        dict: Dictionary mapping material formulas to file paths
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    exported_files = {}
    
    for i, material in enumerate(materials):
        try:
            # Get structure and metadata
            structure = material['structure']
            formula = material['formula']
            material_id = material.get('material_id', f"gen_{i}")
            
            # Create a safe filename
            safe_name = f"{material_id}_{formula.replace(' ', '_')}"
            
            material_files = {}
            
            # Export as CIF
            if "cif" in formats:
                cif_path = os.path.join(output_dir, f"{safe_name}.cif")
                cif_writer = CifWriter(structure)
                cif_writer.write_file(cif_path)
                material_files['cif'] = cif_path
                logger.info(f"Exported {formula} to CIF: {cif_path}")
            
            # Export as XYZ
            if "xyz" in formats:
                xyz_path = os.path.join(output_dir, f"{safe_name}.xyz")
                xyz_writer = XYZ(structure)
                xyz_writer.write_file(xyz_path)
                material_files['xyz'] = xyz_path
                logger.info(f"Exported {formula} to XYZ: {xyz_path}")
            
            # Save property information in a JSON file
            props_path = os.path.join(output_dir, f"{safe_name}_properties.json")
            with open(props_path, 'w') as f:
                props_data = {
                    'formula': formula,
                    'material_id': material_id,
                    'band_gap': float(material['target_properties'][0]),
                    'formation_energy': float(material['target_properties'][1]),
                    'bulk_modulus': float(material['target_properties'][2])
                }
                json.dump(props_data, f, indent=2)
            
            material_files['properties_json'] = props_path
            
            # Store in results
            exported_files[formula] = material_files
            
        except Exception as e:
            logger.error(f"Error exporting structure for material {i}: {str(e)}")
    
    return exported_files

def structure_to_3d_vis_data(structure):
    """
    Convert a pymatgen Structure to data suitable for 3D visualization.
    
    Args:
        structure (Structure): Pymatgen Structure object
        
    Returns:
        dict: Dictionary with atoms, positions, and lattice information
    """
    # Get atomic symbols and positions
    symbols = [site.species_string for site in structure]
    positions = [site.coords.tolist() for site in structure]
    
    # Get lattice parameters
    lattice = structure.lattice
    a, b, c = lattice.abc
    alpha, beta, gamma = lattice.angles
    
    # Get lattice vectors
    matrix = lattice.matrix.tolist()
    
    return {
        'formula': structure.composition.reduced_formula,
        'atoms': symbols,
        'positions': positions,
        'lattice_parameters': {
            'a': a,
            'b': b,
            'c': c,
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma
        },
        'lattice_vectors': matrix
    }

def create_visualization_data(materials, include_structure_data=False):
    """
    Create visualization data for a list of materials.
    
    Args:
        materials (list): List of generated materials
        include_structure_data (bool): Whether to include full structure data
        
    Returns:
        list: List of materials with visualization data
    """
    vis_data = []
    
    for material in materials:
        # Basic properties
        material_data = {
            'formula': material['formula'],
            'material_id': material.get('material_id', ''),
            'properties': {
                'band_gap': float(material['target_properties'][0]),
                'formation_energy': float(material['target_properties'][1]),
                'bulk_modulus': float(material['target_properties'][2]),
            }
        }
        
        # Add structure data if requested
        if include_structure_data:
            material_data['structure'] = structure_to_3d_vis_data(material['structure'])
        
        vis_data.append(material_data)
    
    return vis_data