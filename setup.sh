#!/bin/bash

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";

# I want to be able to get the latest automatically, but for now I just
# grab the version that is the latest online. If Google would give latest
# a static name then we could easily change.
AE_PYTHON_VERSION="1.9.28";
AE_PYTHON_NAME="google_appengine";
AE_PYTHON_ZIP_NAME="${AE_PYTHON_NAME}_${AE_PYTHON_VERSION}.zip";
AE_PYTHON_LOCATION="https://storage.googleapis.com/appengine-sdks/featured/";
AE_PYTHON_REMOTE_FILE=$AE_PYTHON_LOCATION$AE_PYTHON_ZIP_NAME;
AE_PYTHON_LOCAL_DIR="$ROOT_DIR/$AE_PYTHON_NAME";

UFO_MS_NAME="ufo-management-server-master"
UFO_MS_GIT_REPO="https://github.com/uProxy/ufo-management-server.git";
UFO_MS_LOCAL_DIR="$ROOT_DIR/$UFO_MS_NAME/";
UFO_MS_LOCAL_LIB="$ROOT_DIR/lib";

TEMP_BASH_PROFILE=".bash_profile";

# A simple bash script to run commands to setup and install all dev dependencies
# (including non-npm ones)
function runAndAssertCmd ()
{
    echo "Running: $1"
    echo
    # We use set -e to make sure this will fail if the command returns an error
    # code.
    set -e && cd $ROOT_DIR && eval $1
}

function setupAppEngine ()
{
  runAndAssertCmd "wget $AE_PYTHON_REMOTE_FILE"
  runAndAssertCmd "unzip $AE_PYTHON_ZIP_NAME"
  runAndAssertCmd "rm -fr $AE_PYTHON_ZIP_NAME"
}

function addVendorPackage ()
{
  runAndAssertCmd "mkdir $UFO_MS_LOCAL_LIB"
  runAndAssertCmd "pip install -t $UFO_MS_LOCAL_LIB google-api-python-client pycrypto"
}

function AddAppEngineRuntimePackages ()
{
  runAndAssertCmd "pip install WebTest"
  runAndAssertCmd "pip install Jinja2"
  runAndAssertCmd "pip install pyyaml"
}

function addAllExports ()
{
  runAndAssertCmd "touch $TEMP_BASH_PROFILE"
  runAndAssertCmd "echo export PATH=$PATH:$AE_PYTHON_LOCAL_DIR:$AE_PYTHON_LOCAL_DIR/:$AE_PYTHON_LOCAL_DIR/lib:$AE_PYTHON_LOCAL_DIR/lib/:$AE_PYTHON_LOCAL_DIR/lib/webapp2-2.5.2:$AE_PYTHON_LOCAL_DIR/lib/webapp2-2.5.2/:$AE_PYTHON_LOCAL_DIR/lib/webob-1.2.3:$AE_PYTHON_LOCAL_DIR/lib/webob-1.2.3/:$UFO_MS_LOCAL_LIB:$UFO_MS_LOCAL_LIB/ >> $TEMP_BASH_PROFILE"
  runAndAssertCmd "echo export PYTHONPATH=$PYTHONPATH:$AE_PYTHON_LOCAL_DIR:$AE_PYTHON_LOCAL_DIR/:$AE_PYTHON_LOCAL_DIR/lib:$AE_PYTHON_LOCAL_DIR/lib/:$AE_PYTHON_LOCAL_DIR/lib/webapp2-2.5.2:$AE_PYTHON_LOCAL_DIR/lib/webapp2-2.5.2/:$AE_PYTHON_LOCAL_DIR/lib/webob-1.2.3:$AE_PYTHON_LOCAL_DIR/lib/webob-1.2.3/:$UFO_MS_LOCAL_LIB:$UFO_MS_LOCAL_LIB/ >> $TEMP_BASH_PROFILE"
  runAndAssertCmd "source $TEMP_BASH_PROFILE"
}

function setupUnitTest ()
{
  setupAppEngine
  addVendorPackage
  AddAppEngineRuntimePackages
  addAllExports
}

function setupManagementServer ()
{
  runAndAssertCmd "git clone $UFO_MS_GIT_REPO"
  runAndAssertCmd "cp $UFO_MS_LOCAL_DIR/* . -r"
  runAndAssertCmd "rm -fr $UFO_MS_LOCAL_DIR"
  setupUnitTest
}

if [ "$1" == 'install' ]; then
  setupManagementServer
elif [ "$1" == 'unit_test' ]; then
  setupUnitTest
elif [ "$1" == 'add_exports' ]; then
  addAllExports
else
  echo
  echo "Usage: setup.sh [install|unit_test]"
  echo
  echo "  install      - Sets up the entire project from github."
  echo "  unit_test    - Prepares the machine for unit testing."
  echo "  add_exports  - Add environment exports for variable setup."
  echo
  exit 0
fi
