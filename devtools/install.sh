#!/bin/bash

INSTALL_MODE=${1:-install}

export DATE=`date +%Y-%m-%d`
export ENV_NAME=${ENV_NAME:-football}
export CPU_ONLY=${CPU_ONLY:-0}
export CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

unamestr=`uname`
if [[ "$unamestr" == 'Darwin' ]];
then
    echo "Using OSX Conda"
    export CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh
    export CPU_ONLY=1
    export ENVIRONMENT_YML="devtools/environment.yml"
else
    export ENVIRONMENT_YML="devtools/environment.yml"
fi

export CONDA_EXISTS=`which conda`
if [[ "$CONDA_EXISTS" = "" ]];
then
    wget ${CONDA_URL} -O anaconda.sh;
    bash anaconda.sh -b -p `pwd`/anaconda
    export PATH=`pwd`/anaconda/bin:$PATH
else
    echo "Using Existing Conda"
fi

# Install Libraries
conda env create --name=${ENV_NAME} -f devtools/environment.yml
echo "Installed $ENV_NAME conda environment"
