
# make independent configs
for mof in ../run-relax-NVT/mofs-relaxed-cifs/*CF3-2.cif
  set mofname (basename $mof .cif)

  for gas in *.lammps
    set gasname (basename $gas .lammps)
    set mofgasdir $mofname-$gasname
    mkdir $mofgasdir

    cd $mofgasdir/
    python3 ../../run-relax-NVT/cif2lmpdat.py --mic 12.8 ../$mof $mofname.lmpdat
    python3 ../../lmpdatdump2cif.py $mofname.lmpdat -o $mofname.xyz
    python3 ../packmol_gaslmpdat.py -n 10 {$mofname}.lmpdat {$mofname}.xyz ../$gasname.lmpdat ../$gasname.xyz
    cd ..
  end
end
