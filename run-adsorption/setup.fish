

for mof in ../run-eqeq/cifs-w-charges/*.cif
  set mofname (basename $mof .mol)
  for raspa_input in *.input
    set gasprocess (basename $raspa_input .input)
    set mofprocessdir {$mofname}_{$gasprocess}

    mkdir $mofprocessdir
    cp $mof $mofprocessdir/
    cp ./*.def $mofprocessdir/
    cp $raspa_input $mofprocessdir

    gsed -i "s/FrameworkName.*/FrameworkName $mofname/g" $mofprocessdir/$gasprocess.input
    if string match "uio67*" $mofname
      gsed -i "s/UnitCells.*/UnitCells 1 1 1/g" $mofprocessdir/$gasprocess.input
    end
  end
end
