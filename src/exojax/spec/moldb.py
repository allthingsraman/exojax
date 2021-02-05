import numpy as np
from exojax.spec import hapi
__all__ = ['MdbHit']

class MdbHit(object):
    def __init__(self,datapath,molec,nurange=[-np.inf,np.inf],margin=100.0,crit=-np.inf):
        """Molecular database for HITRAN/HITEMP form

        Args: 
           datapath: 
           molec: 
           nurange: wavenumber range list (cm-1)
           margin: margin for nurange (cm-1)
           crit: line strength lower limit for extraction

        """
        hapi.db_begin(datapath)
        self.Tref=296.0
        self.molec = molec
        self.molecid = search_molecid(molec)
        self.crit = crit
        self.margin = margin
        self.nurange=[np.min(nurange),np.max(nurange)]
        self.nu_lines = hapi.getColumn(molec, 'nu')
        self.S_ij = hapi.getColumn(molec, 'sw')

        ### MASKING ###
        mask=(self.nu_lines>self.nurange[0]-self.margin)\
        *(self.nu_lines<self.nurange[1]+self.margin)\
        *(self.S_ij>self.crit)
        
        self.A = hapi.getColumn(molec, 'a')[mask]
        self.n_air = hapi.getColumn(molec, 'n_air')[mask]
        self.isoid = hapi.getColumn(molec,'local_iso_id')[mask]
        self.gamma_air = hapi.getColumn(molec, 'gamma_air')[mask]
        self.gamma_self = hapi.getColumn(molec, 'gamma_self')[mask]
        self.delta_air = hapi.getColumn(molec, 'delta_air')[mask]
        self.elower = hapi.getColumn(molec, 'elower')[mask]
        self.gpp = hapi.getColumn(molec, 'gpp')[mask]
        self.nu_lines = hapi.getColumn(molec, 'nu')[mask]
        self.S_ij = hapi.getColumn(molec, 'sw')[mask]
        
        self.logsij0=np.log(self.S_ij)
        self.uniqiso=np.unique(self.isoid)

    def Qr(self,Tarr):
        """Partition Function ratio using HAPI partition sum

        """
        allT=list(np.concatenate([[self.Tref],Tarr]))
        Qrx=[]
        for iso in self.uniqiso:
            Qrx.append(hapi.partitionSum(self.molecid,iso, allT))
        Qrx=np.array(Qrx)
        qr=Qrx[:,0]/Qrx[:,1:].T #Q(Tref)/Q(T)
        return qr


def search_molecid(molec):
    """molec id from tag of HITRAN/HITEMP

    Args:
       molec:

    """
    try:
        hitf=molec.split("_")
        if hitf[1]=="hit12":
            molecid=int(hitf[0])
            return molecid
    except:
        print("Warning: Define molecid by yourself.")
        return None
