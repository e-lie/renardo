export RENARDO_VERSION="1.0.0.dev23"

echo '######## creating venv'
python3 -m venv ../venv

echo '######## activating venv'
source ../venv/bin/activate

echo '####### installing python requirements in venv (editable + normal libs)'
pip3 install -r ../requirements.pyinstaller.txt

echo '####### bundling with pyinstaller'
export DISTP="/tmp/renardo-$RENARDO_VERSION"
mkdir -p $DISTP
pyinstaller "renardo-entrypoint.py" \
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

#echo '####### create archive'
tar -czvf "$DISTP/renardo-$RENARDO_VERSION.tar.gz" "$DISTP/renardo-$RENARDO_VERSION"

