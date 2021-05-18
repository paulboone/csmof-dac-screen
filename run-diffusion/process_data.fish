
echo "NVEeq-1, NVEeq-2, NVEeq-3, NVEeq-4, NVEeq-5, NVT-1, NVT-2, NVT-3, NVT-4, NVT-5" > temps.csv

function _converttrj
  set -l atoms_per_molecule $argv[1]
  set -l mofs $argv[2..-1]

  echo $atoms_per_molecule
  echo $mofs
  for sim in $mofs
    cd $sim
    echo $sim
    if not test -f gastrj.npy
      if test -f ./output/gas.lammpstrj.gz
        lammpstrj_to_npy.py ./output/gas.lammpstrj.gz -f gastrj.npy --atoms-per-molecule $atoms_per_molecule --start-molecule-index 2
      else
        echo $sim: NO ./output/gas.lammpstrj.gz
      end
    end
    if not test -f diffusivity.out
      if test -f ./gastrj.npy
        npytraj_diffusivity.py ./gastrj.npy --average-rows 1 --fs-per-row 1000 --output-molecule-plots > diffusivity.out
      else
        echo $sim: NO ./gastrj.npy
      end
    end
    if not test -f nvt-eq.tsv
      lmp_log_to_tsv.py ./output/lammps.log -i 3 > nvt-eq.tsv
    end
    if not test -f nvt.tsv
      lmp_log_to_tsv.py ./output/lammps.log -i 4 > nvt.tsv
    end
    python3 ../../../csmof-dac-screening/run-diffusion/average_temps.py -r $sim >> ../temps.csv
    cd ..
  end
end

_converttrj 3 uio*-co2
_converttrj 3 uio*-n2
_converttrj 4 uio*-tip4p

echo "MOF, gas, D (MSD), D(FIT), MSD" > diffusivities.csv
for sim in uio*/diffusivity.out
  set -l gasname (string split - (dirname $sim))[-1]
  set -l mofname (basename (dirname $sim) -$gasname)
  set -l dmsd (awk '/^D \(MSD \/ t\) = .* angstrom\^2 \/ fs/ { print $6 }' $sim)
  set -l dfit (awk '/^D \(fit\) = .* angstrom\^2 \/ fs/ { print $4 }' $sim)
  set -l msd (awk '/^MSD = .* angstrom\^2/ { print $3 }' $sim)
  echo $mofname, $gasname, $diffusivity, $dmsd, $dfit, $msd >> diffusivities.csv
end

# for sim in uio*
#   cd $sim
#   python3 ../../../csmof-dac-screening/run-diffusion/average_temps.py -r $sim >> ../temps.csv
#   cd ..
# end

functions -e _converttrj
