// Material types
export interface MaterialProperty {
    min: number;
    max: number;
  }
  
  export interface Constraints {
    band_gap: MaterialProperty;
    formation_energy: MaterialProperty;
    bulk_modulus: MaterialProperty;
    [key: string]: MaterialProperty;
  }
  
  export interface Material {
    formula: string;
    material_id: string;
    band_gap: number;
    formation_energy: number;
    bulk_modulus: number;
    cif_url: string | null;
  }
  
  export interface GenerationResponse {
    success: boolean;
    query: string;
    constraints: Constraints;
    materials: Material[];
    process_time: number;
    error?: string;
  }
  
  // Structure visualization types
  export interface AtomInfo {
    element: string;
    atomicNumber: number;
    position: [number, number, number];
    elementProperties: ElementProperties;
  }
  
  export interface ElementProperties {
    name: string;
    symbol: string;
    atomicNumber: number;
    atomicMass: number;
    category: string;
    color: string;
    electronConfiguration: string;
    electronegativity?: number;
    ionizationEnergy?: number;
  }
  
  export interface LatticeParameters {
    a: number;
    b: number;
    c: number;
    alpha: number;
    beta: number;
    gamma: number;
  }
  
  export interface StructureData {
    formula: string;
    atoms: string[];
    positions: number[][];
    lattice_parameters: LatticeParameters;
    lattice_vectors: number[][];
  }
  
  // Element data type (for periodic table information)
  export interface ElementData {
    [symbol: string]: ElementProperties;
  }