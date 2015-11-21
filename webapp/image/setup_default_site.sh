#!/bin/bash

# Copy image files
mkdir -p /var/www/html/files
cp -r /var/www/okeanos-LoD/webapp/frontend/public/assets/img/ /var/www/html/files

# Copy js and css files
mkdir -p /var/www/html/files/js
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/dist/js/app.min.js /var/www/html/files/js/
mkdir -p /var/www/html/files/css
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/dist/css/AdminLTE.min.css /var/www/html/files/css
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/dist/css/skins/skin-blue.css /var/www/html/files/css
mkdir -p /var/www/html/files/js/plugins/jQuery
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/plugins/jQuery/jQuery-2.1.4.min.js /var/www/html/files/js/plugins/jQuery/
mkdir -p /var/www/html/files/js/plugins/jQueryUI
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/plugins/jQueryUI/jquery-ui.min.js /var/www/html/files/js/plugins/jQueryUI/
mkdir -p /var/www/html/files/bootstrap/js
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/bootstrap/js/bootstrap.min.js /var/www/html/files/bootstrap/js/
mkdir -p /var/www/html/files/bootstrap/css
cp /var/www/okeanos-LoD/webapp/frontend/bower_components/AdminLTE/bootstrap/css/bootstrap.min.css /var/www/html/files/bootstrap/css/

# Copy default html
cp /var/www/okeanos-LoD/webapp/image/index.html /var/www/html

# Fetch jquery-plainoverlay js
wget --quiet https://raw.githubusercontent.com/anseki/jquery-plainoverlay/master/jquery.plainoverlay.min.js -P /var/www/html/files/js

