#!/bin/sh

# update modules
npm update

# generate deployable artifacts
npm run build

# copy artifacts to local server directory
rsync -rpv --delete-after build/* ../server/data/public/

echo "client application deployed to server directory."
