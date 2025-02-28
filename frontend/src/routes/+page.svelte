<script lang="ts">
    import { onMount } from 'svelte';
    import { checkApiHealth } from '../api';
    import MaterialForm from '../lib/MaterialForm.svelte';
    import MaterialCard from '../lib/MaterialCard.svelte';
    import StructureViewer from '../lib/StructureViewer.svelte';
    import type { Material, GenerationResponse } from '../types';
    
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
  
  <main class="container">
    <header>
      <div class="logo">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="12 2 19 7 19 17 12 22 5 17 5 7 12 2"></polygon>
          <line x1="12" y1="2" x2="12" y2="22"></line>
          <line x1="5" y1="7" x2="19" y2="7"></line>
          <line x1="5" y1="17" x2="19" y2="17"></line>
          <line x1="19" y1="12" x2="5" y2="12"></line>
        </svg>
        <h1>Material Generator</h1>
      </div>
      
      <div class="api-status">
        API Status: 
        {#if apiStatus === 'checking'}
          <span class="status checking">Checking...</span>
        {:else if apiStatus === 'connected'}
          <span class="status connected">Connected</span>
        {:else}
          <span class="status disconnected">Disconnected</span>
        {/if}
      </div>
    </header>
    
    <section class="form-section">
      <MaterialForm 
        on:success={handleGenerationSuccess}
        on:error={handleGenerationError}
      />
    </section>
    
    {#if generatedMaterials.length > 0}
      <section class="results-section">
        <div class="results-header">
          <h2>Generated Materials</h2>
          {#if processTime !== null}
            <div class="process-time">
              Generated in {processTime.toFixed(2)} seconds
            </div>
          {/if}
        </div>
        
        <div class="results-content">
          <div class="materials-list">
            {#each generatedMaterials as material}
              <MaterialCard 
                {material}
                selected={selectedMaterial === material}
                on:click={() => selectMaterial(material)}
              />
            {/each}
          </div>
          
          <div class="structure-view">
            {#if selectedMaterial}
              <StructureViewer 
                cifUrl={selectedMaterial.cif_url}
                formula={selectedMaterial.formula}
                materialId={selectedMaterial.material_id}
              />
            {:else}
              <div class="no-selection">
                <div class="placeholder-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="12 2 19 7 19 17 12 22 5 17 5 7 12 2"></polygon>
                  </svg>
                </div>
                <div class="placeholder-text">
                  Select a material to view its 3D structure
                </div>
              </div>
            {/if}
          </div>
        </div>
      </section>
    {/if}
    
    <footer>
      <p>
        Material Generator API - Powered by MEGNet+VAE and Phi-3-mini
      </p>
    </footer>
  </main>
  
  <style>
    .form-section {
      margin-bottom: 2rem;
    }
    
    .results-section {
      margin-top: 2rem;
    }
    
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
    
    .results-header h2 {
      margin: 0;
      font-size: 1.5rem;
      color: #2d3748;
    }
    
    .process-time {
      font-size: 0.9rem;
      color: #718096;
    }
    
    .results-content {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 1.5rem;
    }
    
    .materials-list {
      overflow-y: auto;
      max-height: 600px;
    }
    
    .no-selection {
      height: 400px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .placeholder-icon {
      color: #cbd5e0;
      margin-bottom: 1rem;
    }
    
    .placeholder-text {
      color: #a0aec0;
      font-size: 1.1rem;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
      .results-content {
        grid-template-columns: 1fr;
      }
      
      .materials-list {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
        gap: 1rem;
        max-height: none;
      }
    }
  </style>