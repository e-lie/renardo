

echo '######## creating venv'
python3 -m venv venv

echo '######## activating venv'
source venv/bin/activate

echo '######## getting renardo parts from github'
git clone https://github.com/e-lie/renardo.git ../renardo
git clone https://github.com/e-lie/FoxDotEditor.git ../FoxDotEditor
git clone https://github.com/e-lie/renardo_sitter.git ../renardo_sitter
git clone https://github.com/e-lie/renardo_samples.git ../renardo_samples

echo '####### installing python requirements in venv (editable + normal libs)'
pip3 install -r requirements.txt

echo '####### bundling with pyinstaller'
pyinstaller renardo_bundle.py \
    --collect-all renardo \
    --collect-all FoxDotEditor \
    --collect-all renardo_sitter \
    --hidden-import wave \
    --hidden-import psutil \
    --clean \
    --distpath ./renardo_linux
    # --workpath ../renardooo_build \

echo '####### injecting samples in the result'
cp -Rv ../renardo_samples renardo_macos/

echo '####### create archive'
tar -czvf renardo_macos.tar.gz renardo_macos

