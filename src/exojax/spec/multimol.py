import numpy as np
from exojax.spec import api
import os


class MultiMol():
    """multiple molecular database handler

        Notes:
            MultiMol provides an easy way to generate multiple mdb (multimdb) and multiple opa (multiopa) 
            for multiple molecules/wavenumber segements.
            
    """
    def __init__(self, molmulti, dbmulti, database_root_path=".database"):
        """initialization

        Args:
            molmulti (_type_): multiple simple molecule names [n_wavenumber_segments, n_molecules], such as [["H2O","CO"],["H2O"],["CO"]]
            dbmulti (_type_): multiple database names, such as [["HITEMP","EXOMOL"],["HITEMP","HITRAN12"]]],
            database_root_path (str, optional): _description_. Defaults to ".database".
        """
        self.molmulti = molmulti
        self.dbmulti = dbmulti
        self.database_root_path = database_root_path
        self.generate_database_directories()

    def generate_database_directories(self):
        """generate database directory array
        """
        dbpath_lookup = {
            "ExoMol": database_path_exomol,
            "HITRAN12": database_path_hitran12,
            "HITEMP": database_path_hitemp,
            "exomol": database_path_exomol,
            "hitran12": database_path_hitran12,
            "hitemp": database_path_hitemp
        }
        self.db_dirs = []
        for mol_k, db_k in zip(self.molmulti, self.dbmulti):
            db_dir_k = []
            for mol_i, db_i in zip(mol_k, db_k):
                if db_i not in dbpath_lookup:
                    raise ValueError(f"Unsupported database: {db_i}")

                dbpath_func = dbpath_lookup[db_i]
                dbpath = dbpath_func(mol_i)

                if dbpath is None:
                    raise ValueError("db_dirs not specified")

                db_dir_k.append(dbpath)

            self.db_dirs.append(db_dir_k)

    def multimdb(self, nu_grid_list, crit=0., Ttyp=1000.):
        """select current multimols from wavenumber grid

        Args:
            nu_grid_list (_type_): _description_
            crit (_type_, optional): _description_. Defaults to 0..
            Ttyp (_type_, optional): _description_. Defaults to 1000..

        Returns:
            lists of mdb: multi mdb
        """
        _multimdb = []
        self.masked_molmulti = self.molmulti[:]
        for k, mol in enumerate(self.molmulti):

            mdb_k = []
            mask = np.ones_like(mol, dtype=bool)

            for i, item in enumerate(mol):
                try:
                    if self.dbmulti[k][i] in ["ExoMol", "exomol"]:
                        mdb_k.append(
                            api.MdbExomol(os.path.join(self.database_root_path,
                                                       self.db_dirs[k][i]),
                                          nu_grid_list[k],
                                          crit=crit,
                                          Ttyp=Ttyp,
                                          gpu_transfer=False))
                    elif self.dbmulti[k][i] in ["HITRAN12", "hitran12"]:
                        mdb_k.append(
                            api.MdbHitran(os.path.join(self.database_root_path,
                                                       self.db_dirs[k][i]),
                                          nu_grid_list[k],
                                          crit=crit,
                                          Ttyp=Ttyp,
                                          gpu_transfer=False,
                                          isotope=1))
                    elif self.dbmulti[k][i] in ["HITEMP", "hitemp"]:
                        mdb_k.append(
                            api.MdbHitemp(os.path.join(self.database_root_path,
                                                       self.db_dirs[k][i]),
                                          nu_grid_list[k],
                                          crit=crit,
                                          Ttyp=Ttyp,
                                          gpu_transfer=False,
                                          isotope=1))
                except:
                    mask[i] = False

                self.masked_molmulti[k] = np.array(self.molmulti[k])[mask].tolist()
                _multimdb.append(mdb_k)
                
            return _multimdb

    def multiopa_premodit(self,
                          multimdb,
                          nu_grid_list,
                          auto_trange,
                          diffmode=2,
                          dit_grid_resolution=0.2):
        """multiple opa for PreMODIT

        Args:
            multimdb (): multimdb
            nu_grid_list (): wavenumber grid list
            auto_trange (optional): temperature range [Tl, Tu], in which line strength is within 1 % prescision. Defaults to None.
            diffmode (int, optional): _description_. Defaults to 2.
            dit_grid_resolution (float, optional): force to set broadening_parameter_resolution={mode:manual, value: dit_grid_resolution}), ignores broadening_parameter_resolution.
            
        Returns:
            _type_: _description_
        """
        from exojax.spec.opacalc import OpaPremodit
        multiopa = []
        for k in range(len(multimdb)):
            opa_k = []
            for i in range(len(multimdb[k])):
                opa_i = OpaPremodit(mdb=multimdb[k][i],
                                    nu_grid=nu_grid_list[k],
                                    diffmode=diffmode,
                                    auto_trange=auto_trange,
                                    dit_grid_resolution=dit_grid_resolution)
                opa_k.append(opa_i)
            multiopa.append(opa_k)

        return multiopa

    def multi_molmass(self):
        from exojax.spec import molinfo
        mols_unique = []
        mols_num = []
        for k in range(len(self.masked_molmulti)):
            mols_num_k = []
            for i in range(len(self.masked_molmulti[k])):
                if self.masked_molmulti[k][i] in mols_unique:
                    mols_num_k.append(mols_unique.index(self.masked_molmulti[k][i]))
                else:
                    mols_unique.append(self.masked_molmulti[k][i])
                    mols_num_k.append(mols_unique.index(self.masked_molmulti[k][i]))
            mols_num.append(mols_num_k)

        molmass = []
        for i in range(len(mols_unique)):
            print(mols_unique[i], molinfo.molmass(mols_unique[i]))
            molmass.append(molinfo.molmass(mols_unique[i]))

        molmassH2=molinfo.molmass("H2")
        molmassHe=molinfo.molmass("He", db_HIT=False)
        print("H2", molmassH2, "He", molmassHe)

        return mols_unique, mols_num, molmass, molmassH2, molmassHe


