<script lang="ts">
    import { onMount } from 'svelte';
    import { checkApiHealth } from './api';
    import MaterialForm from './lib/MaterialForm.svelte';
    import MaterialCard from './lib/MaterialCard.svelte';
    import StructureViewer from './lib/StructureViewer.svelte';
    import type { Material, GenerationResponse } from './types';
    
    // App state
    let apiStatus: 'checking' | 'connected' | 'disconnected' = 'checking';
    let generatedMaterials: Material[] = [];
    let selectedMaterial: Material | null = null;
    let processTime: number | null = null;
    
    // Check API health on mount
    onMount(async () => {
      try {
        await checkApiHealth();
        apiStatus = 'connected';
      } catch (error) {
        apiStatus = 'disconnected';
        console.error('API connection failed:', error);
      }
    });
    
    // Handle successful generation
    function handleGenerationSuccess(event: CustomEvent<GenerationResponse>): void {
      const result = event.detail;
      generatedMaterials = result.materials || [];
      processTime = result.process_time || null;
      
      // Select the first material if available
      if (generatedMaterials.length > 0) {
        selectedMaterial = generatedMaterials[0];
      } else {
        selectedMaterial = null;
      }
    }
    
    // Handle generation error
    function handleGenerationError(): void {
      generatedMaterials = [];
      selectedMaterial = null;
      processTime = null;
    }
    
    // Select a material for viewing
    function selectMaterial(material: Material): void {
      selectedMaterial = material;
    }
  </script>