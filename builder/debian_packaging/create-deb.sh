
# Launch bundle_linux.sh to create renardo binary in /tmp

# edit renardo/debian/control to change metadata if needed

cp /tmp/renardo-0.9.13/renardo-0.9.13 ./renardo/renardo

cd renardo

sudo dpkg-buildpackage -us -uc