def database_path_hitran12(simple_molecule_name):
    """HITRAN12 default data path

    Args:
        simple_molecule_name (str): simple molecule name "H2O" 

    Returns:
        str: HITRAN12 default data path, such as "H2O/01_hit12.par" for "H2O"
    """
    from radis.db.classes import get_molecule_identifier
    ihitran = get_molecule_identifier(simple_molecule_name)
    return simple_molecule_name + "/" + str(ihitran).zfill(2) + "_hit12.par"


def database_path_hitemp(simple_molname):
    """default HITEMP path based on https://hitran.org/hitemp/

    Args:
        simple_molecule_name (str): simple molecule name "H2O" 

    Returns:
        str: HITEMP default data path, such as "H2O/01_HITEMP2010" for "H2O"
    """
    _hitemp_dbpath = {
        "H2O": "H2O/01_HITEMP2010",
        "CO2": "CO2/02_HITEMP2010",
        "N2O": "N2O/04_HITEMP2019/04_HITEMP2019.par.bz2",
        "CO": "CO/05_HITEMP2019/05_HITEMP2019.par.bz2",
        "CH4": "CH4/06_HITEMP2020/06_HITEMP2020.par.bz2",
        "NO": "NO/08_HITEMP2019/08_HITEMP2019.par.bz2",
        "NO2": "NO2/10_HITEMP2019/10_HITEMP2019.par.bz2",
        "OH": "OH/13_HITEMP2020/13_HITEMP2020.par.bz2"
    }
    return _hitemp_dbpath[simple_molname]


def database_path_exomol(simple_molname, root_database_path=".database"):
    from exojax.utils.molname import simple_molname_to_exact_exomol_stable
    from radis.api.exomolapi import get_exomol_database_list
    exact_molname_exomol_stable = simple_molname_to_exact_exomol_stable(
        simple_molname)
    mlist, recommended = get_exomol_database_list(simple_molname,
                                                  exact_molname_exomol_stable)
    dbpath = root_database_path + "/" + simple_molname + "/" + recommended
    return dbpath
