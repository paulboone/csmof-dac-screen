
function _converttrj
  set atoms_per_molecule $argv[1]
  set mofs $argv[2..-1]

  echo $atoms_per_molecule
  echo $mofs
  for sim in $mofs
    if not test -f $sim/gastrj.npy
      cd $sim
      echo $sim
      if test -f ./output/gas.lammpstrj.gz
        lammpstrj_to_npy.py ./output/gas.lammpstrj.gz -f gastrj.npy --atoms-per-molecule $atoms_per_molecule --start-molecule-index 2
      else
        echo $sim: NO ./output/gas.lammpstrj.gz
      end
      if test -f ./gastrj.npy
        npytraj_diffusivity.py ./gastrj.npy --average-rows 1 --fs-per-row 1000 --output-molecule-plots > diffusivities.out
      else
        echo $sim: NO ./gastrj.npy
      end
      cd ..
    end
  end
end

_converttrj 3 uio*-co2
_converttrj 3 uio*-n2
_converttrj 4 uio*-tip4p

functions -e _converttrj
