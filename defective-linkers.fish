
function setup-defective-mofs
  ## run this, and delete out the extra bonds / etc
  # uff-parameterize-linker --outpath=linkers-lmpdat/ linkers-cml/uio67-defective.cml
  mkdir -p mofs

  functionalize-structure original_mofs/uio67.cif --output-dir=./mofs/ --replace-fraction=0.05 linkers-cml/uio67.cml linkers-defective-lmpdat/uio67-defective.lmpdat
  mv ./mofs/uio67-defective.lmpdat ./mofs/uio67-defective05.lmpdat
  functionalize-structure original_mofs/uio67.cif --output-dir=./mofs/ --replace-fraction=0.10 linkers-cml/uio67.cml linkers-defective-lmpdat/uio67-defective.lmpdat
  mv ./mofs/uio67-defective.lmpdat ./mofs/uio67-defective10.lmpdat
  functionalize-structure original_mofs/uio67.cif --output-dir=./mofs/ --replace-fraction=0.15 linkers-cml/uio67.cml linkers-defective-lmpdat/uio67-defective.lmpdat
  mv ./mofs/uio67-defective.lmpdat ./mofs/uio67-defective15.lmpdat
  functionalize-structure original_mofs/uio67.cif --output-dir=./mofs/ --replace-fraction=0.20 linkers-cml/uio67.cml linkers-defective-lmpdat/uio67-defective.lmpdat
  mv ./mofs/uio67-defective.lmpdat ./mofs/uio67-defective20.lmpdat
end

function setup-structures
  mkdir -p linkers-lmpdat
  echo ""
  echo "Parameterizing CML linkers and outputting LMPDAT files..."
  # uff-parameterize-linker --linker-path=linkers-cml/uio66.cml --outpath=linkers-lmpdat/ linkers-cml/uio66-*.cml
  # uff-parameterize-linker --linker-path=linkers-cml/uio67.cml --outpath=linkers-lmpdat/ linkers-cml/uio67-*.cml

  mkdir -p mofs-functionalized/
  echo ""
  echo "Functionalizing structure with parameterized linkers..."
  for linker in ./linkers-lmpdat/*.lmpdat
    for mof in mofs/uio67-defective*.lmpdat
      echo $mof + $linker
      functionalize-structure $mof --output-dir=./mofs-functionalized/ linkers-cml/uio67.cml $linker
    end
  end

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


function renamedefectivedirs
  for d in uio67*
    set newd (string replace -- '_uio67' '-uio67' $d)
    echo D: $d to $newd
    mv $d $newd
  end
end



