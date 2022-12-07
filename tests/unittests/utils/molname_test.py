import pytest
from exojax.utils.molname import s2e_stable
from exojax.utils.molname import e2s
from exojax.utils.molname import split_simple
import numpy as np
def test_s2estable():
    EXOMOL_SIMPLE2EXACT = \
        {
            'CO': '12C-16O',
            'OH': '16O-1H',
            'NH3': '14N-1H3',
            'NO': '14N-16O',
            'FeH': '56Fe-1H',
            'H2S': '1H2-32S',
            'SiO': '28Si-16O',
            'CH4': '12C-1H4',
            'HCN': '1H-12C-14N',
            'C2H2': '12C2-1H2',
            'TiO': '48Ti-16O',
            'CO2': '12C-16O2',
            'CrH': '52Cr-1H',
            'H2O': '1H2-16O',
            'VO': '51V-16O',
            'CN': '12C-14N',
            'PN': '31P-14N',
        }

    check = True
    for i in EXOMOL_SIMPLE2EXACT:
        assert s2e_stable(i) == EXOMOL_SIMPLE2EXACT[i]
    assert s2e_stable("H3O_p") ==  "1H3-16O_p"


def test_e2s():
    assert e2s('12C-1H4') == "CH4"
    assert e2s('23Na-16O-1H') == "NaOH"
    assert e2s('HeH_p') == "HeH_p"
    assert e2s("trans-31P2-1H-2H") == "trans-31P2-1H-2H"

def test_split_simple():
    assert np.all(split_simple("Fe2O3") == (['Fe', 'O'], ['2', '3']))

if __name__ == '__main__':
    test_s2estable()