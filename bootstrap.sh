[ ! -f bin/pip ] && virtualenv .
bin/pip install --upgrade pip setuptools zc.buildout
bin/buildout -c $1 annotate | tee annotate.txt | grep -E 'setuptools= |zc.buildout= ' | sed 's/= /==/' > requirements.txt
cat annotate.txt
cat requirements.txt
bin/pip install --upgrade -r requirements.txt

