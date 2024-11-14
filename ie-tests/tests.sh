#!/bin/bash

TEST_FOLDER=$1

echo " "
echo "Changing folder to ${TEST_FOLDER}"

cd $TEST_FOLDER

echo " "
echo " Cleaning ..."
mvn clean

echo " "
echo " Running tests..."
# Run maven tests 
mvn test -fn 

echo " "
echo " Finished."
