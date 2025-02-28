import type { ElementData, ElementProperties } from '../types';

// Element data for the most common elements in materials
export const elementData: ElementData = {
  "H": {
    name: "Hydrogen",
    symbol: "H",
    atomicNumber: 1,
    atomicMass: 1.008,
    category: "Nonmetal",
    color: "#FFFFFF",
    electronConfiguration: "1s¹",
    electronegativity: 2.20,
    ionizationEnergy: 13.598
  },
  "Li": {
    name: "Lithium",
    symbol: "Li",
    atomicNumber: 3,
    atomicMass: 6.94,
    category: "Alkali Metal",
    color: "#CC80FF",
    electronConfiguration: "[He] 2s¹",
    electronegativity: 0.98,
    ionizationEnergy: 5.392
  },
  "Be": {
    name: "Beryllium",
    symbol: "Be",
    atomicNumber: 4,
    atomicMass: 9.0122,
    category: "Alkaline Earth Metal",
    color: "#C2FF00",
    electronConfiguration: "[He] 2s²",
    electronegativity: 1.57,
    ionizationEnergy: 9.323
  },
  "B": {
    name: "Boron",
    symbol: "B",
    atomicNumber: 5,
    atomicMass: 10.81,
    category: "Metalloid",
    color: "#FFB5B5",
    electronConfiguration: "[He] 2s² 2p¹",
    electronegativity: 2.04,
    ionizationEnergy: 8.298
  },
  "C": {
    name: "Carbon",
    symbol: "C",
    atomicNumber: 6,
    atomicMass: 12.011,
    category: "Nonmetal",
    color: "#909090",
    electronConfiguration: "[He] 2s² 2p²",
    electronegativity: 2.55,
    ionizationEnergy: 11.260
  },
  "N": {
    name: "Nitrogen",
    symbol: "N",
    atomicNumber: 7,
    atomicMass: 14.007,
    category: "Nonmetal",
    color: "#3050F8",
    electronConfiguration: "[He] 2s² 2p³",
    electronegativity: 3.04,
    ionizationEnergy: 14.534
  },
  "O": {
    name: "Oxygen",
    symbol: "O",
    atomicNumber: 8,
    atomicMass: 15.999,
    category: "Nonmetal",
    color: "#FF0D0D",
    electronConfiguration: "[He] 2s² 2p⁴",
    electronegativity: 3.44,
    ionizationEnergy: 13.618
  },
  "F": {
    name: "Fluorine",
    symbol: "F",
    atomicNumber: 9,
    atomicMass: 18.998,
    category: "Halogen",
    color: "#90E050",
    electronConfiguration: "[He] 2s² 2p⁵",
    electronegativity: 3.98,
    ionizationEnergy: 17.423
  },
  "Na": {
    name: "Sodium",
    symbol: "Na",
    atomicNumber: 11,
    atomicMass: 22.99,
    category: "Alkali Metal",
    color: "#AB5CF2",
    electronConfiguration: "[Ne] 3s¹",
    electronegativity: 0.93,
    ionizationEnergy: 5.139
  },
  "Mg": {
    name: "Magnesium",
    symbol: "Mg",
    atomicNumber: 12,
    atomicMass: 24.305,
    category: "Alkaline Earth Metal",
    color: "#8AFF00",
    electronConfiguration: "[Ne] 3s²",
    electronegativity: 1.31,
    ionizationEnergy: 7.646
  },
  "Al": {
    name: "Aluminum",
    symbol: "Al",
    atomicNumber: 13,
    atomicMass: 26.982,
    category: "Post-Transition Metal",
    color: "#BFA6A6",
    electronConfiguration: "[Ne] 3s² 3p¹",
    electronegativity: 1.61,
    ionizationEnergy: 5.986
  },
  "Si": {
    name: "Silicon",
    symbol: "Si",
    atomicNumber: 14,
    atomicMass: 28.085,
    category: "Metalloid",
    color: "#F0C8A0",
    electronConfiguration: "[Ne] 3s² 3p²",
    electronegativity: 1.90,
    ionizationEnergy: 8.152
  },
  "P": {
    name: "Phosphorus",
    symbol: "P",
    atomicNumber: 15,
    atomicMass: 30.974,
    category: "Nonmetal",
    color: "#FF8000",
    electronConfiguration: "[Ne] 3s² 3p³",
    electronegativity: 2.19,
    ionizationEnergy: 10.487
  },
  "S": {
    name: "Sulfur",
    symbol: "S",
    atomicNumber: 16,
    atomicMass: 32.06,
    category: "Nonmetal",
    color: "#FFFF30",
    electronConfiguration: "[Ne] 3s² 3p⁴",
    electronegativity: 2.58,
    ionizationEnergy: 10.360
  },
  "Cl": {
    name: "Chlorine",
    symbol: "Cl",
    atomicNumber: 17,
    atomicMass: 35.45,
    category: "Halogen",
    color: "#1FF01F",
    electronConfiguration: "[Ne] 3s² 3p⁵",
    electronegativity: 3.16,
    ionizationEnergy: 12.968
  },
  "K": {
    name: "Potassium",
    symbol: "K",
    atomicNumber: 19,
    atomicMass: 39.098,
    category: "Alkali Metal",
    color: "#8F40D4",
    electronConfiguration: "[Ar] 4s¹",
    electronegativity: 0.82,
    ionizationEnergy: 4.341
  },
  "Ca": {
    name: "Calcium",
    symbol: "Ca",
    atomicNumber: 20,
    atomicMass: 40.078,
    category: "Alkaline Earth Metal",
    color: "#3DFF00",
    electronConfiguration: "[Ar] 4s²",
    electronegativity: 1.00,
    ionizationEnergy: 6.113
  },
  "Ti": {
    name: "Titanium",
    symbol: "Ti",
    atomicNumber: 22,
    atomicMass: 47.867,
    category: "Transition Metal",
    color: "#BFC2C7",
    electronConfiguration: "[Ar] 3d² 4s²",
    electronegativity: 1.54,
    ionizationEnergy: 6.828
  },
  "Cr": {
    name: "Chromium",
    symbol: "Cr",
    atomicNumber: 24,
    atomicMass: 51.996,
    category: "Transition Metal",
    color: "#8A99C7",
    electronConfiguration: "[Ar] 3d⁵ 4s¹",
    electronegativity: 1.66,
    ionizationEnergy: 6.767
  },
  "Mn": {
    name: "Manganese",
    symbol: "Mn",
    atomicNumber: 25,
    atomicMass: 54.938,
    category: "Transition Metal",
    color: "#9C7AC7",
    electronConfiguration: "[Ar] 3d⁵ 4s²",
    electronegativity: 1.55,
    ionizationEnergy: 7.434
  },
  "Fe": {
    name: "Iron",
    symbol: "Fe",
    atomicNumber: 26,
    atomicMass: 55.845,
    category: "Transition Metal",
    color: "#E06633",
    electronConfiguration: "[Ar] 3d⁶ 4s²",
    electronegativity: 1.83,
    ionizationEnergy: 7.902
  },
  "Co": {
    name: "Cobalt",
    symbol: "Co",
    atomicNumber: 27,
    atomicMass: 58.933,
    category: "Transition Metal",
    color: "#F090A0",
    electronConfiguration: "[Ar] 3d⁷ 4s²",
    electronegativity: 1.88,
    ionizationEnergy: 7.881
  },
  "Ni": {
    name: "Nickel",
    symbol: "Ni",
    atomicNumber: 28,
    atomicMass: 58.693,
    category: "Transition Metal",
    color: "#50D050",
    electronConfiguration: "[Ar] 3d⁸ 4s²",
    electronegativity: 1.91,
    ionizationEnergy: 7.640
  },
  "Cu": {
    name: "Copper",
    symbol: "Cu",
    atomicNumber: 29,
    atomicMass: 63.546,
    category: "Transition Metal",
    color: "#C88033",
    electronConfiguration: "[Ar] 3d¹⁰ 4s¹",
    electronegativity: 1.90,
    ionizationEnergy: 7.726
  },
  "Zn": {
    name: "Zinc",
    symbol: "Zn",
    atomicNumber: 30,
    atomicMass: 65.38,
    category: "Transition Metal",
    color: "#7D80B0",
    electronConfiguration: "[Ar] 3d¹⁰ 4s²",
    electronegativity: 1.65,
    ionizationEnergy: 9.394
  },
  "Ga": {
    name: "Gallium",
    symbol: "Ga",
    atomicNumber: 31,
    atomicMass: 69.723,
    category: "Post-Transition Metal",
    color: "#C28F8F",
    electronConfiguration: "[Ar] 3d¹⁰ 4s² 4p¹",
    electronegativity: 1.81,
    ionizationEnergy: 5.999
  },
  "Ge": {
    name: "Germanium",
    symbol: "Ge",
    atomicNumber: 32,
    atomicMass: 72.630,
    category: "Metalloid",
    color: "#668F8F",
    electronConfiguration: "[Ar] 3d¹⁰ 4s² 4p²",
    electronegativity: 2.01,
    ionizationEnergy: 7.900
  },
  "As": {
    name: "Arsenic",
    symbol: "As",
    atomicNumber: 33,
    atomicMass: 74.922,
    category: "Metalloid",
    color: "#BD80E3",
    electronConfiguration: "[Ar] 3d¹⁰ 4s² 4p³",
    electronegativity: 2.18,
    ionizationEnergy: 9.815
  },
  "Se": {
    name: "Selenium",
    symbol: "Se",
    atomicNumber: 34,
    atomicMass: 78.971,
    category: "Nonmetal",
    color: "#FFA100",
    electronConfiguration: "[Ar] 3d¹⁰ 4s² 4p⁴",
    electronegativity: 2.55,
    ionizationEnergy: 9.752
  },
  "Rb": {
    name: "Rubidium",
    symbol: "Rb",
    atomicNumber: 37,
    atomicMass: 85.468,
    category: "Alkali Metal",
    color: "#702EB0",
    electronConfiguration: "[Kr] 5s¹",
    electronegativity: 0.82,
    ionizationEnergy: 4.177
  },
  "Sr": {
    name: "Strontium",
    symbol: "Sr",
    atomicNumber: 38,
    atomicMass: 87.62,
    category: "Alkaline Earth Metal",
    color: "#00FF00",
    electronConfiguration: "[Kr] 5s²",
    electronegativity: 0.95,
    ionizationEnergy: 5.695
  },
  "Zr": {
    name: "Zirconium",
    symbol: "Zr",
    atomicNumber: 40,
    atomicMass: 91.224,
    category: "Transition Metal",
    color: "#94E0E0",
    electronConfiguration: "[Kr] 4d² 5s²",
    electronegativity: 1.33,
    ionizationEnergy: 6.634
  },
  "Nb": {
    name: "Niobium",
    symbol: "Nb",
    atomicNumber: 41,
    atomicMass: 92.906,
    category: "Transition Metal",
    color: "#73C2C9",
    electronConfiguration: "[Kr] 4d⁴ 5s¹",
    electronegativity: 1.6,
    ionizationEnergy: 6.759
  },
  "Mo": {
    name: "Molybdenum",
    symbol: "Mo",
    atomicNumber: 42,
    atomicMass: 95.95,
    category: "Transition Metal",
    color: "#54B5B5",
    electronConfiguration: "[Kr] 4d⁵ 5s¹",
    electronegativity: 2.16,
    ionizationEnergy: 7.092
  },
  "Tc": {
    name: "Technetium",
    symbol: "Tc",
    atomicNumber: 43,
    atomicMass: 98,
    category: "Transition Metal",
    color: "#3B9E9E",
    electronConfiguration: "[Kr] 4d⁵ 5s²",
    electronegativity: 1.9,
    ionizationEnergy: 7.28
  },
  "Ru": {
    name: "Ruthenium",
    symbol: "Ru",
    atomicNumber: 44,
    atomicMass: 101.07,
    category: "Transition Metal",
    color: "#248F8F",
    electronConfiguration: "[Kr] 4d⁷ 5s¹",
    electronegativity: 2.2,
    ionizationEnergy: 7.36
  },
  "Rh": {
    name: "Rhodium",
    symbol: "Rh",
    atomicNumber: 45,
    atomicMass: 102.91,
    category: "Transition Metal",
    color: "#0A7D8C",
    electronConfiguration: "[Kr] 4d⁸ 5s¹",
    electronegativity: 2.28,
    ionizationEnergy: 7.459
  },
  "Pd": {
    name: "Palladium",
    symbol: "Pd",
    atomicNumber: 46,
    atomicMass: 106.42,
    category: "Transition Metal",
    color: "#006985",
    electronConfiguration: "[Kr] 4d¹⁰",
    electronegativity: 2.2,
    ionizationEnergy: 8.337
  },
  "Ag": {
    name: "Silver",
    symbol: "Ag",
    atomicNumber: 47,
    atomicMass: 107.87,
    category: "Transition Metal",
    color: "#C0C0C0",
    electronConfiguration: "[Kr] 4d¹⁰ 5s¹",
    electronegativity: 1.93,
    ionizationEnergy: 7.576
  },
  "In": {
    name: "Indium",
    symbol: "In",
    atomicNumber: 49,
    atomicMass: 114.82,
    category: "Post-Transition Metal",
    color: "#A67573",
    electronConfiguration: "[Kr] 4d¹⁰ 5s² 5p¹",
    electronegativity: 1.78,
    ionizationEnergy: 5.786
  },
  "Sn": {
    name: "Tin",
    symbol: "Sn",
    atomicNumber: 50,
    atomicMass: 118.71,
    category: "Post-Transition Metal",
    color: "#668080",
    electronConfiguration: "[Kr] 4d¹⁰ 5s² 5p²",
    electronegativity: 1.96,
    ionizationEnergy: 7.344
  },
  "Sb": {
    name: "Antimony",
    symbol: "Sb",
    atomicNumber: 51,
    atomicMass: 121.76,
    category: "Metalloid",
    color: "#9E63B5",
    electronConfiguration: "[Kr] 4d¹⁰ 5s² 5p³",
    electronegativity: 2.05,
    ionizationEnergy: 8.64
  },
  "Te": {
    name: "Tellurium",
    symbol: "Te",
    atomicNumber: 52,
    atomicMass: 127.60,
    category: "Metalloid",
    color: "#D47A00",
    electronConfiguration: "[Kr] 4d¹⁰ 5s² 5p⁴",
    electronegativity: 2.1,
    ionizationEnergy: 9.01
  },
  "Ba": {
    name: "Barium",
    symbol: "Ba",
    atomicNumber: 56,
    atomicMass: 137.33,
    category: "Alkaline Earth Metal",
    color: "#00C900",
    electronConfiguration: "[Xe] 6s²",
    electronegativity: 0.89,
    ionizationEnergy: 5.212
  },
  "La": {
    name: "Lanthanum",
    symbol: "La",
    atomicNumber: 57,
    atomicMass: 138.91,
    category: "Lanthanide",
    color: "#70D4FF",
    electronConfiguration: "[Xe] 5d¹ 6s²",
    electronegativity: 1.1,
    ionizationEnergy: 5.577
  },
  "Ce": {
    name: "Cerium",
    symbol: "Ce",
    atomicNumber: 58,
    atomicMass: 140.12,
    category: "Lanthanide",
    color: "#FFFFC7",
    electronConfiguration: "[Xe] 4f¹ 5d¹ 6s²",
    electronegativity: 1.12,
    ionizationEnergy: 5.539
  },
  "Gd": {
    name: "Gadolinium",
    symbol: "Gd",
    atomicNumber: 64,
    atomicMass: 157.25,
    category: "Lanthanide",
    color: "#45FEDE",
    electronConfiguration: "[Xe] 4f⁷ 5d¹ 6s²",
    electronegativity: 1.2,
    ionizationEnergy: 6.15
  },
  "Hf": {
    name: "Hafnium",
    symbol: "Hf",
    atomicNumber: 72,
    atomicMass: 178.49,
    category: "Transition Metal",
    color: "#4DC2FF",
    electronConfiguration: "[Xe] 4f¹⁴ 5d² 6s²",
    electronegativity: 1.3,
    ionizationEnergy: 6.825
  },
  "Bi": {
    name: "Bismuth",
    symbol: "Bi",
    atomicNumber: 83,
    atomicMass: 208.98,
    category: "Post-Transition Metal",
    color: "#9E4FB5",
    electronConfiguration: "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p³",
    electronegativity: 2.02,
    ionizationEnergy: 7.289
  },
  "Pb": {
    name: "Lead",
    symbol: "Pb",
    atomicNumber: 82,
    atomicMass: 207.2,
    category: "Post-Transition Metal",
    color: "#575961",
    electronConfiguration: "[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p²",
    electronegativity: 2.33,
    ionizationEnergy: 7.417
  }
};

/**
 * Get element data by symbol
 * 
 * @param symbol - Element symbol (e.g., "Fe")
 * @returns Element data or a default object if not found
 */
export function getElementData(symbol: string): ElementProperties {
  // Basic default element data if not found
  const defaultElement: ElementProperties = {
    name: "Unknown",
    symbol: symbol,
    atomicNumber: 0,
    atomicMass: 0,
    category: "Unknown",
    color: "#CCCCCC",
    electronConfiguration: "Unknown"
  };
  
  return elementData[symbol] || defaultElement;
}

/**
 * Get color for an element
 * 
 * @param symbol - Element symbol (e.g., "Fe")
 * @returns Hex color string
 */
export function getElementColor(symbol: string): string {
  return getElementData(symbol).color;
}

/**
 * Get a readable description of an element
 * 
 * @param symbol - Element symbol (e.g., "Fe")
 * @returns Formatted description
 */
export function getElementDescription(symbol: string): string {
  const element = getElementData(symbol);
  return `${element.name} (${element.symbol}, Z=${element.atomicNumber})
Atomic Mass: ${element.atomicMass} u
Category: ${element.category}
Electron Config: ${element.electronConfiguration}
${element.electronegativity ? `Electronegativity: ${element.electronegativity}` : ''}`;
}