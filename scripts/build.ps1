# Build a TW Blue installer.
# Must be called from root of repo
echo "Generating documentation..."
cd doc
python documentation_importer.py
python generator.py
mv documentation ..\src
cd ..
echo "done."

echo "Building binary..."
cd src
python setup.py build
cd ..
echo "done."
