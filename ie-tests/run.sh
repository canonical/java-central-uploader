#!/bin/bash

function run_tests(){
    echo "START TEST"
    IE_FOLDER=$(pwd)

    FOLDER="${IE_FOLDER}/.."

    DATE=$(date +%Y%m%dH%HM%M)
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    COMMIT=$(git rev-parse --short HEAD)

    LOG_NAME=${DATE}_${BRANCH}_${RANDOM}_test

    mkdir -p "${IE_FOLDER}/logs"

    STD_OUT="${IE_FOLDER}/logs/${LOG_NAME}.out"
    STD_ERR="${IE_FOLDER}/logs/${LOG_NAME}.err"

    # populate the error file
    echo "" >> $STD_ERR

    echo "***************************************" > $STD_OUT
    echo "     INTEGRATION TESTS" >> $STD_OUT
    echo "***************************************" >> $STD_OUT
    echo "" >> $STD_OUT
    echo "Date: ${DATE}" >> $STD_OUT
    echo "Branch: ${BRANCH}" >> $STD_OUT
    echo "Commit: ${COMMIT}" >> $STD_OUT
    echo "LogName: ${LOG_NAME}" >> $STD_OUT
    echo "" >> $STD_OUT
    echo "***************************************" >> $STD_OUT
    echo "" >> $STD_OUT

    FORMAT_TIME="\n***************************************\nTIMINGS:\n%E real\n%U user\n%S sys"
    ls
    echo "Before running the test!"
    ./tests.sh "${FOLDER}" >> $STD_OUT 2> $STD_ERR

    echo "***************************************" >> $STD_OUT
}

BRANCH=$*

if [ -z "$BRANCH" ];
then 
    BRANCH="release-3.3.6-ubuntu2"
fi

echo "Branch: ${BRANCH}"
git checkout $BRANCH
run_tests
