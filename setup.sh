#!/bin/bash

# Get the directory where this script is and set ROOT_DIR to that path. This
# allows script to be run from different directories but always act on the
# directory it is within.
ROOT_DIR="$(cd "$(dirname $0)"; pwd)";
UP_DIR="$(cd ..; pwd)";

# I want to be able to get the latest automatically, but for now I just
# grab the version that is the latest online. If Google would give latest
# a static name then we could easily change.
AE_PYTHON_VERSION="1.9.30";
AE_PYTHON_NAME="google_appengine";
AE_PYTHON_ZIP_NAME="${AE_PYTHON_NAME}_${AE_PYTHON_VERSION}.zip";
AE_PYTHON_LOCATION="https://storage.googleapis.com/appengine-sdks/featured/";
AE_PYTHON_REMOTE_FILE=$AE_PYTHON_LOCATION$AE_PYTHON_ZIP_NAME;
AE_PYTHON_LOCAL_DIR="$ROOT_DIR/$AE_PYTHON_NAME/";
AE_PYTHON_GOOGLE="${AE_PYTHON_LOCAL_DIR}google/";
AE_PYTHON_GAE="${AE_PYTHON_GOOGLE}appengine/";
AE_PYTHON_API="${AE_PYTHON_GAE}api/";
AE_PYTHON_MEMCACHE="${AE_PYTHON_API}memcache/";
AE_PYTHON_EXT="${AE_PYTHON_GAE}ext/";
AE_PYTHON_NDB="${AE_PYTHON_EXT}ndb/";
AE_PYTHON_TESTBED="${AE_PYTHON_EXT}testbed/";
AE_PYTHON_LIB="${AE_PYTHON_LOCAL_DIR}lib/";
AE_PYTHON_WEBAPP="${AE_PYTHON_LIB}webapp2-2.5.2/";
AE_PYTHON_WEBOB="${AE_PYTHON_LIB}webob-1.2.3/";
AE_PYTHON_FANCY="${AE_PYTHON_LIB}fancy_urllib/";

AE_PYTHON_UP="$UP_DIR/$AE_PYTHON_NAME/";

UFO_MS_NAME="ufo-management-server-master"
UFO_MS_GIT_REPO="https://github.com/uProxy/ufo-management-server.git";
UFO_MS_LOCAL_DIR="$ROOT_DIR/$UFO_MS_NAME/";
UFO_MS_LOCAL_LIB="$UFO_MS_LOCAL_DIR/lib";

UFO_MS_UP="$UP_DIR/$UFO_MS_NAME/";

TEMP_BASH_PROFILE=".bash_profile";

UFO_TGZ="UfO-release.tgz"

# A simple bash script to run commands to setup and install all dev
# dependencies (including non-npm ones)
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

function addAppEngineRuntimePackages ()
{
  runAndAssertCmd "pip install Jinja2"
  runAndAssertCmd "pip install pyyaml"
}

function addTestingPackages ()
{
  runAndAssertCmd "pip install WebTest"
  runAndAssertCmd "pip install pytest"
  runAndAssertCmd "pip install nose"
  runAndAssertCmd "pip install mock"
}

function addAllExports ()
{
  runAndAssertCmd "touch $TEMP_BASH_PROFILE"
  runAndAssertCmd "echo export PATH=$PATH:$AE_PYTHON_LOCAL_DIR:$AE_PYTHON_API:$AE_PYTHON_MEMCACHE:$AE_PYTHON_EXT:$AE_PYTHON_NDB:$AE_PYTHON_TESTBED$AE_PYTHON_LIB:$AE_PYTHON_WEBAPP:$AE_PYTHON_WEBOB:$AE_PYTHON_FANCY:$UFO_MS_LOCAL_LIB >> $TEMP_BASH_PROFILE"
  runAndAssertCmd "echo export PYTHONPATH=$PYTHONPATH:$AE_PYTHON_LOCAL_DIR:$AE_PYTHON_API:$AE_PYTHON_MEMCACHE:$AE_PYTHON_EXT:$AE_PYTHON_NDB:$AE_PYTHON_TESTBED$AE_PYTHON_LIB:$AE_PYTHON_WEBAPP:$AE_PYTHON_WEBOB:$AE_PYTHON_FANCY:$UFO_MS_LOCAL_LIB >> $TEMP_BASH_PROFILE"
  runAndAssertCmd "source $TEMP_BASH_PROFILE"
}

