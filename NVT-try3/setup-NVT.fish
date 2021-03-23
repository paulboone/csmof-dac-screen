

for mof in ../mofs-functionalized/*.lmpdat
  mkdir (basename $mof .lmpdat)
  cp $mof (basename $mof .lmpdat)/
end
