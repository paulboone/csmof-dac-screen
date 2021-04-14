
for mofpath in */*.lmpdat
  set mof (dirname $mofpath)
  echo "\n\n $mof"
  cd $mof
  ~/workspace/lammps/src/lmp_serial -l lammps.log -var lmpdatpath $mof.lmpdat < ../fngroup.lammps
  cd ..
end

grep "Dangerous builds" */log.lammps > dangerous-builds.out
grep "WARNING" */log.lammps > warnings.out
grep "ERROR" */log.lammps > errors.out

. ./checkdumps.fish > checkdumps.out


for mofpath in */*.lmpdat
  set mof (dirname $mofpath)
  cd $mof
  python3 ../../lmpdatdump2cif.py $mof.lmpdat --dumppath=nvt-preeq.dump.20000.custom --outpath=cifs/$mof.cif
  cd ..
end

mkdir charges
for cif in cifs/*.cif
    echo (basename $cif .cif)
    obabel -i cif $cif --partialcharge eqeq -o mol2 -O /dev/null --print > charges/(basename $cif .cif).charges
end

mkdir mols
for cif in cifs/*.cif
    set mof (basename $cif .cif)
    echo $mof
    python3 ../generate_raspa_mol.py $cif charges/$mof.charges mols/$mof.mol
end

mkdir lmpdat
for cif in cifs/*.cif
    set mof (basename $cif .cif)
    echo $mof
    python3 ../generate_lammps_diffusion.py $cif charges/$mof.charges lmpdat/$mof.lmpdat
end
