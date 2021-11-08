
function setup-workflow
  set gitrepo (realpath $argv[1])
  set -g CSMOFTMPS $gitrepo/workflow-files

  echo "Using gitrepo $gitrepo"
  echo "Using workflow-files directory $CSMOFTMPS"
end

setup-workflow (dirname (status --current-filename))

function setup-structures
  mkdir -p linkers-lmpdat
  echo ""
  echo "Parameterizing CML linkers and outputting LMPDAT files..."
  uff-parameterize-linker --linker-path=linkers-cml/uio66.cml --outpath=linkers-lmpdat/ linkers-cml/uio66-*.cml
  uff-parameterize-linker --linker-path=linkers-cml/uio67.cml --outpath=linkers-lmpdat/ linkers-cml/uio67-*.cml

  mkdir -p mofs-functionalized/
  echo ""
  echo "Functionalizing structure with parameterized linkers..."
  functionalize-structure mofs/uio66.cif --expected-num=24 --output-dir=./mofs-functionalized/ linkers-cml/uio66.cml linkers-lmpdat/uio66-*.lmpdat
  functionalize-structure mofs/uio67.cif --expected-num=24 --output-dir=./mofs-functionalized/ linkers-cml/uio67.cml linkers-lmpdat/uio67-*.lmpdat

  echo "replacing H-C-H force constant with one stronger so H-C-H angles don't collapse..."
  gsed -i 's/fourier  75.498766  0.343737  0.374972  0.281246   # H_ C_3 H_/fourier  200.0  0.343737  0.374972  0.281246   # H_ C_3 H_/g' mofs-functionalized/*.lmpdat

  mkdir -p relax-fngroup-NVT
  echo "making NVT simulation directories, one for each functionalized MOF..."
  for mof in ./mofs-functionalized/*.lmpdat
    set mofname (basename $mof .lmpdat)
    set mofdir relax-fngroup-NVT/$mofname
    mkdir $mofdir
    cp $mof $mofdir/
  end
  echo "Please run NVT sims using `run-relax-fngroup-NVT`"
end

function run-relax-fngroup-NVT
  mkdir -p mofs-relaxed-cifs
  cd relax-fngroup-NVT
  for mofpath in */*.lmpdat
    echo $mofpath
    set mof (dirname $mofpath)
    cd $mof
    ~/workspace/lammps/src/lmp_serial -l lammps.log -var lmpdatpath $mof.lmpdat < $CSMOFTMPS/relax-fngroup-NVT/relax-fngroup-NVT.lammps
    lmpdatdump2cif $mof.lmpdat --dumppath=nvt-preeq.dump.20000.custom --outpath=../../mofs-relaxed-cifs/$mof.cif
    cd ..
  end

  grep "Dangerous builds" */lammps.log > relax-NVT-dangerous-builds.out
  grep "WARNING" */lammps.log > relax-NVT-warnings.out
  grep "ERROR" */lammps.log > relax-NVT-errors.out

  echo "copy over original non-functionalized MOFS"
  # need to use converter to convert from cartesian to fractional coordinates
  lmpdatdump2cif ../mofs/uio66.cif -o ../mofs-relaxed-cifs/uio66.cif
  lmpdatdump2cif ../mofs/uio67.cif -o ../mofs-relaxed-cifs/uio67.cif

  echo "Please review the *.out files in relax-fngroup-NVT to verify NVT was OK!"
  checkNVTdumpfiles > checkdumps.out

  cd ..
end

function checkNVTdumpfiles
  for mofpath in */
    set mof (basename $mofpath)
    cd $mof
    printf "%21s: " $mof
    set dump ./nvt-preeq.dump.20000.custom
    if test -e $dump
      checkNVTdumpfile $mof.lmpdat $dump
    else
      printf "NO file: $dump"
    end
    printf "\n"
    cd ..
  end
end

function modify-raspa-input
  set mofname $argv[1]
  set inputfile $argv[2]
  set vffile $argv[3]

  gsed -i "s/FrameworkName.*/FrameworkName $mofname/g" $inputfile

  if string match --quiet "uio67*" $mofname
    gsed -i "s/UnitCells.*/UnitCells 1 1 1/g" $inputfile
  end

  if test -n "$vffile"
    set vfline (string split , (grep $mofname, $vffile))
    if test -z "$vfline"
      echo "ERROR: no void fraction match found for $mofname"
    else
      gsed -i "s/HeliumVoidFraction.*/HeliumVoidFraction $vfline[2]/g" $inputfile
    end
  end
end

function setup-calculate-charges
  echo "generate RASPA dirs + run EQEQ on each MOF"
  mkdir -p run-calculate-charges
  cd run-calculate-charges
  for mof in ../mofs-relaxed-cifs/*
    echo "$mof"
    set mofname (basename $mof .cif)
    mkdir $mofname
    cp $mof ./$mofname/
    cp $CSMOFTMPS/run-calculate-charges/*.def ./$mofname/
    cp $CSMOFTMPS/run-calculate-charges/*.input ./$mofname/
    cd $mofname/

    gsed -i "s/FrameworkName.*/FrameworkName $mofname/g" ./eqeq.input
    # simulate -i eqeq.input

    cd ..
  end
  cp $CSMOFTMPS/run-adsorption/raspa.slurm ./
  cd ..
end

function process-calculate-charges
  mkdir -p mofs-relaxed-cifs-w-charges
  cd run-calculate-charges
  for mof in ../mofs-relaxed-cifs/*
    set mofname (basename $mof .cif)
    echo $mofname
    cp $mofname/results/Movies/System_0/Framework_0_final_1_1_1_P1.cif ../mofs-relaxed-cifs-w-charges/$mofname.cif
  end
  cd ..
end

function setup-voidfraction
  mkdir -p run-voidfraction
  cd run-voidfraction
  for mof in ../mofs-relaxed-cifs-w-charges/*.cif
    set mofname (basename $mof .cif)
    set mofprocessdir {$mofname}
    echo $mofname
    mkdir $mofprocessdir
    cp $mof $mofprocessdir/
    cp $CSMOFTMPS/run-adsorption/*.def $mofprocessdir/
    cp $CSMOFTMPS/run-voidfraction/voidfraction.input $mofprocessdir

    modify-raspa-input $mofname $mofprocessdir/voidfraction.input
  end
  cp $CSMOFTMPS/run-adsorption/raspa.slurm ./
  cd ..
  echo "Finished. The dirs in run-voidfraction should be run on H2P using the provided .slurm file."
end

function process-voidfraction
  echo "mof, voidfraction, voidfraction_error" > voidfraction.csv
  for mof in */
    set mofname (basename $mof)
    echo $mofname
    set widomline (string split -n " " (grep "Average Widom Rosenbluth-weight:" $mofname/results/Output/System_0/*.data))
    echo "$mofname, $widomline[5], $widomline[7]" >> voidfraction.csv
  end
end

function setup-surfacearea
  mkdir -p run-surfacearea
  cd run-surfacearea
  for mof in ../mofs-relaxed-cifs-w-charges/*.cif
    set mofname (basename $mof .cif)

    set mofprocessdir {$mofname}
    mkdir $mofprocessdir
    cp $mof $mofprocessdir/
    cp $CSMOFTMPS/run-adsorption/*.def $mofprocessdir/
    cp $CSMOFTMPS/run-surfacearea/surfacearea.input $mofprocessdir

    modify-raspa-input $mofname $mofprocessdir/surfacearea.input ../run-voidfraction/voidfraction.csv
  end
  cp $CSMOFTMPS/run-surfacearea/raspa.slurm ./
  cd ..
  echo "Finished. The dirs in run-surfacearea should be run on H2P using the provided .slurm file."
end

function process-surfacearea
  echo "mof, surfacearea, surfacearea_error" > surfacearea.csv
  for mof in */
    set mofname (basename $mof)
    echo $mofname
    set widomline (string split -n " " (grep "Surface area: .* \[m^2/g\]" $mofname/results/Output/System_0/*.data))
    echo "$mofname, $widomline[3], $widomline[5]" >> surfacearea.csv
  end
end

function setup-adsorption
  mkdir -p run-adsorption
  cd run-adsorption
  for mof in ../mofs-relaxed-cifs-w-charges/*.cif
    set mofname (basename $mof .cif)
    for raspa_input in $CSMOFTMPS/run-adsorption/*.input
      set gasprocess (basename $raspa_input .input)
      set mofprocessdir {$mofname}_{$gasprocess}

      mkdir $mofprocessdir
      cp $mof $mofprocessdir/
      cp $CSMOFTMPS/run-adsorption/*.def $mofprocessdir/
      cp $raspa_input $mofprocessdir

      modify-raspa-input $mofname $mofprocessdir/$gasprocess.input ../run-voidfraction/voidfraction.csv
    end
  end
  cp $CSMOFTMPS/run-adsorption/raspa.slurm ./
  cd ..
  echo "Finished. The dirs in run-adsorption should be run on H2P using the provided .slurm file."
end

function process-adsorption-data
  extract-loadings "uio*_stp/results/Output/System_0/*.data" > loadings_stp.csv
  extract-loadings "uio*_desorb/results/Output/System_0/*.data" > loadings_desorb.csv

  extract-henrys "uio*_henrys/results/Output/System_0/*.data" > henrys_stp.csv
  extract-henrys "uio*_henrys2/results/Output/System_0/*.data" > henrys_desorb.csv
end

function setup-diffusion
  mkdir -p run-diffusion
  cd run-diffusion
  # make independent configs
  for mof in ../mofs-relaxed-cifs-w-charges/*.cif
    set mofname (basename $mof .cif)

    for gas in $CSMOFTMPS/run-diffusion/*.lammps
      set gasname (basename $gas .lammps)
      set mofgasdir $mofname-$gasname
      mkdir $mofgasdir

      cd $mofgasdir/
      mofun_converter --mic 12.8 --pp ../$mof $mofname.lmpdat
      mofun_converter $mofname.lmpdat $mofname.xyz
      packmol_gaslmpdat -n 10 {$mofname}.lmpdat {$mofname}.xyz $CSMOFTMPS/run-diffusion/$gasname.lmpdat $CSMOFTMPS/run-diffusion/$gasname.xyz
      cp $gas ./

      set randomseed (random)
      gsed -i "s/variable randomSeed equal.*/variable randomSeed equal $randomseed/g" $gas

      set numatomtypes (grep ".* atom types" $mofname.lmpdat | cut -f 1 -d ' ')
      gsed -i "s/variable mofAtomTypes equal.*/variable mofAtomTypes equal $numatomtypes/g" $gas

      cd ..
    end
  end
  cp $CSMOFTMPS/run-diffusion/lammps.slurm ./
  cd ..
  echo "Finished. The dirs in run-diffusion should be run on H2P using the provided .slurm file."
end

function check-configs
  for sim in uio*
    cd $sim
    set -l structure uio*.lmpdat
    set -l gas (ls | grep -v "^uio*" | grep ".*lmpdat")
    echo $structure $gas
    check-config $structure $gas
    cd ..
  end
end

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
    cd ..
  end
end

function _cleantrj
  rm */gastrj.npy
  rm */diffusivity.out
  rm */nvt-eq.tsv
  rm */nvt.tsv
end

function process-diffusion-data
  echo "NVEeq-1, NVEeq-2, NVEeq-3, NVEeq-4, NVEeq-5, NVT-1, NVT-2, NVT-3, NVT-4, NVT-5" > temps.csv
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

  for sim in uio*
    cd $sim
    echo $sim
    average-temps -r $sim >> ../temps.csv
    cd ..
  end
end
  # functions -e _converttrj

function setup-raspa-isotherm-dirs
  set mofs $argv
  set pressures  10 25 40 50 100 500 1000 5000 10000 50000 101325
  mkdir -p run-isotherms
  cd run-isotherms

  # make independent configs
  for mofpath in $mofs
    cp $CSMOFTMPS/run-adsorption/raspa.slurm ./
    echo "mofpath: $mofpath"
    set mof (basename $mofpath .cif)
    echo "mof: $mof"
    mkdir -p $mof
    cd $mof

    # CO2
    for p in $pressures
      mkdir -p CO2-$p
      cd CO2-$p
      cp ../../../$mofpath ./$mof.cif
      cp $CSMOFTMPS/run-adsorption/co2_stp.input ./co2.input
      cp $CSMOFTMPS/run-adsorption/force_field.def ./
      cp $CSMOFTMPS/run-adsorption/force_field_mixing_rules.def ./
      cp $CSMOFTMPS/run-adsorption/pseudo_atoms.def ./

      modify-raspa-input $mof ./co2.input ../../../run-voidfraction/voidfraction.csv
      gsed -i -e "s|^ExternalPressure.*|ExternalPressure     $p|" ./co2.input
      cd ..
    end

    # N2
    for p in $pressures
      mkdir -p N2-$p
      cd N2-$p
      cp ../../../$mofpath ./$mof.cif
      cp $CSMOFTMPS/run-adsorption/n2_stp.input ./n2.input
      cp $CSMOFTMPS/run-adsorption/force_field.def ./
      cp $CSMOFTMPS/run-adsorption/force_field_mixing_rules.def ./
      cp $CSMOFTMPS/run-adsorption/pseudo_atoms.def ./
      modify-raspa-input $mof ./n2.input ../../../run-voidfraction/voidfraction.csv
      gsed -i -e "s|^ExternalPressure.*|ExternalPressure     $p|" ./n2.input
      cd ..
    end

    # N2 @ 77K for surface area
    for p in $pressures
      mkdir -p N2@77K-$p
      cd N2@77K-$p
      cp ../../../$mofpath ./$mof.cif
      cp $CSMOFTMPS/run-adsorption/n2_stp.input ./n2.input
      cp $CSMOFTMPS/run-adsorption/force_field.def ./
      cp $CSMOFTMPS/run-adsorption/force_field_mixing_rules.def ./
      cp $CSMOFTMPS/run-adsorption/pseudo_atoms.def ./
      modify-raspa-input $mof ./n2.input ../../../run-voidfraction/voidfraction.csv
      gsed -i -e "s|^ExternalTemperature.*|ExternalTemperature  77|" ./n2.input
      gsed -i -e "s|^ExternalPressure.*|ExternalPressure     $p|" ./n2.input
      cd ..
    end
    cd ..
  end
  cd ..
end

function process-isotherm-data
  mkdir -p isotherms
  for d in uio*/
    set mof (basename $d)
    echo "$mof/*/results/Output/System_0/*.data"
    extract-loadings --pa2bar --isothermruns --units cc_g "$mof/N2-*/results/Output/System_0/*.data" > ./isotherms/{$mof}_N2_sim.csv
    extract-loadings --pa2bar --isothermruns --units cc_g "$mof/N2@77K-*/results/Output/System_0/*.data" > ./isotherms/{$mof}_N2@77K_sim.csv
    extract-loadings --pa2bar --isothermruns --units cc_g "$mof/CO2*/results/Output/System_0/*.data" > ./isotherms/{$mof}_CO2_sim.csv
  end
end
