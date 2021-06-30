


python3 ../../csmof-dac-screening/run-adsorption/extract_loadings.py "uio*_stp/results/Output/System_0/*.data" > loadings_stp.csv
python3 ../../csmof-dac-screening/run-adsorption/extract_loadings.py "uio*_desorb/results/Output/System_0/*.data" > loadings_desorb.csv

python3 ../../csmof-dac-screening/run-adsorption/extract_henrys.py "uio*_henrys/results/Output/System_0/*.data" > henrys_stp.csv
python3 ../../csmof-dac-screening/run-adsorption/extract_henrys.py "uio*_henrys2/results/Output/System_0/*.data" > henrys_desorb.csv
