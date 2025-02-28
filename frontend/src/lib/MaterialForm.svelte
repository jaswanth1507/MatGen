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