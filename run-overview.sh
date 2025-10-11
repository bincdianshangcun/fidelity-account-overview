#!/usr/bin/env bash

set -e


source common.qmenu.sh 

if command -v deactivate &> /dev/null
then
    echo 'deactivate'
    deactivate
fi

PrjDir="${MySrcDir}/fidelity-account-overview"

ActivatePath="${PrjDir}/.venv/bin/activate"
echo "source ${ActivatePath}"
source $ActivatePath


pushd $PrjDir


./run.sh

popd