<script lang="ts">
    import { onMount, onDestroy } from 'svelte';
    import { getStructureUrl } from '../api';
    import { getElementData, getElementColor, getElementDescription } from './elementData';
    import type { AtomInfo, ElementProperties } from '../types';
    
    export let cifUrl: string | null = null;
    export let formula: string = '';
    export let materialId: string = '';
    
    let viewerElement: HTMLDivElement;
    let tooltipElement: HTMLDivElement;
    let infoPanel: HTMLDivElement;
    
    let viewer: any = null;
    let loading: boolean = true;
    let error: string | null = null;
    
    // State variables for viewer controls
    let showUnitCell: boolean = true;
    let showAtomLabels: boolean = false;
    let backgroundColor: string = '#ffffff';
    let style: string = 'ball and stick';
    let useElementColors: boolean = true;
    
    // Current atom information
    let currentAtom: AtomInfo | null = null;
    
    // Store all atom information for structure
    let atomsInfo: AtomInfo[] = [];
    
    // Mouse position for tooltip
    let mouseX: number = 0;
    let mouseY: number = 0;
    let showTooltip: boolean = false;
    
    // Atoms statistics for current structure
    let atomStats: { [symbol: string]: number } = {};
    
    // Import 3Dmol.js dynamically
    async function load3DMol(): Promise<any> {
      try {
        // Load 3Dmol.js from CDN
        const script = document.createElement('script');
        script.src = 'https://3dmol.org/build/3Dmol-min.js';
        script.async = true;
        
        const loaded = new Promise((resolve, reject) => {
          script.onload = resolve;
          script.onerror = reject;
        });
        
        document.head.appendChild(script);
        await loaded;
        
        return window.$3Dmol;
      } catch (err) {
        console.error('Failed to load 3Dmol.js:', err);
        throw err;
      }
    }
    
    // Initialize the 3D viewer
    async function initViewer(): Promise<void> {
      try {
        loading = true;
        error = null;
        
        if (!viewerElement) return;
        
        // Check if $3Dmol is already loaded
        const $3Dmol = (window as any).$3Dmol || await load3DMol();
        
        // Create the viewer
        viewer = $3Dmol.createViewer(viewerElement, {
          backgroundColor: backgroundColor
        });
        
        if (cifUrl) {
          await loadStructure();
        } else {
          error = "No structure URL provided";
          loading = false;
        }
      } catch (err: any) {
        error = `Failed to initialize viewer: ${err.message}`;
        loading = false;
      }
    }
    
    // Load the structure from the CIF URL
    async function loadStructure(): Promise<void> {
      if (!viewer || !cifUrl) return;
      
      try {
        loading = true;
        error = null;
        
        // Get the full URL
        const fullUrl = getStructureUrl(cifUrl);
        
        // Fetch the CIF data
        const response = await fetch(fullUrl || '');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch structure (${response.status})`);
        }
        
        const cifData = await response.text();
        
        // Clear the viewer and atom info
        viewer.clear();
        atomsInfo = [];
        atomStats = {};
        
        // Load the structure
        viewer.addModel(cifData, "cif");
        
        // Extract atom information
        extractAtomInfo();
        
        // Style the structure
        updateStyle();
        
        // Setup hover and click listeners
        setupInteractivity();
        
        // Zoom to fit
        viewer.zoomTo();
        
        // Set initial view
        viewer.setView([ 
          -13.516, -1.289, 15.831,  // lookAt x,y,z
           0.0, 0.0, 0.0,           // center x,y,z
           0.132, -0.271, 0.954     // up x,y,z
        ]);
        
        // Render
        viewer.render();
        
        loading = false;
      } catch (err: any) {
        error = `Failed to load structure: ${err.message}`;
        loading = false;
      }
    }
    
    // Extract atom information from the model
    function extractAtomInfo(): void {
      if (!viewer) return;
      
      const atoms = viewer.getModel().selectedAtoms({});
      atomsInfo = [];
      atomStats = {};
      
      for (let i = 0; i < atoms.length; i++) {
        const atom = atoms[i];
        const element = atom.elem;
        
        // Count atoms by element
        atomStats[element] = (atomStats[element] || 0) + 1;
        
        // Get element properties
        const elementProperties = getElementData(element);
        
        // Create atom info object
        const atomInfo: AtomInfo = {
          element: element,
          atomicNumber: elementProperties.atomicNumber,
          position: [atom.x, atom.y, atom.z],
          elementProperties: elementProperties
        };
        
        atomsInfo.push(atomInfo);
      }
      
      // Sort the atom stats by element symbol
      const tempStats: { [symbol: string]: number } = {};
      Object.keys(atomStats).sort().forEach(key => {
        tempStats[key] = atomStats[key];
      });
      atomStats = tempStats;
    }
    
    // Setup interactivity for atoms
    function setupInteractivity(): void {
      if (!viewer) return;
      
      // Add hover callback
      viewer.setHoverDuration(200);
      
      viewer.setHover({
        hoverCallback: (atom: any, viewer: any, event: any, container: any) => {
          if (!atom) {
            hideTooltip();
            return;
          }
          
          // Update mouse position
          if (event) {
            mouseX = event.pageX;
            mouseY = event.pageY;
          }
          
          // Get element information
          const element = atom.elem;
          const elementProperties = getElementData(element);
          
          // Create current atom info
          currentAtom = {
            element: element,
            atomicNumber: elementProperties.atomicNumber,
            position: [atom.x, atom.y, atom.z],
            elementProperties: elementProperties
          };
          
          // Show tooltip
          showTooltip = true;
          
          // Highlight the atom
          viewer.setStyle({serial: atom.serial}, {sphere: {scale: 0.7, color: elementProperties.color}});
          viewer.render();
        },
        unhoverCallback: () => {
          hideTooltip();
          // Restore the original style
          updateStyle();
        }
      });
      
      // Add click callback for showing details in the info panel
      viewer.addClickListener((atom: any, viewer: any, event: any, container: any) => {
        if (!atom) return;
        
        // Get element information
        const element = atom.elem;
        const elementProperties = getElementData(element);
        
        // Create current atom info
        currentAtom = {
          element: element,
          atomicNumber: elementProperties.atomicNumber,
          position: [atom.x, atom.y, atom.z],
          elementProperties: elementProperties
        };
        
        // Highlight the atom
        viewer.setStyle({}, updateStyle()); // Reset all atoms
        viewer.setStyle({serial: atom.serial}, {sphere: {scale: 0.8, color: '#FFC107'}}); // Highlight selected atom
        viewer.render();
      });
    }
    
    // Hide tooltip
    function hideTooltip(): void {
      showTooltip = false;
      currentAtom = null;
    }
    
    // Update the display style
    function updateStyle(): any {
      if (!viewer) return {};
      
      // Base style object
      let styleObj = {};
      
      // Apply selected style
      switch (style) {
        case 'ball and stick':
          styleObj = {stick: {radius: 0.15}, sphere: {scale: 0.4}};
          break;
        case 'stick':
          styleObj = {stick: {radius: 0.2}};
          break;
        case 'sphere':
          styleObj = {sphere: {scale: 0.6}};
          break;
        case 'line':
          styleObj = {line: {}};
          break;
        case 'cartoon':
          styleObj = {cartoon: {}};
          break;
      }
      
      // Clear existing styles
      viewer.setStyle({}, styleObj);
      
      // Apply element colors if enabled
      if (useElementColors) {
        for (const atom of atomsInfo) {
          const element = atom.element;
          const color = getElementColor(element);
          
          // Apply color based on style
          if (style === 'ball and stick') {
            viewer.setStyle({elem: element}, {sphere: {color: color}, stick: {color: color}});
          } else if (style === 'sphere') {
            viewer.setStyle({elem: element}, {sphere: {color: color}});
          } else if (style === 'stick') {
            viewer.setStyle({elem: element}, {stick: {color: color}});
          } else if (style === 'line') {
            viewer.setStyle({elem: element}, {line: {color: color}});
          }
        }
      }
      
      // Show/hide unit cell
      if (showUnitCell) {
        viewer.addUnitCell();
      }
      
      // Show/hide atom labels
      if (showAtomLabels) {
        viewer.addLabels({}, {font: '12px Arial', alignment: 'center'});
      }
      
      // Update background color
      viewer.setBackgroundColor(backgroundColor);
      
      // Render the updated view
      viewer.render();
      
      return styleObj;
    }
    
    // Handle style change
    function handleStyleChange(): void {
      updateStyle();
    }
    
    // Reset view
    function resetView(): void {
      if (viewer) {
        viewer.zoomTo();
        viewer.render();
      }
    }
    
    // Download structure
    function downloadStructure(): void {
      if (cifUrl) {
        const fullUrl = getStructureUrl(cifUrl);
        if (fullUrl) {
          window.open(fullUrl, '_blank');
        }
      }
    }
    
    // Get a formatted description of the structure
    function getStructureDescription(): string {
      // Count total atoms
      const totalAtoms = Object.values(atomStats).reduce((a, b) => a + b, 0);
      
      // Format description
      let description = `${formula}\n`;
      if (materialId) {
        description += `ID: ${materialId}\n`;
      }
      description += `Total atoms: ${totalAtoms}\n\n`;
      
      // Add element counts
      description += 'Composition:\n';
      Object.entries(atomStats).forEach(([element, count]) => {
        const percentage = (count / totalAtoms * 100).toFixed(1);
        description += `${element}: ${count} (${percentage}%)\n`;
      });
      
      return description;
    }
    
    // Initialize on mount
    onMount(() => {
      initViewer();
    });
    
    // Cleanup on destroy
    onDestroy(() => {
      if (viewer) {
        viewer.clear();
      }
    });
    
    // Watch for URL changes
    $: if (viewer && cifUrl) {
      loadStructure();
    }
  </script>
  
  <div class="structure-viewer">
    <div class="viewer-header">
      <h3>
        {formula || 'Structure Viewer'}
        {#if materialId}
          <span class="material-id">{materialId}</span>
        {/if}
      </h3>
      
      <div class="viewer-controls">
        <div class="control-group">
          <label for="style">Style:</label>
          <select id="style" bind:value={style} on:change={handleStyleChange} disabled={loading}>
            <option value="ball and stick">Ball and Stick</option>
            <option value="stick">Stick</option>
            <option value="sphere">Sphere</option>
            <option value="line">Line</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>
            <input type="checkbox" bind:checked={useElementColors} on:change={handleStyleChange} disabled={loading}>
            Element Colors
          </label>
        </div>
        
        <div class="control-group">
          <label>
            <input type="checkbox" bind:checked={showUnitCell} on:change={handleStyleChange} disabled={loading}>
            Unit Cell
          </label>
        </div>
        
        <div class="control-group">
          <label>
            <input type="checkbox" bind:checked={showAtomLabels} on:change={handleStyleChange} disabled={loading}>
            Atom Labels
          </label>
        </div>
        
        <button class="control-button reset" on:click={resetView} disabled={loading || error !== null}>
          Reset View
        </button>
        
        <button class="control-button download" on:click={downloadStructure} disabled={loading || error !== null || !cifUrl}>
          Download CIF
        </button>
      </div>
    </div>
    
    <div class="viewer-container">
      {#if loading}
        <div class="loading-overlay">
          <div class="spinner"></div>
          <div>Loading structure...</div>
        </div>
      {/if}
      
      {#if error}
        <div class="error-overlay">
          <div class="error-icon">!</div>
          <div>{error}</div>
        </div>
      {/if}
      
      <div class="structure-layout">
        <div class="viewer-element" bind:this={viewerElement}></div>
        
        <div class="info-panel" bind:this={infoPanel}>
          <h4>Structure Information</h4>
          
          {#if Object.keys(atomStats).length > 0}
            <div class="structure-info">
              <pre>{getStructureDescription()}</pre>
            </div>
          {/if}
          
          {#if currentAtom}
            <div class="element-info">
              <h5>Selected Element: {currentAtom.element}</h5>
              <div class="element-color" style="background-color: {currentAtom.elementProperties.color};"></div>
              <div class="element-properties">
                <p><strong>Name:</strong> {currentAtom.elementProperties.name}</p>
                <p><strong>Atomic Number:</strong> {currentAtom.elementProperties.atomicNumber}</p>
                <p><strong>Atomic Mass:</strong> {currentAtom.elementProperties.atomicMass} u</p>
                <p><strong>Category:</strong> {currentAtom.elementProperties.category}</p>
                <p><strong>Electron Config:</strong> {currentAtom.elementProperties.electronConfiguration}</p>
                {#if currentAtom.elementProperties.electronegativity}
                  <p><strong>Electronegativity:</strong> {currentAtom.elementProperties.electronegativity}</p>
                {/if}
                {#if currentAtom.elementProperties.ionizationEnergy}
                  <p><strong>Ionization Energy:</strong> {currentAtom.elementProperties.ionizationEnergy} eV</p>
                {/if}
              </div>
            </div>
          {:else}
            <div class="element-placeholder">
              <p>Hover or click on an atom to see element details</p>
            </div>
          {/if}
        </div>
      </div>
      
      {#if showTooltip && currentAtom}
        <div 
          class="atom-tooltip" 
          bind:this={tooltipElement}
          style="left: {mouseX + 15}px; top: {mouseY + 15}px;"
        >
          <div class="tooltip-title">
            <span class="element-symbol">{currentAtom.element}</span>
            <span class="element-name">{currentAtom.elementProperties.name}</span>
          </div>
          <div class="tooltip-content">
            <p>Z: {currentAtom.elementProperties.atomicNumber}</p>
            <p>Mass: {currentAtom.elementProperties.atomicMass} u</p>
            <p>Category: {currentAtom.elementProperties.category}</p>
          </div>
        </div>
      {/if}
    </div>
  </div>
  
  <style>
    .structure-viewer {
      background-color: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
      overflow: hidden;
      margin-bottom: 2rem;
    }
    
    .viewer-header {
      padding: 1rem;
      border-bottom: 1px solid #e2e8f0;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
    }
    
    h3 {
      margin: 0;
      font-size: 1.25rem;
      color: #2d3748;
    }
    
    h4 {
      margin: 0 0 1rem 0;
      font-size: 1.1rem;
      color: #2d3748;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 0.5rem;
    }
    
    h5 {
      margin: 0.5rem 0;
      font-size: 1rem;
      color: #2d3748;
    }
    
    .material-id {
      font-size: 0.85rem;
      color: #718096;
      font-weight: normal;
      margin-left: 0.5rem;
    }
    
    .viewer-controls {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
    }
    
    .control-group {
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }
    
    .control-group label {
      font-size: 0.85rem;
      color: #4a5568;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }
    
    .control-group select {
      font-size: 0.85rem;
      padding: 0.25rem;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
    }
    
    .control-button {
      background-color: #edf2f7;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 0.25rem 0.5rem;
      font-size: 0.85rem;
      color: #4a5568;
      cursor: pointer;
      transition: all 0.2s ease;
    }
    
    .control-button:hover {
      background-color: #e2e8f0;
    }
    
    .control-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    .control-button.download {
      background-color: #4299e1;
      color: white;
      border-color: #3182ce;
    }
    
    .control-button.download:hover {
      background-color: #3182ce;
    }
    
    .viewer-container {
      position: relative;
      height: 500px;
    }
    
    .structure-layout {
      display: grid;
      grid-template-columns: 3fr 1fr;
      height: 100%;
    }
    
    .viewer-element {
      position: relative;
      width: 100%;
      height: 100%;
    }
    
    .info-panel {
      padding: 1rem;
      border-left: 1px solid #e2e8f0;
      overflow-y: auto;
      background-color: #f8fafc;
      height: 100%;
      box-sizing: border-box;
    }
    
    .structure-info {
      font-size: 0.85rem;
      margin-bottom: 1rem;
    }
    
    .structure-info pre {
      margin: 0;
      font-family: monospace;
      white-space: pre-wrap;
    }
    
    .element-info {
      border-top: 1px solid #e2e8f0;
      padding-top: 1rem;
    }
    
    .element-color {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      margin-right: 0.5rem;
      display: inline-block;
      border: 1px solid #e2e8f0;
    }
    
    .element-properties {
      font-size: 0.85rem;
    }
    
    .element-properties p {
      margin: 0.25rem 0;
    }
    
    .element-placeholder {
      color: #a0aec0;
      font-size: 0.9rem;
      text-align: center;
      padding: 2rem 0;
      border-top: 1px solid #e2e8f0;
      margin-top: 1rem;
    }
    
    .loading-overlay, .error-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background-color: rgba(255, 255, 255, 0.8);
      z-index: 10;
    }
    
    .spinner {
      border: 3px solid rgba(66, 153, 225, 0.3);
      border-radius: 50%;
      border-top: 3px solid #4299e1;
      width: 2rem;
      height: 2rem;
      animation: spin 1s linear infinite;
      margin-bottom: 0.5rem;
    }
    
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .error-icon {
      background-color: #fc8181;
      color: white;
      width: 2rem;
      height: 2rem;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-bottom: 0.5rem;
    }
    
    .error-overlay {
      background-color: rgba(255, 255, 255, 0.9);
      color: #e53e3e;
    }
    
    .atom-tooltip {
      position: fixed;
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      border-radius: 4px;
      padding: 0.5rem;
      font-size: 0.85rem;
      z-index: 100;
      pointer-events: none;
      max-width: 200px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .tooltip-title {
      display: flex;
      align-items: center;
      margin-bottom: 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
      padding-bottom: 0.25rem;
    }
    
    .element-symbol {
      font-weight: bold;
      font-size: 1.2em;
      margin-right: 0.5rem;
    }
    
    .tooltip-content p {
      margin: 0.25rem 0;
      font-size: 0.8rem;
    }
    
    /* Responsive styles */
    @media (max-width: 768px) {
      .structure-layout {
        grid-template-columns: 1fr;
      }
      
      .info-panel {
        height: auto;
        border-left: none;
        border-top: 1px solid #e2e8f0;
      }
      
      .viewer-container {
        height: auto;
      }
      
      .viewer-element {
        height: 300px;
      }
    }
  </style>