"""
Summary
----------
Functions for radial velocity curves, JAX autograd/jit compatible.

"""
import jax
from jax.lax import map
import jax.numpy as jnp
from jax import jit
import numpy as np
import sys
from exojax.dynamics import getE

@jit
def rvf(t,T0,P,e,omegaA,Ksini,Vsys):
    """
    Summary
    ----------
    Unit-free radial velocity curve for SB1

    Parameters
    ----------
    t : ndarray 
        Time in your time unit
    T0 : float 
         Time of periastron passage in your time unit
    P : float 
        orbital period in your time unit
    e : float 
        eccentricity
    omegaA : float 
             argument of periastron
    Ksini : float 
            RV semi-amplitude in your velocity unit
    Vsys : float 
           systemic velocity in your velocity unit

    Returns
    ------------
    model : ndarray
            radial velocity curve in your velocity unit

    """

    n=2*jnp.pi/P
    M=n*(t-T0)

    Ea=map(lambda x: getE.getE(x, e), M)
    cosE=jnp.cos(Ea)
    cosf=(-cosE + e)/(-1 + cosE*e)
    sinf=jnp.sqrt((-1 + cosE*cosE)*(-1 + e*e))/(-1 + cosE*e)
    sinf=jnp.where(Ea<jnp.pi,-sinf,sinf)
        
    cosfpo=cosf*jnp.cos(omegaA)-sinf*jnp.sin(omegaA)
    face=1.0/jnp.sqrt(1.0-e*e)
    model = Ksini*face*(cosfpo+e*jnp.cos(omegaA)) + Vsys

    return model

def get_G_cuberoot():
    
    """
    Summary
    ----------
    This function computes cuberoot of Gravitaional constant (in the unit of [km/s]) normalized by day and Msun

    Parameters
    -----------

    Returns
    ----------
    Gcr_val: float
             cuberoot of Gravitaional constant (km/s) normalized by day and Msun

    """
    from astropy.constants import G
    from astropy.constants import M_sun
    from astropy import units as u
    day=24*3600*u.s
    Gu=(G*M_sun/day).value
    Gcr_val=Gu**(1.0/3.0)*1.e-3
    return Gcr_val


Gcr=get_G_cuberoot()
fac=(2.0*jnp.pi)**(1.0/3.0)
m23=-2.0/3.0
m13=-1.0/3.0



@jit
def rvcoref(t,T0,P,e,omegaA,K,i):
    """
    Summary
    --------
    Unit-free radial velocity curve w/o systemic velocity, in addition, i and K are separated. 

    Parameters
    -----------
    t: ndarray
       Time in your time unit
    T0: float
        Time of periastron passage in your time unit
    P: float 
       orbital period in your time unit
    e: float
       eccentricity
    omegaA: float
            argument of periastron
    K: float
       RV semi-amplitude/sin i in your velocity unit
    i: float
       inclination

    Returns
    ------------
    model : ndarray
            radial velocity curve in your velocity unit

    """
    n=2*jnp.pi/P
    M=n*(t-T0)

    Ea=map(lambda x: getE.getE(x, e), M)
    cosE=jnp.cos(Ea)
    cosf=(-cosE + e)/(-1 + cosE*e)
    sinf=jnp.sqrt((-1 + cosE*cosE)*(-1 + e*e))/(-1 + cosE*e)
    sinf=jnp.where(Ea<jnp.pi,-sinf,sinf)
        
    cosfpo=cosf*jnp.cos(omegaA)-sinf*jnp.sin(omegaA)
    face=1.0/jnp.sqrt(1.0-e*e)
    Ksini=K*jnp.sin(i)
    model = Ksini*face*(cosfpo+e*jnp.cos(omegaA))

    return model

@jit
def rvf2(t,T0,P,e,omegaA,M1,M2,i,Vsys):
    #RV of M1
    K=fac*Gcr*M2*((M1+M2)**m23)*(P**m13)/jnp.sqrt(1.0 - e*e)
    return rvcoref(t,T0,P,e,omegaA,K,i) + Vsys

@jit
def rvf2c(t,T0,P,e,omegaA,M1,M2,i,Vsys):
    #RV of M2 (companion)
    K=fac*Gcr*M1*((M1+M2)**m23)*(P**m13)/jnp.sqrt(1.0 - e*e)
    return -rvcoref(t,T0,P,e,omegaA,K,i) + Vsys

@jit
def rvf1(t,T0,P,e,omegaA,K,i,Vsys):
    return rvcoref(t,T0,P,e,omegaA,K,i) + Vsys


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    t=jnp.linspace(0,1.0,100)
    T0=0
    P=0.25
    e=0.85
    omegaA=np.pi
    K=3.0
    i=np.pi/2.0
    Vsys=1.0
    rv=rvf1(t,T0,P,e,omegaA,K,i,Vsys)
    plt.plot(t,rv,".")
    plt.plot(t,rv)
    plt.show()