[ ! -f bin/pip ] && virtualenv .
[ ! -f bin/buildout ] && bin/pip install --upgrade pip zc.buildout
bin/buildout -c $1 annotate | tee annotate.txt | grep -E 'setuptools= |zc.buildout= ' | sed 's/= /==/' > requirements.txt
cat annotate.txt
cat requirements.txt
bin/pip install --upgrade -r requirements.txt

