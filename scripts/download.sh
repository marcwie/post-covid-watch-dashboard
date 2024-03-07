source .env
wget --user $USER --password $PW -O data/01_raw/export.7z $URL
7za x data/01_raw/export.7z -p$ZIPPW -odata/01_raw
rm data/01_raw/export.7z