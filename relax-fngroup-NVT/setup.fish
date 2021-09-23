for mof in ../mofs-functionalized/*.lmpdat
  set mofname (basename $mof .lmpdat)
  mkdir $mofname
  cp $mof $mofname/

  ### replace H-C-H force constant with one stronger so H-C-H angles don't collapse
  gsed -i 's/fourier  75.498766  0.343737  0.374972  0.281246   # H_ C_3 H_/fourier  200.0  0.343737  0.374972  0.281246   # H_ C_3 H_/g' $mofname/$mofname.lmpdat
end
