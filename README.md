# Pre-FAIR: Combining Partial Preferences for Fair Consensus Decision-making


Code and data for "Pre-FAIR: Combining Partial Preferences for Fair Consensus Decision-making". To reproduce
the experiments run `wh.py` (world happiness data), `econf.py` (economic freedom data), `gsci.py` (gsci data),
`ibmhr.py` (ibmhr data), and `synthetic_study.py` (partially synthetic ACMEMP-Mallows profiles - note the code to
generate the Mallows profiles themselves are in `data\synthetic-study\generate_mallows.R`). Next to produce the plots
used in the paper run the script `plotting.R` in the `results/` folder.

All Prefair source code is in the `src/` folder, and all compared methods are in the `comparedmethods/` folder (using code 
from [EPIRA](https://github.com/KCachel/Fairer-Together-Mitigating-Disparate-Exposure-in-Kemeny-Aggregation),
[RAPF](https://github.com/MouinulIslamNJIT/Rank-Aggregation_Proportionate_Fairness),
and [FMWV](https://github.com/huanglx12/Balanced-Committee-Election)). Note that
FMWV requires the Gurobi python package and corresponding licence.  If you do not have one, you can just run the R script 
to generate the figures using the provided results files.

Each dataset is provided in the `data/` folder and are derived from publicly released data. However, our repo cannot directly contain the Economic Freedom data. The Fraser institute makes
the data publicly available, but users wishing to use it must download it themselves from https://www.fraserinstitute.org/economic-freedom/dataset.
Once the `efotw-2023-master-index-data-for-researchers-iso.xlsx` file is downloaded please place it into the `econ-freedom/` folder.

