#!/usr/bin/env bash

env_dir=$(pwd)/env
virtualenv_dir=${env_dir}/py27
buildout_dir=${env_dir}/buildout

# buildout rebuild
[ "${virtualenv_dir}" == "${VIRTUAL_ENV}" ] \
    && echo "you are in virtualenv: ${virtualenv_dir}." \
    || { echo "you are not in specified virtualenv: ${virtualenv_dir}." && venvflag="not_in_venv"; }

[ "${venvflag}" == "not_in_venv" ] \
    && source ${virtualenv_dir}/bin/activate \
    && echo "activate virtualenv: ${virtualenv_dir} "

${buildout_dir}/bin/buildout buildout:directory=${buildout_dir} -U

[ "${venvflag}" == "not_in_venv" ] \
    && deactivate \
    && echo "deactivate virtualenv: ${virtualenv_dir} "
