for sim in uio*co2
  cd $sim
  lammpstrj_to_npy.py ./gas.lammpstrj -f gastrj.npy --atoms-per-molecule 3 --start-molecule-index 2
  npytraj_diffusivity.py ./gastrj.npy --average_rows 4000 --output-molecule-plots
  cd ..
end
