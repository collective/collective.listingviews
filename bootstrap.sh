[ ! -f venv/bin/pip ] && virtualenv-2.7 venv
venv/bin/pip install --upgrade pip setuptools zc.buildout
venv/bin/buildout -c $1 annotate | tee annotate.txt | grep -E 'setuptools *= *[0-9][^ ]*|zc.buildout *= *[0-9][^ ]*'| sed 's/= /==/' > requirements.txt
cat annotate.txt
cat requirements.txt
venv/bin/pip install --upgrade -r requirements.txt