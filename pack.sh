#!/bin/bash

declare -a tiles=("h27v11" "h27v12" "h28v11" "h28v12" "h28v13" "h29v10" "h29v11" "h29v12" "h29v13" "h30v10" "h30v11" "h30v12" "h31v10" "h31v11" "h31v12" "h32v10" "h32v11")

for y in {2018..2018};
do
    for t in "${tiles[@]}"
    do
        echo "Iteration $y $t"
        /g/data1/xc0/software/conda-envs/rs3/bin/python packer.py -y $y -t $t
    done
done

