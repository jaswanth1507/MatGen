<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { generateMaterials } from '../api';
  import type { GenerationResponse } from '../types';
  
  const dispatch = createEventDispatcher<{
    success: GenerationResponse;
    error: { error: string };
  }>();
  
  // Form state
  let query: string = '';
  let n_samples: number = 5;
  let temperature: number = 1.2;
  let loading: boolean = false;
  let error: string | null = null;
  
  // Example queries
  const exampleQueries: string[] = [
    "I need a semiconductor with band gap between 1.5 and 2.0 eV",
    "Find materials with low thermal conductivity but high electrical conductivity",
    "I want a lightweight material with good corrosion resistance and high strength-to-weight ratio",
    "Looking for a material for battery electrodes with high stability",
    "Generate a material with high tensile strength and ductility"
  ];
  
  function setExampleQuery(example: string): void {
    query = example;
  }
  
  async function handleSubmit(): Promise<void> {
    if (!query.trim()) {
      error = "Please enter a material description";
      return;
    }
    
    error = null;
    loading = true;
    
    try {
      const result = await generateMaterials({
        query,
        n_samples,
        temperature
      });
      
      dispatch('success', result);
    } catch (err: any) {
      error = err.message || "Failed to generate materials";
      dispatch('error', { error });
    } finally {
      loading = false;
    }
  }
</script>

<form on:submit|preventDefault={handleSubmit}>
<div class="form-group">
  <label for="query">Material Description</label>
  <textarea 
    id="query" 
    bind:value={query} 
    placeholder="Describe the material you need..."
    rows="4"
    class="form-control"
  ></textarea>
</div>

<div class="form-options">
  <div class="option">
    <label for="n_samples">Number of Materials</label>
    <input 
      type="number" 
      id="n_samples" 
      bind:value={n_samples} 
      min="1" 
      max="10"
    />
  </div>
  
  <div class="option">
    <label for="temperature">Temperature</label>
    <input 
      type="range" 
      id="temperature" 
      bind:value={temperature} 
      min="0.5" 
      max="2" 
      step="0.1"
    />
    <span>{temperature}</span>
  </div>
</div>

<div class="example-queries">
  <h4>Example Queries</h4>
  <div class="examples">
    {#each exampleQueries as example}
      <button 
        type="button" 
        class="example-button" 
        on:click={() => setExampleQuery(example)}
      >
        {example}
      </button>
    {/each}
  </div>
</div>

{#if error}
  <div class="error-message">{error}</div>
{/if}

<button 
  type="submit" 
  class="submit-button" 
  disabled={loading || !query.trim()}
>
  {#if loading}
    Generating Materials...
  {:else}
    Generate Materials
  {/if}
</button>
</form>

<style>
form {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #4a5568;
}

textarea {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.75rem;
  font-size: 1rem;
  color: #2d3748;
}

.form-options {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.option {
  flex: 1;
}

.example-queries {
  margin-bottom: 1.5rem;
}

.examples {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.example-button {
  background-color: #edf2f7;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: #4a5568;
  cursor: pointer;
  transition: all 0.2s ease;
}

.example-button:hover {
  background-color: #e2e8f0;
}

.error-message {
  background-color: #fed7d7;
  color: #c53030;
  padding: 0.75rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.submit-button {
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.submit-button:hover {
  background-color: #3182ce;
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>