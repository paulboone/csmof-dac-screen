set -l sourcemofs ../run-relax-NVT/mofs-relaxed-mols/*
if count $argv
  set sourcemofs $argv
end
echo "using: $sourcemofs"
# make independent configs
mkdir -p cifs-w-charges
for mof in $sourcemofs
  set mofname (basename $mof .mol)
  echo (date): $mofname
  mkdir $mofname
  cp $mof ./$mofname/
  cd $mofname/
  cp ../*.def ./
  cp ../*.input ./

  gsed -i "s/FrameworkName.*/FrameworkName $mofname/g" ./eqeq.input
  simulate -i eqeq.input
  cp Movies/System_0/Framework_0_final_1_1_1_P1.cif ../cifs-w-charges/$mofname.cif

  cd ..
end
