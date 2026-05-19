import numpy as np
from node import Node
from element import Element, TrussElement
from loads import NodeLoad, DistLoad

class Structure:
    """
    Zentraler Datenbehälter: sammelt Knoten, Elemente und Lasten,
    vergibt DOF-Indizes und assembliert die globale Steifigkeitsmatrix.
    """
    def __init__(self):
        self.nodes = []
        self.elements = []
        self.loads = []
        self._n_dof = 0 # laufender DOF-Zähler
    
    # ------------------------------------------------------------------ #
    #  Knoten und Elemente hinzufügen                                      #
    # ------------------------------------------------------------------ #
    
    def add_node(self, x: float, z: float, kind: str = "frame", support: dict = None)  -> Node:
        """
        Erstellt einen Knoten, vergibt sofort seine dof_indices
        und fügt ihn der Struktur hinzu.
        """
        new_node = Node(
            id=len(self.nodes), 
            x=x, 
            z=z, 
            kind=kind, 
            support=support)
        
        # DOF-Indizes vergeben
        new_node.dof_indices = list(range(self._n_dof, self._n_dof + new_node.n_dof))
        self._n_dof += new_node.n_dof
        
        self.nodes.append(new_node)
        
        return new_node

        
        
    def add_element(self, node_i: Node, node_j: Node, E: float, A: float, I: float = 0.0) -> Element:
        """
        Erstellt ein Element und fügt es der Struktur hinzu.
        Für Fachwerk: I weglassen (default 0) → TrussElement.
        Für Rahmen:   I angeben             → Element.
        """
        if node_i.kind == "truss" and node_i.kind == "truss":
            new_element = TrussElement(
                id=len(self.elements),
                node_i=node_i,
                node_j=node_j,
                E=E,
                A=A,
            )
        else:
            new_element = Element(
                id=len(self.elements),
                node_i=node_i,
                node_j=node_j,
                E=E,
                A=A,
                I=I,
            )
            
        self.elements.append(new_element)
        
        return new_element
    
    # Generelles Lastobjekt
    def add_load(self, load) -> None:
        self.loads.append(load)
    
    # Knotenlast
    def add_node_load(self, node: Node, Fx: float = 0.0, Fz: float = 0.0, M: float = 0.0) -> None:
        self.add_load(NodeLoad(node, Fx=Fx, Fz=Fz, M=M))
    
    # Konstante Streckenlast
    def add_dist_load(self, element: Element, qx: float = 0.0, qz: float = 0.0, local: bool = True) -> None:
        self.add_load(DistLoad(element, qx=qx, qz=qz, local=local))
    # ------------------------------------------------------------------ #
    #  Assemblierung                                                       #
    # ------------------------------------------------------------------ #
    def assemble_K(self) -> np.ndarray:
        """
        Assembliert die globale Steifigkeitsmatrix K (n_dof × n_dof) für Theorie I.O..
        Trägt für jedes Element k_global an den richtigen
        Zeilen/Spalten gemäß dof_indices ein.
        """
        K = np.zeros((self._n_dof, self._n_dof))
        
        for elem in self.elements:
            idx = elem.dof_indices          # z.B. [0,1,2, 3,4,5]
            kg  = elem.k_global             # 6×6 oder 4×4

            for i_local, i_global in enumerate(idx):
                for j_local, j_global in enumerate(idx):
                    K[i_global, j_global] += kg[i_local, j_local]

        return K
        
    def assemble_Kg(self, results) -> np.ndarray:
        """
        Assembliert die globale geometrische Steifigkeitsmatrix Kg.
        results: Results-Objekt aus dem vorherigen Iterationsschritt,
                liefert die Normalkräfte N pro Element.
        """
        Kg = np.zeros((self._n_dof, self._n_dof))

        for elem in self.elements:
            N   = results.internal_forces(elem)["N_i"]  # Normalkraft aus Th1
            idx = elem.dof_indices
            kg  = elem.kg_global(N)

            for i_local, i_global in enumerate(idx):
                for j_local, j_global in enumerate(idx):
                    Kg[i_global, j_global] += kg[i_local, j_local]

        return Kg
        
    
    def assemble_f(self) -> np.ndarray:
        """
        Assembliert den globalen Lastvektor f (n_dof,).
        Knotenlasten werden direkt eingetragen,
        Streckenlasten über Festeinspanngrößen umgerechnet.
        """
        f = np.zeros(self._n_dof)
        
        for load in self.loads:
            load.assemble_into(f)

        return f
    
    # ------------------------------------------------------------------ #
    #  Randbedingungen                                                     #
    # ------------------------------------------------------------------ #
    def get_free_dofs(self) -> list:
        """Alle freien (ungefesselten) globalen DOF-Indizes."""
        free = []
        for node in self.nodes:
            free.extend(node.free_dof_indices)
        return free

    def get_fixed_dofs(self) -> list:
        """Alle gesperrten globalen DOF-Indizes."""
        fixed = []
        for node in self.nodes:
            fixed.extend(node.fixed_dof_indices)
        return fixed
    
    # ------------------------------------------------------------------ #
    #  Darstellung                                                         #
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:
        return (f"Structure("
                f"{len(self.nodes)} Knoten, "
                f"{len(self.elements)} Elemente, "
                f"{self._n_dof} DOFs)")