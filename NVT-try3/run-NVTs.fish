
for mofpath in */*.lmpdat
  set mof (dirname $mofpath)
  echo "\n\n $mof"
  cd $mof
  ~/workspace/lammps/src/lmp_serial -var lmpdatpath $mof.lmpdat < ../fngroup-NVT.lammps
  python3 ../../lmpdatdump2cif.py $mof.lmpdat --dumppath=nvt-preeq.dump.20000.custom --outpath=$mof.cif > lmpdatdump.log

  echo "START @0"
  python3 ../../checkdumpfile.py $mof.lmpdat nvt-preeq.dump.0.custom
  echo "END @10000"
  python3 ../../checkdumpfile.py $mof.lmpdat nvt-preeq.dump.10000.custom
  cd ..
end

grep "Dangerous builds" */log.lammps > dangerous-builds.out
grep "WARNING" */log.lammps > warnings.out
grep "ERROR" */log.lammps > errors.out


for mofpath in uio*/
  set mof (basename $mofpath)
  echo "" >> checkdumps.out
  echo "$mof" >> checkdumps.out
  cd $mof
  echo "START @0" >> checkdumps.out
  python3 ../../checkdumpfile.py $mof.lmpdat nvt-preeq.dump.0.custom >> checkdumps.out
  echo "END @10000" >> checkdumps.out
  python3 ../../checkdumpfile.py $mof.lmpdat nvt-preeq.dump.10000.custom >> checkdumps.out
  cd ..
end
