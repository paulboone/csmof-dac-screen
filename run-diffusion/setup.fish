
# make independent configs
for mof in ../run-relax-NVT/mofs-relaxed-lmpdat/*CF3-2.lmpdat
  set mofname (basename $mof .lmpdat)

  for gas in *.lmpdat
    set gasname (basename $gas .lmpdat)
    set mofgasdir $mofname-$gasname
    mkdir $mofgasdir
    cp $mof $mofgasdir/
    obabel -i cif ../run-relax-NVT/mofs-relaxed-cifs/$mofname.cif -o xyz -O $mofgasdir/$mofname.xyz
    cd $mofgasdir/
    python3 ../packmol_gaslmpdat.py -n 100 $mofname.xyz ../$gasname.lmpdat ../$gasname.xyz
    cd ..
  end
end
