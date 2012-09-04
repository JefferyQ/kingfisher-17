#!/bin/sh

. env/bin/activate
mkdir -p env/tmp
exec nosetests \
    --with-doctest \
    --with-coverage --cover-html --cover-html-dir=env/tmp \
    --cover-package=kingfisher \
    -m '/^kingfisher/'
