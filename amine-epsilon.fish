
function setup-amine-epsilon-test
  set mofs (realpath $argv)
  # set mofs ../mofs-relaxed-cifs-w-charges/*.cif

  mkdir -p run-amine-epsilon-test
  cd run-amine-epsilon-test
  for mof in $mofs
    set mofname (basename $mof .cif)
    for multpl in 1 2 10 100
      set mofprocessdir {$mofname}_{$multpl}xEPS
      mkdir $mofprocessdir
      cp $mof $mofprocessdir/
      cp $CSMOFTMPS/run-adsorption/co2_stp.input $mofprocessdir/
      cp $CSMOFTMPS/run-adsorption/force_field_mixing_rules.def $mofprocessdir/
      cp $CSMOFTMPS/run-adsorption/pseudo_atoms.def $mofprocessdir/
      cp $CSMOFTMPS/run-amine-epsilon/force_field.def $mofprocessdir/

      modify-raspa-input $mofname $mofprocessdir/co2_stp.input ../run-voidfraction/voidfraction.csv
      set eps (math $multpl x 30.61983 )
      gsed -i "s/C_co2 N lennard-jones.*/C_co2 N lennard-jones $eps 3.03035/g" $mofprocessdir/force_field.def
    end
  end
  cp $CSMOFTMPS/run-adsorption/raspa.slurm ./
  cd ..
  echo "Finished. The dirs in run-adsorption should be run on H2P using the provided .slurm file."
end
