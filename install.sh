#! /bin/bash

echo "Uninstalling..." &&
pip uninstall acmm -y > /dev/null &&
echo "Building..." &&
rm ./dist -rf &&
python3 -m build > /dev/null &&
echo "Installing..." &&
pip install dist/acmm*.whl > /dev/null