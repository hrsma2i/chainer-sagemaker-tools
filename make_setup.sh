set -eu
name=$1
poetry build
tar zxvf dist/$name.tar.gz
mv $name/setup.py .
trash $name
trash dist
code setup.py