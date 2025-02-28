"""
Material generation core components for VAE model and structure recovery.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from sklearn.neighbors import NearestNeighbors

class VAEModel(models.Model):
    """Custom VAE model class that properly handles the KL loss"""

    def __init__(self, encoder, decoder, latent_dim, **kwargs):
        super(VAEModel, self).__init__(**kwargs)
        self.encoder = encoder
        self.decoder = decoder
        self.latent_dim = latent_dim
        self.kl_weight = 1.0  # Default weight for KL loss

    def call(self, inputs):
        # This defines the forward pass
        feature_input, property_input = inputs

        # Encode
        z_mean, z_log_var = self.encoder([feature_input, property_input])

        # Sample
        batch_size = tf.shape(z_mean)[0]
        epsilon = tf.random.normal(shape=(batch_size, self.latent_dim))
        z = z_mean + tf.exp(0.5 * z_log_var) * epsilon

        # Decode
        reconstructed = self.decoder([z, property_input])

        # Add KL loss
        kl_loss = -0.5 * tf.reduce_mean(
            tf.reduce_sum(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var), axis=1)
        )
        self.add_loss(self.kl_weight * kl_loss)

        return reconstructed

class MaterialVAE:
    def __init__(self, input_dim, property_dim=3, latent_dim=16, hidden_dims=[64, 32]):
        """
        Initialize the VAE model for material generation.

        Args:
            input_dim (int): Dimension of input features
            property_dim (int): Dimension of material properties
            latent_dim (int): Dimension of latent space
            hidden_dims (list): Dimensions of hidden layers
        """
        self.input_dim = input_dim
        self.property_dim = property_dim
        self.latent_dim = latent_dim
        self.hidden_dims = hidden_dims
        self.kl_weight = 1.0  # Will be used for KL annealing

        # Build the encoder, decoder, and full VAE model
        self.encoder = self._build_encoder()
        self.decoder = self._build_decoder()
        self.vae_model = self._build_vae()

    def _build_encoder(self):
        """Build the encoder network."""
        # Input layers
        feature_input = layers.Input(shape=(self.input_dim,), name='feature_input')
        property_input = layers.Input(shape=(self.property_dim,), name='property_input')

        # Combine inputs
        x = feature_input

        # Add hidden layers
        for i, dim in enumerate(self.hidden_dims):
            x = layers.Dense(dim, activation='relu', name=f'encoder_dense_{i}')(x)

        # Output layers for mean and log variance
        z_mean = layers.Dense(self.latent_dim, name='z_mean')(x)
        z_log_var = layers.Dense(self.latent_dim, name='z_log_var')(x)

        # Create encoder model
        encoder = models.Model([feature_input, property_input], [z_mean, z_log_var], name='encoder')
        return encoder

    def _build_decoder(self):
        """Build the decoder network."""
        # Input layers
        latent_input = layers.Input(shape=(self.latent_dim,), name='latent_input')
        property_input = layers.Input(shape=(self.property_dim,), name='property_input')

        # Concatenate latent vector with property conditioning
        x = layers.Concatenate()([latent_input, property_input])

        # Add hidden layers in reverse order
        for i, dim in enumerate(reversed(self.hidden_dims)):
            x = layers.Dense(dim, activation='relu', name=f'decoder_dense_{i}')(x)

        # Output layer for reconstructed features
        outputs = layers.Dense(self.input_dim, activation='sigmoid', name='decoder_output')(x)

        # Create decoder model
        decoder = models.Model([latent_input, property_input], outputs, name='decoder')
        return decoder

    def _build_vae(self):
        """Build the VAE model using the custom VAEModel class."""
        # Create the custom VAE model
        vae = VAEModel(
            encoder=self.encoder,
            decoder=self.decoder,
            latent_dim=self.latent_dim,
            name='vae'
        )

        # Define inputs for compilation (needed to build the model)
        dummy_features = tf.keras.Input(shape=(self.input_dim,))
        dummy_properties = tf.keras.Input(shape=(self.property_dim,))

        # Build the model
        vae([dummy_features, dummy_properties])

        # Compile the model
        vae.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss='mse')

        # Set the KL weight
        vae.kl_weight = self.kl_weight

        return vae

    def generate(self, properties, n_samples=1, temperature=1.2):
        """
        Generate new materials conditioned on desired properties with temperature control.

        Args:
            properties (np.ndarray): Target properties
            n_samples (int): Number of samples to generate
            temperature (float): Higher values (>1.0) increase diversity but may reduce accuracy

        Returns:
            np.ndarray: Generated feature vectors
        """
        # Ensure properties have the right shape
        if properties.ndim == 1:
            properties = properties.reshape(1, -1)

        # Repeat properties for n_samples
        if n_samples > 1:
            properties = np.repeat(properties, n_samples, axis=0)

        # Sample from the latent space with temperature control
        random_latent_vectors = np.random.normal(0, temperature, size=(n_samples, self.latent_dim))

        # Decode the random latent vectors
        generated_features = self.decoder.predict([random_latent_vectors, properties])

        return generated_features

    def save(self, filepath):
        """Save the VAE model."""
        self.vae_model.save_weights(filepath)

    def load(self, filepath):
        """Load the VAE model."""
        self.vae_model.load_weights(filepath)

class StructureRecovery:
    def __init__(self, feature_matrix, materials, feature_scaler=None, n_neighbors=5):
        """
        Initialize the structure recovery module.

        Args:
            feature_matrix (np.ndarray): Original feature matrix
            materials (list): List of materials with structures
            feature_scaler (sklearn.preprocessing.MinMaxScaler): Scaler used for features
            n_neighbors (int): Number of nearest neighbors to consider
        """
        self.feature_matrix = feature_matrix
        self.materials = materials
        self.feature_scaler = feature_scaler
        self.n_neighbors = n_neighbors

        # Build nearest neighbors model
        self.nn_model = self._build_nn_model()

        # Keep track of previously selected materials to promote diversity
        self.previously_selected = set()

    def _build_nn_model(self):
        """Build nearest neighbors model for structure lookup."""
        nn_model = NearestNeighbors(n_neighbors=self.n_neighbors)
        nn_model.fit(self.feature_matrix)
        return nn_model

    def recover_structures(self, generated_features, return_multiple=False, diversity_weight=0.7):
        """
        Recover crystal structures from generated features with improved diversity.

        Args:
            generated_features (np.ndarray): Generated feature vectors
            return_multiple (bool): Whether to return multiple candidate structures
            diversity_weight (float): Weight for diversity penalty (0-1)

        Returns:
            list: Recovered structures or list of candidate structures
        """
        # Inverse transform if scaler is provided
        if self.feature_scaler is not None:
            generated_features = self.feature_scaler.inverse_transform(generated_features)

        # Find nearest neighbors
        distances, indices = self.nn_model.kneighbors(generated_features)

        recovered_structures = []
        for i in range(len(generated_features)):
            if return_multiple:
                # Return multiple candidate structures, promoting diversity
                candidates = []
                already_added = set()  # Track formulas we've already added

                # First pass: try to find diverse candidates
                for j in range(min(15, self.n_neighbors)):  # Look at more neighbors
                    idx = indices[i, j]
                    structure = self.materials[idx]["structure"]
                    formula = structure.composition.reduced_formula
                    distance = distances[i, j]

                    # Only add if we haven't seen this formula yet in this batch
                    if formula not in already_added:
                        candidates.append({
                            "structure": structure,
                            "distance": distance,
                            "material_id": self.materials[idx]["material_id"]
                        })
                        already_added.add(formula)

                    # If we have enough candidates, stop
                    if len(candidates) >= 5:
                        break

                # Second pass: if we don't have enough candidates, add more
                if len(candidates) < 5:
                    for j in range(self.n_neighbors):
                        idx = indices[i, j]
                        structure = self.materials[idx]["structure"]
                        distance = distances[i, j]

                        # Check if we already added this material
                        if j < len(candidates):
                            continue

                        candidates.append({
                            "structure": structure,
                            "distance": distance,
                            "material_id": self.materials[idx]["material_id"]
                        })

                        # Stop when we have 5 candidates
                        if len(candidates) >= 5:
                            break

                recovered_structures.append(candidates)
            else:
                # Find the best match that promotes diversity
                for j in range(min(10, self.n_neighbors)):
                    idx = indices[i, j]
                    structure = self.materials[idx]["structure"]
                    formula = structure.composition.reduced_formula

                    # If formula hasn't been used recently or with probability based on diversity_weight
                    if formula not in self.previously_selected or np.random.random() > diversity_weight:
                        self.previously_selected.add(formula)
                        recovered_structures.append(structure)
                        break
                else:
                    # Fallback: use the closest match
                    idx = indices[i, 0]
                    structure = self.materials[idx]["structure"]
                    recovered_structures.append(structure)

                # Limit memory of previously selected formulas
                if len(self.previously_selected) > 20:
                    self.previously_selected = set(list(self.previously_selected)[-20:])

        return recovered_structures