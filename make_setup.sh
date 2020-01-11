set -eu
name=$1
poetry build
tar zxvf dist/$name.tar.gz
mv $name/setup.py .
trash $name
code setup.py