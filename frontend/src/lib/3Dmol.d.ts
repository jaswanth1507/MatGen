// Type definitions for 3Dmol.js
declare global {
    interface Window {
      $3Dmol: {
        createViewer: (element: HTMLElement, options: any) => Viewer3D;
      };
    }
  }
  
  // Basic viewer interface
  interface Viewer3D {
    addModel: (data: string, format: string) => void;
    setStyle: (selector: any, style: any) => void;
    setHoverDuration: (duration: number) => void;
    setHover: (options: any) => void;
    addClickListener: (callback: (atom: Atom, viewer: Viewer3D, event: Event, container: HTMLElement) => void) => void;
    zoomTo: () => void;
    setView: (view: number[]) => void;
    render: () => void;
    clear: () => void;
    setBackgroundColor: (color: string) => void;
    addUnitCell: () => void;
    addLabels: (selector: any, options: any) => void;
    getModel: () => Model3D;
  }
  
  interface Model3D {
    selectedAtoms: (selector: any) => Atom[];
  }
  
  interface Atom {
    elem: string;
    serial: number;
    x: number;
    y: number;
    z: number;
  }
  
  export {};