function setupDevelopmentEnvironment ()
{
  if [ ! -d  "$AE_PYTHON_LOCAL_DIR" ] && [ ! -d  "$AE_PYTHON_UP" ]; then
    setupAppEngine
    addVendorPackage
    addAppEngineRuntimePackages
    addAllExports
    addTestingPackages
  else
    echo "Development environment already setup with appengine and packages."
  fi
}

function fixTravisCIEnvironment ()
{
  if [ ! -d  "$UFO_MS_LOCAL_DIR" ] && [ ! -d  "$AE_PYTHON_UP" ]; then
    TEMP_FILES="$(ls -A)"
    runAndAssertCmd "mkdir $UFO_MS_LOCAL_DIR"
    runAndAssertCmd "cp $TEMP_FILES $UFO_MS_LOCAL_DIR -r"
    runAndAssertCmd "rm -fr $TEMP_FILES"
  else
    echo "Code files already in proper directory."
  fi
}

function setupUnitTests ()
{
  fixTravisCIEnvironment
  setupDevelopmentEnvironment
}

function runUnitTests ()
{
  setupUnitTests
  runAndAssertCmd "python -m unittest discover -p '*_test.py'"
}

function package ()
{
  DIR_TO_PACKAGE="*"
  if [ -d  "$UFO_MS_LOCAL_DIR" ]; then
    DIR_TO_PACKAGE="$UFO_MS_NAME/*"
  elif [ -d  "$UFO_MS_UP" ]; then
    DIR_TO_PACKAGE="../$UFO_MS_NAME/*"
  else
    echo "Couldn't find UfO directory so packaging current dir."
  fi
  runAndAssertCmd "tar -czf $UFO_TGZ $DIR_TO_PACKAGE"
}

function release ()
{
  runUnitTests
  package
  # Not sure how to automatically push this while maintaining some control over
  # who can push. For right now, push will just be a manual step after the tgz
  # is generated.
  echo "Success! $UFO_TGZ has been generated. Please push it manually."
}

function deploy ()
{
  AE_FILE=""
  if [ -d  "$AE_PYTHON_LOCAL_DIR" ]; then
    AE_FILE="${AE_PYTHON_LOCAL_DIR}appcfg.py"
  elif [ -d  "$AE_PYTHON_UP" ]; then
    AE_FILE="${AE_PYTHON_UP}appcfg.py"
  else
    echo "$AE_PYTHON_NAME directory not found. Run './setup.sh setup_tests' to fix then retry."
  fi

  UFO_DIR="."
  if [ -d  "$UFO_MS_LOCAL_DIR" ]; then
    UFO_DIR="$UFO_MS_LOCAL_DIR"
  elif [ -d  "$UFO_MS_UP" ]; then
    UFO_DIR="$UFO_MS_UP"
  else
    echo "Couldn't find UfO directory so packaging current dir."
  fi

  if [ ! -z  "$AE_FILE" ]; then
    runAndAssertCmd "$AE_FILE -A uproxy-management-server update $UFO_DIR"
  fi
}

function setupManagementServer ()
{
  runAndAssertCmd "git clone $UFO_MS_GIT_REPO"
}

function installManagementServer ()
{
  setupManagementServer
  setupDevelopmentEnvironment
}

if [ "$1" == 'install' ]; then
  installManagementServer
elif [ "$1" == 'release' ]; then
  release
elif [ "$1" == 'deploy' ]; then
  deploy
elif [ "$1" == 'run_tests' ]; then
  runUnitTests
elif [ "$1" == 'setup_tests' ]; then
  setupUnitTests
else
  echo
  echo "Usage: setup.sh [install|release|deploy|run_tests|setup_tests]"
  echo
  echo "  install      - Sets up the entire project from github."
  echo "  release      - Runs the tests and generate a tgz if successful."
  echo "  deploy       - Uploads the local code copy to appspot."
  echo "  run_tests    - Prepares the machine for unit testing and runs."
  echo "  setup_tests  - Prepares the machine for unit testing."
  echo
  exit 0
fi
