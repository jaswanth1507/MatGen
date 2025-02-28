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
    // If already loaded, return it
    if (window.$3Dmol) {
      console.log("3DMol.js already loaded");
      return window.$3Dmol;
    }

    console.log("Loading 3DMol.js from CDN...");
    
    try {
      // Load 3Dmol.js from CDN - version 2.0.1 which should be more stable
      const script = document.createElement('script');
      script.src = 'https://3Dmol.org/build/3Dmol-min.js';
      script.async = true;
      script.crossOrigin = "anonymous";

      return new Promise((resolve, reject) => {
        script.onload = () => {
          console.log("3DMol.js script loaded");
          if (window.$3Dmol) {
            console.log("$3Dmol object available:", typeof window.$3Dmol);
            resolve(window.$3Dmol);
          } else {
            console.error("3DMol.js loaded but $3Dmol is not defined");
            reject(new Error('3DMol.js loaded but $3Dmol is not defined'));
          }
        };
        
        script.onerror = (e) => {
          console.error("Failed to load 3DMol.js script:", e);
          reject(new Error('Failed to load 3DMol.js'));
        };

        document.head.appendChild(script);
      });
    } catch (err) {
      console.error('Error during 3DMol.js loading:', err);
      throw err;
    }
  }
  
  // Initialize the 3D viewer
  async function initViewer(): Promise<void> {
    try {
      loading = true;
      error = null;

      if (!viewerElement) {
        console.error("Viewer element reference is missing");
        return;
      }
      
      console.log("Initializing viewer with element:", viewerElement);

      // Set explicit inline dimensions to ensure the viewer has proper size
      viewerElement.style.width = "100%";
      viewerElement.style.height = "400px";

      // Try to load 3DMol.js
      let $3Dmol;
      try {
        $3Dmol = await load3DMol();
        console.log("3DMol.js loaded successfully, version:", $3Dmol.version || "unknown");
      } catch (err) {
        console.error("Failed to load 3DMol.js:", err);
        error = `Failed to load 3DMol.js: ${err.message}`;
        loading = false;
        return;
      }

      // Clear any existing viewer
      if (viewer) {
        try {
          viewer.clear();
          console.log("Cleared existing viewer");
        } catch (e) {
          console.warn("Could not clear existing viewer:", e);
        }
      }

      // Add a slight delay to ensure DOM is fully ready
      await new Promise(resolve => setTimeout(resolve, 100));

      // Create the viewer with explicit dimensions
      try {
        console.log("Creating viewer with backgroundColor:", backgroundColor);
        
        // Log the element's dimensions
        console.log("Viewer element dimensions:", 
          viewerElement.offsetWidth, "×", viewerElement.offsetHeight);
        
        // Create with explicit config
        viewer = $3Dmol.createViewer(viewerElement, {
          backgroundColor: backgroundColor,
          antialias: true,
          id: 'molecule-viewer',
          width: viewerElement.offsetWidth,
          height: viewerElement.offsetHeight
        });
        
        console.log("3DMol viewer created:", viewer ? "success" : "failed");
        
        // Check if canvas was created
        const canvas = viewerElement.querySelector('canvas');
        if (!canvas) {
          console.warn("No canvas element found after creating viewer");
        } else {
          console.log("Canvas created successfully with dimensions:", 
            canvas.width, "×", canvas.height);
          
          // Ensure canvas has correct style
          canvas.style.position = "absolute";
          canvas.style.top = "0";
          canvas.style.left = "0";
          canvas.style.zIndex = "5";
        }
        
        if (!viewer) {
          throw new Error("Failed to create 3DMol viewer - returned null/undefined");
        }
      } catch (err) {
        console.error("Error creating 3DMol viewer:", err);
        error = `Failed to create 3D viewer: ${err.message}`;
        loading = false;
        return;
      }

      if (cifUrl) {
        await loadStructure();
      } else {
        error = "No structure URL provided";
        loading = false;
      }
    } catch (err: any) {
      console.error("Failed to initialize viewer:", err);
      error = `Failed to initialize viewer: ${err.message}`;
      loading = false;
    }
  }

  async function loadStructure(): Promise<void> {
  if (!viewer || !cifUrl) {
    console.error("Cannot load structure - viewer or cifUrl is missing");
    return;
  }
  
  try {
    loading = true;
    error = null;
    
    // Get the full URL
    const fullUrl = getStructureUrl(cifUrl);
    
    if (!fullUrl) {
      throw new Error("Invalid structure URL");
    }
    
    console.log("Loading structure from:", fullUrl);
    
    // Fetch the CIF data with timeout and error handling
    let cifData: string;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15-second timeout
      
      const response = await fetch(fullUrl, { signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Server returned ${response.status} ${response.statusText}`);
      }
      
      cifData = await response.text();
      console.log("Received data of length:", cifData.length);
      console.log("First 100 characters:", cifData.substring(0, 100));
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw new Error("Request timed out. Server may be unavailable.");
      }
      throw err;
    }
    
    // Simple validation that it looks like a CIF file
    if (!cifData.includes("data_") && !cifData.includes("_cell_")) {
      console.error("Response doesn't look like a valid CIF file:", cifData.substring(0, 100) + "...");
      throw new Error("Response is not a valid CIF file");
    }
    
    // Clear the viewer and atom info
    try {
      viewer.clear();
      atomsInfo = [];
      atomStats = {};
      console.log("Viewer cleared");
    } catch (err) {
      console.error("Error clearing viewer:", err);
    }
    
    // SIMPLIFIED APPROACH: Focus on core functionality
    try {
      // Set basic styling first
      viewer.setBackgroundColor(backgroundColor);
      
      // Add the model
      console.log("Adding model to viewer");
      viewer.addModel(cifData, "cif", {keepH: true});
      console.log("Model added successfully");
      
      // Extract atom information
      extractAtomInfo();
      
      // Apply a simplified style to ensure visibility
      viewer.setStyle({}, {
        stick: {radius: 0.3, opacity: 1.0},
        sphere: {scale: 0.5, opacity: 1.0}
      });
      
      // Apply element colors if enabled
      if (useElementColors) {
        for (const atom of atomsInfo) {
          const element = atom.element;
          const color = getElementColor(element);
          
          viewer.setStyle({elem: element}, {
            sphere: {color: color, scale: 0.5, opacity: 1.0},
            stick: {color: color, radius: 0.3, opacity: 1.0}
          });
        }
      }
      
      // Add unit cell
      if (showUnitCell) {
        try {
          viewer.addUnitCell();
        } catch (e) {
          console.warn("Could not add unit cell:", e);
        }
      }
      
      // CRITICAL: Force zoom to center the model in view
      viewer.zoomTo();
      
      // Set up click interactions - modified to use setClickable instead of addClickListener
      try {
        console.log("Setting up click interactions");
        viewer.setClickable({}, true, function(atom: any, viewer: any) {
          if (!atom) return;
          
          console.log("Atom clicked:", atom);
          const element = atom.elem;
          const elementProperties = getElementData(element);
          
          currentAtom = {
            element: element,
            atomicNumber: elementProperties.atomicNumber,
            position: [atom.x, atom.y, atom.z],
            elementProperties: elementProperties
          };
          
          // Update the display - highlight just this atom
          updateStyle(); // Reset all atoms first
          viewer.setStyle({serial: atom.serial}, {
            sphere: {scale: 0.7, color: '#FFC107', opacity: 1.0}
          });
          viewer.render();
        });
        console.log("Click interactions set up successfully");
      } catch (err) {
        console.warn("Could not set up click interactions, continuing anyway:", err);
        // Continue without click interactions rather than failing the whole load
      }
      
      // Final render
      viewer.render();
      console.log("Structure loaded successfully");
      
      // Force a second render after a short delay
      setTimeout(() => {
        if (viewer) {
          viewer.render();
          console.log("Second render completed");
        }
      }, 500);
      
    } catch (err) {
      console.error("Error loading structure:", err);
      throw err;
    }
    
    loading = false;
    
  } catch (err: any) {
    console.error("Structure loading error:", err);
    error = `Failed to load structure: ${err.message}`;
    loading = false;
  }
}

  // Extract atom information from the model
  function extractAtomInfo(): void {
    if (!viewer) return;
    
    try {
      const model = viewer.getModel();
      if (!model) {
        console.error("No model found in viewer");
        return;
      }
      
      // Some versions use selectedAtoms, others might use differently named methods
      let atoms;
      if (typeof model.selectedAtoms === 'function') {
        atoms = model.selectedAtoms({});
      } else if (typeof model.atoms === 'function') {
        atoms = model.atoms({});
      } else if (model.atoms && Array.isArray(model.atoms)) {
        atoms = model.atoms;
      } else {
        console.error("Could not retrieve atoms from model");
        return;
      }
      
      console.log(`Retrieved ${atoms.length} atoms from model`);
      
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
      
    } catch (err) {
      console.error("Error extracting atom info:", err);
      atomsInfo = [];
      atomStats = {};
    }
  }
  
  // A completely simplified version of interactivity setup
  function setupSimpleInteractions(): void {
    if (!viewer) return;
    
    try {
      console.log("Setting up simple atom click interaction and ensuring visibility");
      
      // CRITICAL FIX: Set explicit visualization style first
      // This ensures atoms are visible with proper colors and sizes
      viewer.setStyle({}, {
        stick: {radius: 0.3, opacity: 1.0},
        sphere: {scale: 0.5, opacity: 1.0}
      });
      
      // Explicitly set colors by element
      if (useElementColors) {
        for (const atom of atomsInfo) {
          const element = atom.element;
          const color = getElementColor(element);
          
          viewer.setStyle({elem: element}, {
            sphere: {color: color, scale: 0.5, opacity: 1.0},
            stick: {color: color, radius: 0.3, opacity: 1.0}
          });
        }
      }
      
      // CRITICAL: Force zoomTo to ensure atoms are in view
      viewer.zoomTo();
      
      // CRITICAL: Add unit cell to help with orientation
      try {
        viewer.addUnitCell();
      } catch (e) {
        console.warn("Could not add unit cell:", e);
      }
      
      // Force render before adding click handlers
      viewer.render();
      
      // Make all atoms clickable
      viewer.setClickable({}, true, function(atom: any) {
        console.log("Atom clicked:", atom);
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
        
        // Highlight the atom - use a larger, brighter sphere
        updateStyle(); // Reset all atoms
        viewer.setStyle({serial: atom.serial}, {
          sphere: {scale: 0.7, color: '#FFC107', opacity: 1.0}
        });
        viewer.render();
      });
      
      console.log("Click interaction and visibility setup complete");
    } catch (err) {
      console.error("Error setting up atom interaction:", err);
    }
  }
  
  // Hide tooltip
  function hideTooltip(): void {
    showTooltip = false;
    currentAtom = null;
  }
  
  // Update the display style
  function updateStyle(): any {
    if (!viewer) return {};
    
    console.log("Updating style");
    
    // Base style object
    let styleObj = {};
    
    // Apply selected style
    switch (style) {
      case 'ball and stick':
        styleObj = {stick: {radius: 0.3}, sphere: {scale: 0.5}};
        break;
      case 'stick':
        styleObj = {stick: {radius: 0.3}};
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
      default:
        styleObj = {stick: {radius: 0.3}, sphere: {scale: 0.5}}; // Default to ball and stick
        break;
    }
    
    // Clear existing styles
    try {
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
        try {
          viewer.addUnitCell();
        } catch (e) {
          console.warn("Error adding unit cell:", e);
        }
      }
      
      // Show/hide atom labels
      if (showAtomLabels) {
        try {
          viewer.addLabels({}, {font: '12px Arial', alignment: 'center'});
        } catch (e) {
          console.warn("Error adding labels:", e);
        }
      }
      
      // Update background color
      viewer.setBackgroundColor(backgroundColor);
      
      // Render the updated view
      viewer.render();
    } catch (err) {
      console.error("Error applying style:", err);
    }
    
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
  
  // Debug function to check viewer state
  function debugViewerState(): void {
    if (!viewer || !viewerElement) return;
    
    console.log("DEBUG: Viewer state");
    console.log("viewerElement dimensions:", viewerElement.offsetWidth, "×", viewerElement.offsetHeight);
    
    const canvas = viewerElement.querySelector('canvas');
    if (canvas) {
      console.log("Canvas dimensions:", canvas.width, "×", canvas.height);
      console.log("Canvas style:", canvas.style.cssText);
    } else {
      console.warn("No canvas element found in viewerElement");
    }
    
    console.log("Atoms count:", atomsInfo.length);
    console.log("Current style:", style);
  }
  
  // Function to handle window resizing
  function setupResizeHandler(): () => void {
    // Create resize observer to detect container size changes
    try {
      const resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          if (entry.target === viewerElement && viewer) {
            console.log("Viewer element resized:", 
              entry.contentRect.width, "×", entry.contentRect.height);
            
            try {
              // Resize the viewer
              viewer.resize();
              // Re-render with a short delay to ensure complete redraw
              setTimeout(() => {
                if (viewer) {
                  viewer.render();
                  console.log("Viewer resized and re-rendered");
                }
              }, 100);
            } catch (e) {
              console.warn("Error handling resize:", e);
            }
          }
        }
      });
      
      // Start observing the viewer element
      if (viewerElement) {
        resizeObserver.observe(viewerElement);
        console.log("Resize observer attached to viewer element");
      }
      
      // Clean up on component destroy
      return () => {
        resizeObserver.disconnect();
        console.log("Resize observer disconnected");
      };
    } catch (e) {
      console.warn("ResizeObserver not supported or error setting up:", e);
      
      // Fallback to window resize event
      const handleResize = () => {
        if (viewer) {
          try {
            viewer.resize();
            viewer.render();
            console.log("Viewer resized via window event");
          } catch (e) {
            console.warn("Error handling window resize:", e);
          }
        }
      };
      
      window.addEventListener('resize', handleResize);
      
      // Clean up on component destroy
      return () => {
        window.removeEventListener('resize', handleResize);
        console.log("Window resize event listener removed");
      };
    }
  }
  
  // Initialize on mount
  onMount(() => {
    console.log("StructureViewer component mounted");
    initViewer();
    
    // Add resize handling
    const cleanupResize = setupResizeHandler();
    
    // Return cleanup function to handle both resize and viewer cleanup
    return () => {
      // Clean up resize handler
      cleanupResize();
      
      // Clean up viewer
      if (viewer) {
        try {
          viewer.clear();
          console.log("Viewer cleared on unmount");
        } catch (e) {
          console.warn("Error cleaning up viewer:", e);
        }
      }
    };
  });
  
  // Watch for URL changes
  $: if (viewer && cifUrl) {
    console.log("CIF URL changed, loading new structure:", cifUrl);
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
      
      <button class="control-button" on:click={debugViewerState} disabled={loading || error !== null}>
        Debug Viewer
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
            <p>Click on an atom to see element details</p>
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
    overflow: visible; /* Ensure overflow is visible */
  }
  
  .structure-layout {
    display: grid;
    grid-template-columns: 3fr 1fr;
    height: 500px; /* Changed from 100% to explicit height */
  }
  
  .viewer-element {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 400px;
    z-index: 5;
    overflow: visible;
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
  
  /* Ensure the 3DMol canvas is visible - global CSS to target it */
  :global(canvas.viewer_3dmoljs) {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    z-index: 5 !important;
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