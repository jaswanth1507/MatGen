"""
NLP processor for extracting material property constraints from natural language queries.
"""

import re
import json
import time
import logging
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)

class NLPProcessor:
    def __init__(self, model_name="microsoft/phi-3-mini-4k-instruct", use_gpu=True, load_in_4bit=True, trust_remote_code=True):
        """
        Initialize the NLP processor.
        
        Args:
            model_name (str): Name of the model to load
            use_gpu (bool): Whether to use GPU if available
            load_in_4bit (bool): Whether to load in 4-bit quantization
        """
        self.model_name = model_name
        self.use_gpu = use_gpu
        self.load_in_4bit = load_in_4bit
        self.model = None
        self.tokenizer = None
        
        # Load the model if not lazy loading
        self._load_model()
        
    def _load_model(self):
        """Load the NLP model"""
        if self.model is not None:
            return
            
        logger.info(f"Loading NLP model: {self.model_name}")
        start_time = time.time()
        
        # Check GPU availability
        if self.use_gpu and torch.cuda.is_available():
            device_map = "auto"
            logger.info(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device_map = "cpu"
            logger.info("Using CPU for NLP model")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map=device_map,
                load_in_4bit=self.load_in_4bit,
                trust_remote_code=True
            )
            
            load_time = time.time() - start_time
            logger.info(f"NLP model loaded successfully in {load_time:.2f} seconds")
        except Exception as e:
            logger.error(f"Error loading NLP model: {e}")
            raise
    
    def process_query(self, query):
        """
        Process a natural language query to extract material property constraints.
        
        Args:
            query (str): Natural language query about desired material properties
            
        Returns:
            dict: Dictionary of property constraints
        """
        logger.info(f"Processing query: {query}")
        
        # Ensure model is loaded
        self._load_model()
        
        prompt = f"""
        You are a materials science expert. Convert the following material science query into a structured constraints dictionary.
        
        Query: {query}
        
        Output the result as a Python dictionary with the format:
        constraints = {{
            'property_name': {{'min': value, 'max': value}},
            'property_name': {{'min': value, 'max': value}},
            ...
        }}
        
        Guidelines:
        1. Only include properties that are explicitly mentioned or strongly implied in the query.
        2. Use realistic value ranges for common material properties:
           - band_gap: 0-10 eV
           - formation_energy: -20 to 5 eV/atom
           - bulk_modulus: 1-400 GPa
        3. Focus on these three key properties that our model supports:
           - band_gap
           - formation_energy
           - bulk_modulus
        
        The output should ONLY contain the Python dictionary, nothing else.
        """
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate response with controlled sampling
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=512,
            temperature=0.1,
            top_p=0.9,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        logger.debug(f"Raw NLP response: {response}")
        
        # Try to extract constraints using a direct approach first
        constraints = self._extract_constraints_from_response(response)
        
        # If extraction fails, try a simpler rule-based approach
        if not constraints:
            constraints = self._rule_based_constraints_extraction(query)
        
        # Apply the prepare_for_megnet_vae function to the extracted constraints
        return self._prepare_for_megnet_vae(constraints)

    def _extract_constraints_from_response(self, response):
        """Extract constraints dictionary from model response"""
        try:
            # Try different patterns to extract the dictionary
            dict_match = re.search(r'constraints\s*=\s*({[^{}]*(?:{[^{}]*}[^{}]*)*})', response, re.DOTALL)
            if not dict_match:
                dict_match = re.search(r'({[^{}]*(?:{[^{}]*}[^{}]*)*})', response, re.DOTALL)
            
            if dict_match:
                dict_str = dict_match.group(1)
                
                # Clean up the dictionary string for JSON parsing
                dict_str = dict_str.replace("'", '"')  # Replace single quotes with double quotes
                dict_str = re.sub(r'(\w+):', r'"\1":', dict_str)  # Add quotes around property names
                dict_str = dict_str.replace("None", "null")
                dict_str = dict_str.replace("True", "true")
                dict_str = dict_str.replace("False", "false")
                dict_str = re.sub(r',\s*}', '}', dict_str)  # Remove trailing commas
                
                # Parse JSON
                try:
                    return json.loads(dict_str)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                    logger.error(f"Problem string: {dict_str}")
                    return {}
            
            return {}
        except Exception as e:
            logger.error(f"Error extracting constraints: {str(e)}")
            return {}

    def _rule_based_constraints_extraction(self, query):
        """Use rules to extract constraints from query when NLP fails"""
        query_lower = query.lower()
        constraints = {}
        
        # Extract band gap constraints
        if "band gap" in query_lower or "bandgap" in query_lower:
            min_val, max_val = 0.5, 2.5  # Default values
            
            # Look for ranges like "1.5 to 2.0 eV" or "between 1.5 and 2.0 eV"
            range_match = re.search(r'(\d+\.?\d*)\s*(?:to|and|\-)\s*(\d+\.?\d*)\s*(?:eV)', query_lower)
            if range_match:
                min_val = float(range_match.group(1))
                max_val = float(range_match.group(2))
            
            # Look for "at least X eV" or "greater than X eV"
            min_match = re.search(r'(?:at least|greater than|more than|above|>\s*|≥\s*)(\d+\.?\d*)\s*(?:eV)', query_lower)
            if min_match:
                min_val = float(min_match.group(1))
            
            # Look for "at most X eV" or "less than X eV"
            max_match = re.search(r'(?:at most|less than|below|<\s*|≤\s*)(\d+\.?\d*)\s*(?:eV)', query_lower)
            if max_match:
                max_val = float(max_match.group(1))
            
            # Look for "exactly X eV"
            exact_match = re.search(r'(?:exactly|precisely|=\s*)(\d+\.?\d*)\s*(?:eV)', query_lower)
            if exact_match:
                exact_val = float(exact_match.group(1))
                min_val = exact_val
                max_val = exact_val
            
            constraints['band_gap'] = {'min': min_val, 'max': max_val}
        
        # Extract formation energy constraints (similar pattern)
        if "formation energy" in query_lower or "formation" in query_lower:
            # Apply similar extraction patterns for formation energy
            min_val, max_val = -2.0, -0.1  # Default values
            
            # Implementation similar to band gap pattern matching
            # ...
            
            constraints['formation_energy'] = {'min': min_val, 'max': max_val}
        
        # Extract bulk modulus constraints (similar pattern)
        if "bulk modulus" in query_lower or "modulus" in query_lower or "stiffness" in query_lower:
            # Apply similar extraction patterns for bulk modulus
            min_val, max_val = 50, 200  # Default values
            
            # Implementation similar to band gap pattern matching
            # ...
            
            constraints['bulk_modulus'] = {'min': min_val, 'max': max_val}
        
        return constraints

    def _prepare_for_megnet_vae(self, constraints):
        """
        Filter and prepare constraints for the MEGNet+VAE model.
        
        Args:
            constraints (dict): Raw constraints from NLP
            
        Returns:
            dict: Constraints formatted for MEGNet+VAE
        """
        # Default property ranges
        megnet_constraints = {
            'band_gap': constraints.get('band_gap', {'min': 0.5, 'max': 2.5}),
            'formation_energy': constraints.get('formation_energy', {'min': -2.0, 'max': -0.1}),
            'bulk_modulus': constraints.get('bulk_modulus', {'min': 50, 'max': 200})
        }
        
        # Log which properties were found vs. using defaults
        for prop, default_range in [
            ('band_gap', {'min': 0.5, 'max': 2.5}),
            ('formation_energy', {'min': -2.0, 'max': -0.1}),
            ('bulk_modulus', {'min': 50, 'max': 200})
        ]:
            if prop in constraints:
                logger.info(f"Using extracted constraint for '{prop}': {constraints[prop]}")
            else:
                logger.info(f"Property '{prop}' not found in query, using default range: {default_range}")
        
        return megnet_constraints