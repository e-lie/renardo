

echo '######## creating venv'
python3 -m venv ../venv

echo '######## activating venv'
source ../venv/bin/activate

echo '####### installing python requirements in venv (editable + normal libs)'
pip3 install -r ../requirements.pyinstaller.txt

echo '####### bundling with pyinstaller'
pyinstaller renardo_bundle.py \
    --collect-all renardo_gatherer \
    --collect-all renardo_lib \
    --collect-all FoxDotEditor \
    --collect-all renardo \
    --collect-all textual \
    --clean \
    --distpath ./renardo

#echo '####### create archive'
#tar -czvf renardo_linux.tar.gz renardo_linux

