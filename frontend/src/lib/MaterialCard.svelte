<script lang="ts">
    import type { Material } from '../types';
    
    export let material: Material;
    export let selected: boolean = false;
    
    // Format a numeric value with units
    function formatValue(value: number | undefined | null, unit: string, precision: number = 2): string {
      if (value === undefined || value === null) {
        return 'N/A';
      }
      return `${value.toFixed(precision)} ${unit}`;
    }
  </script>
  
  <div class="material-card {selected ? 'selected' : ''}" on:click>
    <div class="card-header">
      <h3 class="formula">{material.formula}</h3>
      {#if material.material_id}
        <div class="material-id">{material.material_id}</div>
      {/if}
    </div>
    
    <div class="properties">
      <div class="property">
        <div class="property-name">Band Gap</div>
        <div class="property-value">{formatValue(material.band_gap, 'eV')}</div>
      </div>
      
      <div class="property">
        <div class="property-name">Formation Energy</div>
        <div class="property-value">{formatValue(material.formation_energy, 'eV/atom')}</div>
      </div>
      
      <div class="property">
        <div class="property-name">Bulk Modulus</div>
        <div class="property-value">{formatValue(material.bulk_modulus, 'GPa')}</div>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="view-button">
        View Structure
      </div>
    </div>
  </div>
  
  <style>
    .material-card {
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      padding: 1rem;
      margin-bottom: 1rem;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 2px solid transparent;
    }
    
    .material-card:hover {
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      transform: translateY(-2px);
    }
    
    .material-card.selected {
      border-color: #4299e1;
      background-color: #ebf8ff;
    }
    
    .card-header {
      margin-bottom: 0.75rem;
    }
    
    .formula {
      margin: 0;
      font-size: 1.25rem;
      color: #2d3748;
    }
    
    .material-id {
      font-size: 0.8rem;
      color: #718096;
      margin-top: 0.25rem;
    }
    
    .properties {
      border-top: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.75rem 0;
      margin-bottom: 0.75rem;
    }
    
    .property {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.35rem;
    }
    
    .property:last-child {
      margin-bottom: 0;
    }
    
    .property-name {
      font-size: 0.85rem;
      color: #4a5568;
    }
    
    .property-value {
      font-size: 0.9rem;
      font-weight: 600;
      color: #2d3748;
    }
    
    .card-footer {
      display: flex;
      justify-content: flex-end;
    }
    
    .view-button {
      font-size: 0.9rem;
      color: #4299e1;
      font-weight: 600;
      display: flex;
      align-items: center;
    }
    
    .material-card.selected .view-button {
      color: #2b6cb0;
    }
  </style>