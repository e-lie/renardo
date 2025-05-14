export RENARDO_VERSION="1.0.0.dev23"

echo '######## creating venv'
rm -Rf /tmp/venv_pyinstaller
python3 -m venv /tmp/venv_pyinstaller

echo '######## activating venv'
source /tmp/venv_pyinstaller/bin/activate

echo '####### installing python requirements in venv (editable + normal libs)'
pip3 install renardo==$RENARDO_VERSION
pip3 install -r ../../requirements.pyinstaller.txt --no-cache-dir --upgrade

echo '####### bundling with pyinstaller'
export DISTP="/tmp/renardo-$RENARDO_VERSION"
mkdir -p $DISTP
pyinstaller "../renardo-entrypoint.py" \
    --name "renardo-$RENARDO_VERSION" \
    --collect-all renardo.gatherer \
    --collect-all renardo_lib \
    --collect-all FoxDotEditor \
    --collect-all renardo \
    --collect-all textual \
    --clean \
    --noconfirm \
    --distpath $DISTP \
    --workpath "/tmp/renardo_pyinstaller_build"

echo '####### create archive'
cd $DISTP && tar -czvf "renardo-$RENARDO_VERSION-linux.tar.gz" "renardo-$RENARDO_VERSION"

