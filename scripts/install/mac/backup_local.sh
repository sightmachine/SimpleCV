tar cvf usrlocal.tar /usr/local
sudo mv /usr/local /usr/local.bak
sudo mkdir /usr/local
sudo chown root:staff /usr/local
sudo chmod g+w /usr/local/
tar cvf pythonlibs.tar /Library/Python/2.6/site-packages
mv /Library/Python/2.6/site-packages /Library/Python/2.6/site-packages.bak 
sudo mkdir /Library/Python/2.6/site-packages
sudo chown root:staff /Library/Python/2.6/site-packages
sudo chmod g+w /Library/Python/2.6/site-packages
