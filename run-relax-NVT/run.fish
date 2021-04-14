
mkdir mofs-relaxed-cifs
for mofpath in */*.lmpdat
  set mof (dirname $mofpath)
  echo "\n\n $mof"
  cd $mof
  ~/workspace/lammps/src/lmp_serial -l lammps.log -var lmpdatpath $mof.lmpdat < ../fngroup.lammps
  python3 ../../lmpdatdump2cif.py $mof.lmpdat --dumppath=nvt-preeq.dump.20000.custom --outpath=../mofs-relaxed-cifs/$mof.cif
  cd ..
end

mkdir charges
mkdir mofs-relaxed-mols
mkdir mofs-relaxed-lmpdat
for cif in mofs-relaxed-cifs/*.cif
    set mof (basename $cif .cif)
    echo $mof
    obabel -i cif $cif --partialcharge eqeq -o mol2 -O /dev/null --print > charges/$mof.charges
    python3 ../cif2raspamol_wcharges.py $cif charges/$mof.charges mofs-relaxed-mols/$mof.mol
    python3 ../cif2lmpdat_wcharges.py $cif charges/$mof.charges mofs-relaxed-lmpdat/$mof.lmpdat
end

grep "Dangerous builds" */log.lammps > dangerous-builds.out
grep "WARNING" */log.lammps > warnings.out
grep "ERROR" */log.lammps > errors.out

. ./checkdumps.fish > checkdumps.out
