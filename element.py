import numpy as np
from node import Node

class Element:
    """
    Euler-Bernoulli-Balkenelement für den ebenen Rahmen (6 DOF).

    DOF-Reihenfolge lokal:  [u_i, w_i, phi_i, u_j, w_j, phi_j]
    DOF-Reihenfolge global: gemäß node_i.dof_indices + node_j.dof_indices

    Parameters
    ----------
    id     : eindeutige Elementnummer
    node_i : Anfangsknoten
    node_j : Endknoten
    E      : Elastizitätsmodul [kN/m²]
    A      : Querschnittsfläche [m²]
    I      : Flächenträgheitsmoment [m⁴]
    """
    
    def __init__(self, id: int, node_i: Node, node_j: Node, E: float, A: float, I: float):
        # greift direkt auf die Node-Objekte zu 
        self.id = id
        self.node_i = node_i
        self.node_j = node_j
        self.E = E
        self.A = A
        self.I = I
        self.f_cl = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) # Volleinspannschnittgrüßen initialisieren
    
    @property
    def L(self) -> float:
        """Stablänge [m]"""
        delta =  self.node_j.coords - self.node_i.coords
        return float(np.linalg.norm(delta))
    
    @property
    def angle(self) -> float:
        """
        Neigungswinkel alpha gegen den Uhrzeigersinn [rad].
        Globales KOS: x nach rechts, z nach unten.
        """
        delta = self.node_j.coords - self.node_i.coords
        return float(np.arctan2(-delta[1], delta[0]))
    
    # ------------------------------------------------------------------ #
    #  Transformationsmatrix                                               #
    # ------------------------------------------------------------------ #
    
    @property
    def T(self) -> np.ndarray:
        """
        Transformationsmatrix 6×6: lokal → global.
        """
        c = np.cos(self.angle)
        s = np.sin(self.angle)

        t = np.array([
            [ c, -s,  0],
            [ s,  c,  0],
            [ 0,  0,  1],
        ])

        T = np.zeros((6, 6))
        T[0:3, 0:3] = t
        T[3:6, 3:6] = t
        return T
    
    # ------------------------------------------------------------------ #
    #  Steifigkeitsmatrizen                                                #
    # ------------------------------------------------------------------ #
    
    @property
    def k_local(self) -> np.ndarray:
        """
        Lokale Elementsteifigkeitsmatrix 6×6 (Euler-Bernoulli, Th.I.O.).
        DOF-Reihenfolge: [u_i, w_i, phi_i, u_j, w_j, phi_j]
        """
        E, A, I, L = self.E, self.A, self.I, self.L
        # Vorfaktoren
        EA_L  = E * A / L
        EI_L3 = E * I / L**3
        EI_L2 = E * I / L**2
        EI_L  = E * I / L
        
        k = np.array([
            [ EA_L,         0,        0, -EA_L,         0,        0],
            [    0,  12*EI_L3, -6*EI_L2,     0, -12*EI_L3, -6*EI_L2],
            [    0,  -6*EI_L2,   4*EI_L,     0,   6*EI_L2,   2*EI_L],
            [-EA_L,         0,        0,  EA_L,         0,        0],
            [    0, -12*EI_L3,  6*EI_L2,     0,  12*EI_L3,  6*EI_L2],
            [    0,  -6*EI_L2,   2*EI_L,     0,   6*EI_L2,   4*EI_L],
        ])
        
        return k
    
    
    def kg_local(self, N: float) -> np.ndarray:
        """
        Geometrische Steifigkeitsmatrix 6×6 im lokalen KOS.
        N: Normalkraft im Stab (Zug positiv)
        """
        L = self.L
        kg = np.zeros((6, 6))

        # Nur Querkraftanteile – Normalkraftanteile entfallen bei Euler-Bernoulli
        c = N / L
        kg[1, 1] =  6/5   * c;   kg[1, 2] = -L/10   * c
        kg[1, 4] = -6/5   * c;   kg[1, 5] = -L/10   * c

        kg[2, 1] = -L/10  * c;   kg[2, 2] =  2*L**2/15 * c
        kg[2, 4] =  L/10  * c;   kg[2, 5] = -L**2/30   * c

        kg[4, 1] = -6/5   * c;   kg[4, 2] =  L/10   * c
        kg[4, 4] =  6/5   * c;   kg[4, 5] =  L/10   * c

        kg[5, 1] = -L/10  * c;   kg[5, 2] = -L**2/30   * c
        kg[5, 4] =  L/10  * c;   kg[5, 5] =  2*L**2/15 * c

        return kg
    
    # @property
    # def k_local_TH2(self) -> np.ndarray:
    #     """
    #     Lokale exakte Elementsteifigkeitsmatrix (Th.II.O.).
    #     Entommen aus Vorlesung  Stability Theory (Formelsammlung)
    #     Unterscheidung zwischen Zug und Druck
    #     DOF-Reihenfolge: [u_i, w_i, phi_i, u_j, w_j, phi_j]
    #     """
    #     E, A, I, L = self.E, self.A, self.I, self.L
    #     # Normalkraft im Stab
    #     N = self.N
    #     # Vorfaktoren
    #     EA_L  = E * A / L
    #     EI_L3 = E * I / L**3
    #     EI_L2 = E * I / L**2
    #     EI_L  = E * I / L
        
    #     if N == 0.0: 
    #         # lokale Elementsteifigkeitsmatrix gemäß Th.I.O.
    #         k = np.array([
    #         [ EA_L,         0,        0, -EA_L,         0,        0],
    #         [    0,  12*EI_L3, -6*EI_L2,     0, -12*EI_L3, -6*EI_L2],
    #         [    0,  -6*EI_L2,   4*EI_L,     0,   6*EI_L2,   2*EI_L],
    #         [-EA_L,         0,        0,  EA_L,         0,        0],
    #         [    0, -12*EI_L3,  6*EI_L2,     0,  12*EI_L3,  6*EI_L2],
    #         [    0,  -6*EI_L2,   2*EI_L,     0,   6*EI_L2,   4*EI_L],
    #         ])
            
    #         return k
        
    #     # Druck im Element
    #     elif N < 0: 
    #         eps = L * np.sqrt(abs(N)/(E*I))
    #         # Strichwerte 
    #         A_strich = (eps*(np.sin(eps)-eps*np.cos(eps)))/(2*(1-np.cos(eps))-eps*np.sin(eps))
    #         B_strich = (eps*(eps-np.sin(eps)))/(2*(1-np.cos(eps))-eps*np.sin(eps))
    #         D_strich = eps**2
    #         # Help variable for cross-terms
    #         AB_sum = A_strich + B_strich
    #         # lokale Elementsteifigkeitsmatrix gemäß Th.II.O.
    #         k = np.array([
    #             [ EA_L,                            0,                 0,    -EA_L,                            0,             0],
    #             [ 0,     (2*AB_sum - D_strich)*EI_L3,     -AB_sum*EI_L2,        0, -(2*AB_sum - D_strich)*EI_L3, -AB_sum*EI_L2],
    #             [ 0,                   -AB_sum*EI_L2,     A_strich*EI_L,        0,                 AB_sum*EI_L2, B_strich*EI_L],
    #             [-EA_L,                            0,                 0,     EA_L,                            0,             0],
    #             [ 0,    -(2*AB_sum - D_strich)*EI_L3,      AB_sum*EI_L2,        0,  (2*AB_sum - D_strich)*EI_L3,  AB_sum*EI_L2],
    #             [ 0,                   -AB_sum*EI_L2,     B_strich*EI_L,        0,                 AB_sum*EI_L2, A_strich*EI_L]
    #         ])
    #         return k
        
    #     # Zug im Element
    #     else:
    #         eps = L * np.sqrt(N/(E*I))
    #         denom = 2 * (np.cosh(eps) - 1) - eps * np.sinh(eps)
    #         A_strich = (eps * (np.sinh(eps) - eps * np.cosh(eps))) / denom
    #         B_strich = (eps * (eps - np.sinh(eps))) / denom
    #         D_strich = eps**2 
    #         # Help variable for cross-terms
    #         AB_sum = A_strich + B_strich
    #         # lokale Elementsteifigkeitsmatrix gemäß Th.II.O.
    #         k = np.array([
    #             [ EA_L,                            0,                 0,    -EA_L,                            0,             0],
    #             [ 0,     (2*AB_sum + D_strich)*EI_L3,     -AB_sum*EI_L2,        0, -(2*AB_sum + D_strich)*EI_L3, -AB_sum*EI_L2],
    #             [ 0,                   -AB_sum*EI_L2,     A_strich*EI_L,        0,                 AB_sum*EI_L2, B_strich*EI_L],
    #             [-EA_L,                            0,                 0,     EA_L,                            0,             0],
    #             [ 0,    -(2*AB_sum + D_strich)*EI_L3,      AB_sum*EI_L2,        0,  (2*AB_sum + D_strich)*EI_L3,  AB_sum*EI_L2],
    #             [ 0,                   -AB_sum*EI_L2,     B_strich*EI_L,        0,                 AB_sum*EI_L2, A_strich*EI_L]
    #         ])

    #         return k
    
    
    @property 
    def k_global(self) -> np.ndarray:
        """
        Globale Elementsteifigkeitsmatrix 6×6 nach Th.I.O.
        k_global = Tᵀ · k_local · T
        """
        T = self.T
        return T.T @ self.k_local @ T
    
    
    def kg_global(self, N: float) -> np.ndarray:
        """
        Geometrische Steifigkeitsmatrix 6×6 im globalen KOS.
        """
        T = self.T
        return T.T @ self.kg_local(N) @ T
    
    # @property 
    # def k_global_TH2(self) -> np.ndarray:
    #     """
    #     Globale Elementsteifigkeitsmatrix 6×6 nach Th.II.O.
    #     k_global = Tᵀ · k_local · T
    #     """
    #     T = self.T
    #     return T.T @ self.k_local_TH2 @ T
        
        
    # ------------------------------------------------------------------ #
    #  DOF-Zuordnung                                                       #
    # ------------------------------------------------------------------ #

    @property
    def dof_indices(self) -> list:
        """
        Globale DOF-Indizes dieses Elements – bestimmen die
        Zeilen und Spalten beim Eintragen in die Gesamtsteifigkeitsmatrix K.
        """
        return self.node_i.dof_indices + self.node_j.dof_indices

    # ------------------------------------------------------------------ #
    #  Darstellung                                                         #
    # ------------------------------------------------------------------ #
    
    def __repr__(self) -> str:
        return (f"Element(id={self.id}, "
                f"node_i={self.node_i.id}, node_j={self.node_j.id}, "
                f"L={self.L:.3f}m, alpha={np.degrees(self.angle):.1f}°)")

# TODO: Noch die __repr__ von TrussElement abändern, damit TrussElement(id=...) als return kommt
class TrussElement(Element):
    """
    Fachwerkstab: nur Normalkraftanteil, keine Biegung.
    Erbt Geometrie und Transformation von Element,
    überschreibt nur k_local (4×4) und T (4×4).
    """

    def __init__(self, id: int, node_i: Node, node_j: Node,
                 E: float, A: float):
        # I=0 wird nicht gebraucht, trotzdem Elternklasse aufrufen
        super().__init__(id, node_i, node_j, E=E, A=A, I=0.0)

    @property
    def T(self) -> np.ndarray:
        """Transformationsmatrix 4×4 für 2-DOF-Knoten."""
        c = np.cos(self.angle)
        s = np.sin(self.angle)

        t = np.array([
            [c, -s],
            [s,  c],
        ])

        T = np.zeros((4, 4))
        T[0:2, 0:2] = t
        T[2:4, 2:4] = t
        return T

    @property
    def k_local(self) -> np.ndarray:
        """Lokale Steifigkeitsmatrix 4×4: nur EA/L-Anteile."""
        EA_L = self.E * self.A / self.L

        return np.array([
            [ EA_L,  0, -EA_L,  0],
            [    0,  0,     0,  0],
            [-EA_L,  0,  EA_L,  0],
            [    0,  0,     0,  0],
        ])
        
