
# make independent configs
for mof in ../run-relax-NVT/mofs-relaxed-cifs/*
  set mofname (basename $mof .cif)

  for gas in *.lammps
    set gasname (basename $gas .lammps)
    set mofgasdir $mofname-$gasname
    mkdir $mofgasdir

    cd $mofgasdir/
    python3 ../../run-relax-NVT/cif2lmpdat.py --mic 12.8 ../$mof $mofname.lmpdat
    python3 ../../lmpdatdump2cif.py $mofname.lmpdat -o $mofname.xyz
    python3 ../packmol_gaslmpdat.py -n 10 {$mofname}.lmpdat {$mofname}.xyz ../$gasname.lmpdat ../$gasname.xyz
    cp ../$gas ./

    set randomseed (random)
    gsed -i "s/variable randomSeed equal.*/variable randomSeed equal $randomseed/g" $gas

    set numatomtypes (grep ".* atom types" $mofname.lmpdat | cut -f 1 -d ' ')
    gsed -i "s/variable mofAtomTypes equal.*/variable mofAtomTypes equal $numatomtypes/g" $gas

    cd ..
  end
end
