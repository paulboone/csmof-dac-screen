for mofpath in uio*
  set mof (basename $mofpath)
  cd $mof
  printf "%21s: " $mof
  set dump ./nvt-preeq.dump.20000.custom
  if test -e $dump
    python3 ../../checkdumpfile.py $mof.lmpdat $dump
  else
    printf "NO file: $dump"
  end
  printf "\n"
  cd ..
end
