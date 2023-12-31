

echo '######## creating venv'
python3 -m venv ../venv

echo '######## activating venv'
source ../venv/bin/activate

echo '####### installing python requirements in venv (editable + normal libs)'
pip3 install -r ../requirements.test.txt

echo '####### bundling with pyinstaller'
pyinstaller renardo_bundle.py \
    --collect-all renardo_lib \
    --collect-all FoxDotEditor \
    --collect-all renardo \
    --hidden-import wave \
    --hidden-import psutil \
    --clean \
    --distpath ./renardo_linux
    # --workpath ../renardooo_build \

echo '####### injecting samples in the result'
#git clone https://github.com/e-lie/renardo_samples.git ../renardo_samples
cp -Rv ../renardo_samples renardo_linux/

echo '####### create archive'
tar -czvf renardo_linux.tar.gz renardo_linux

