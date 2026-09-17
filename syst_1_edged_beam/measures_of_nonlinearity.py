import numpy as np

def kappa_1(l_1k, l_1d, t_S):
    numerator = (t_S(l_1=l_1d, l_2=0) - t_S(l_1=l_1k, l_2=0)) * l_1k
    denominator = (t_S(l_1=l_1k, l_2=0) - t_S(l_1=0, l_2=0)) * (l_1d-l_1k)
    return numerator / denominator


def kappa_2(l_2k, l_2d, t_S):
    numerator = (t_S(l_1=0, l_2=l_2d) - t_S(l_1=0, l_2=l_2k)) * l_2k
    denominator = (t_S(l_1=0, l_2=l_2k) - t_S(l_1=0, l_2=0)) * (l_2d-l_2k)
    return numerator / denominator

def kappa_12(l_1k, l_1d, l_2k, l_2d, t_S):
    numerator = (t_S(l_1=l_1d, l_2=l_2d) - t_S(l_1=l_1k, l_2=l_2k)) * np.sqrt(l_1k**2 + l_2k**2)
    denominator = (t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)) * np.sqrt((l_1d-l_1k)**2 + (l_2d-l_2k)**2)
    return numerator / denominator

def r1(l_1k, l_2k, t_S):
    numerator = t_S(l_1=l_1k, l_2=0) - t_S(l_1=0, l_2=0)
    denominator = t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)
    return numerator / denominator

def r2(l_1k, l_2k, t_S):
    numerator = t_S(l_1=0, l_2=l_2k) - t_S(l_1=0, l_2=0)
    denominator = t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)
    return numerator / denominator