# approximately resembles an IPE 200 
E = 210e6 # kN/m2 
A = 3e-3 # m2
I = 1.94e-5 # m4
h = 0.2  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# approximately resembles an IPE 160 
E = 210e6 # kN/m2 
A = 2.0e-3 # m2
I = 0.869e-5 # m4
h = 0.16  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# approximately resembles an IPE 140 
E = 210e6 # kN/m2 
A = 1.6e-3 # m2
I = 0.54e-5 # m4
h = 0.14  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# approximately resembles an IPE 120
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.318e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# Deprecated modified IPE 120 -> eta Option 1 = 100% for Th.II.O. (Design Option 1)
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.3093e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # m_k in kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# Deprecated modified IPE 120 -> eta = 100% for Th.I.O.
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.2740555e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * 1.14 # kNm

# modified IPE 120 -> eta = 100% for linear hyperplane
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 2.7784576742780014e-06 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * 1.14 # kNm

# approximately resembles an IPE 100
E = 210e6 # kN/m2 
A = 1.032e-3 # m2
I = 0.17e-5 # m4
h = 0.10  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.15
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm

# modified IPE 100 (half frame)
E = 210e6 # kN/m2 
A = 1.032e-3 # m2
I = 0.157e-5 # m4
h = 0.10  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.15
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm