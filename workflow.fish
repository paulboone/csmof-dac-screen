

function setup-workflow
  set gitrepo $argv[1]
  echo "Copying necessary files from $gitrepo"

  cp -r $gitrepo/run-functionalize/mofs
  cp -r $gitrepo/run-functionalize/linkers-cml
  cp $gitrepo/run-relax-NVT/relax-fngroup-NVT.lammps ./
end


function run-workflow
  mkdir -p linkers-lmpdat
  echo ""
  echo "Parameterizing CML linkers and outputting LMPDAT files..."
  # uff-parameterize-linker --linker-path=linkers-cml/uio66.cml --outpath=linkers-lmpdat/ linkers-cml/uio66-*.cml
  uff-parameterize-linker --linker-path=linkers-cml/uio67.cml --outpath=linkers-lmpdat/ linkers-cml/uio67-*.cml

  mkdir -p mofs-functionalized/
  echo ""
  echo "Functionalizing structure with parameterized linkers..."
  # functionalize-structure mofs/uio66-P1.cif --output-dir=./mofs-functionalized/ linkers-cml/uio66.cml linkers-lmpdat/uio66-*.lmpdat
  functionalize-structure mofs/uio67-P1.cif --output-dir=./mofs-functionalized/ linkers-cml/uio67.cml linkers-lmpdat/uio67-*.lmpdat

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
end


function run-relax-fngroup-NVT
  mkdir -p mofs-relaxed-cifs
  cd relax-fngroup-NVT
  for mofpath in */*.lmpdat
    echo $mofpath
    set mof (dirname $mofpath)
    cd $mof
    ~/workspace/lammps/src/lmp_serial -l lammps.log -var lmpdatpath $mof.lmpdat < ../../relax-fngroup-NVT.lammps
    lmpdatdump2cif $mof.lmpdat --dumppath=nvt-preeq.dump.20000.custom --outpath=../../mofs-relaxed-cifs/$mof.cif
    cd ..
  end

  # mkdir charges
  # mkdir mofs-relaxed-mols
  # mkdir mofs-relaxed-lmpdat
  # for cif in mofs-relaxed-cifs/*.cif
  #     set mof (basename $cif .cif)
  #     echo $mof
  #     obabel -i cif $cif --partialcharge eqeq -o mol2 -O /dev/null --print > charges/$mof.charges
  #     python3 ./cif2raspamol_wcharges.py $cif charges/$mof.charges mofs-relaxed-mols/$mof.mol
  #     python3 ./cif2lmpdat_wcharges.py $cif charges/$mof.charges mofs-relaxed-lmpdat/$mof.lmpdat
  # end

  grep "Dangerous builds" */log.lammps > relax-NVT-dangerous-builds.out
  grep "WARNING" */log.lammps > relax-NVT-warnings.out
  grep "ERROR" */log.lammps > relax-NVT-errors.out

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
