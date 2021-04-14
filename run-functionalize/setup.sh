

python3 ./cml2lmpdat_wparams.py --linker-path=linkers-cml/uio66.cml --outpath=linkers-lmpdat/ linkers-cml/uio66-* > cml2lmpdat.out
python3 ./cml2lmpdat_wparams.py --linker-path=linkers-cml/uio67.cml --outpath=linkers-lmpdat/ linkers-cml/uio67-* >> cml2lmpdat.out

python3 ./functionalize_linkers.py mofs/uio66-P1.cif --output-dir=./mofs-functionalized/ linkers-cml/uio66.cml linkers-lmpdat/uio66-* > functional_structure.out
python3 ./functionalize_linkers.py mofs/uio67-P1.cif --output-dir=./mofs-functionalized/ linkers-cml/uio67.cml linkers-lmpdat/uio67-* >> functional_structure.out
