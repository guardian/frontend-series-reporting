make-empty-dist:
	if [ -d "dist" ]; \
	then \
		rm -Rf dist ; \
	fi;
	mkdir dist

copy-site-packages:
	cp -R ./lib/python2.7/site-packages/* dist/

copy-all-python:
	cp -R ./*.py ./*.sql dist/

copy-custom-psycopg2:
	cp -R ./awslambda_psycopg2/ dist/psycopg2/

make-lambda-zip:
	cd dist/ ; \
	zip -r function ./

build: make-empty-dist copy-site-packages copy-all-python copy-custom-psycopg2 make-lambda-zip