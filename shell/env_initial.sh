#!/usr/bin/env bash

env_dir=$(pwd)/env
virtualenv_dir=${env_dir}/py27
buildout_dir=${env_dir}/buildout

# virtualenv init
rm -r ${env_dir}
[ -d ${env_dir} ] && echo "${env_dir} is exist;please don't rerun this script" && exit 1

mkdir ${env_dir}
virtualenv -ppython2.7 ${virtualenv_dir}

# buildout init
source ${virtualenv_dir}/bin/activate
mkdir ${buildout_dir}
python2.7 bootstrap-buildout.py buildout:directory=${buildout_dir} -c buildout.cfg
${buildout_dir}/bin/buildout buildout:directory=${buildout_dir} -U
deactivate
