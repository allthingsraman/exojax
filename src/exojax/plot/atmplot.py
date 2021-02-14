import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plotdtauM(nus,dtauM,Tarr=None,Parr=None,unit=None):
    """plot dtauM

    Args:
       nus: wavenumber
       dtauM: dtau matrix
       Tarr: temperature profile
       Parr: perssure profile 
       unit: x-axis unit = um (wavelength microns), nm  = (wavelength nm), AA  = (wavelength Angstrom), else (wavenumber cm)

    """
    fig=plt.figure(figsize=(20,3))
    ax=plt.subplot2grid((1, 20), (0, 3),colspan=18)
    if unit=="um":
        c=ax.imshow(np.log10(dtauM[:,::-1]),vmin=-3,vmax=3,cmap="RdYlBu_r",alpha=0.9,extent=[1.e4/nus[-1],1.e4/nus[0],np.log10(Parr[-1]),np.log10(Parr[0])])
        plt.xlabel("wavelength (um)")
    elif unit=="nm":
        c=ax.imshow(np.log10(dtauM[:,::-1]),vmin=-3,vmax=3,cmap="RdYlBu_r",alpha=0.9,extent=[1.e7/nus[-1],1.e7/nus[0],np.log10(Parr[-1]),np.log10(Parr[0])])
        plt.xlabel("wavelength (um)")
    elif unit=="AA":
        c=ax.imshow(np.log10(dtauM[:,::-1]),vmin=-3,vmax=3,cmap="RdYlBu_r",alpha=0.9,extent=[1.e8/nus[-1],1.e8/nus[0],np.log10(Parr[-1]),np.log10(Parr[0])])
        plt.xlabel("wavelength (um)")
    else:
        c=ax.imshow(np.log10(dtauM),vmin=-3,vmax=3,cmap="RdYlBu_r",alpha=0.9\
           ,extent=[nus[0],nus[-1],np.log10(Parr[-1]),np.log10(Parr[0])])
        plt.xlabel("wavenumber ($cm^{-1}$)")
        
    plt.colorbar(c,shrink=0.8)
    plt.ylabel("log10 (P (bar))")
    ax.set_aspect(0.2/ax.get_data_ratio())
    if Tarr is not None and Parr is not None:
        ax=plt.subplot2grid((1, 20), (0, 0),colspan=2)
        plt.plot(Tarr,np.log10(Parr),color="gray")
        plt.xlabel("temperature (K)")
        plt.ylabel("log10 (P (bar))")
        plt.gca().invert_yaxis()
        plt.ylim(np.log10(Parr[-1]),np.log10(Parr[0]))
        ax.set_aspect(1.45/ax.get_data_ratio())