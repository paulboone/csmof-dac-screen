for mofpath in uio*
  set mof (basename $mofpath)
  cd $mof
  printf "%21s: " $mof
  if test -e eq.dump.0.custom
    python3 ../../checkdumpfile.py --nowarns $mof.lmpdat eq.dump.0.custom
  else
    printf "NO file: nvt-preeq.dump.0.custom"
  end
  printf " => "
  set dump ./eq.dump.100.custom
  if test -e $dump
    python3 ../../checkdumpfile.py $mof.lmpdat $dump
  else
    printf "NO file: $dump"
  end
  printf "\n"
  cd ..
end
