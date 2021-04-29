
for sim in uio*
  cd $sim
  set -l structure uio*.lmpdat
  set -l gas (ls | grep -v "^uio*" | grep ".*lmpdat")
  echo $structure $gas
  python3 ../../run-diffusion/check_configs.py $structure $gas
  cd ..
end
