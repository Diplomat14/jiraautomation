echo off

rem Installing dependencies
mkdir "dependencies"
cd ./dependencies

git clone https://github.com/Diplomat14/xdev
git clone https://github.com/Diplomat14/jiraorm
git clone https://github.com/Diplomat14/jiraautomation


pip uninstall -y jiraautomation
pip uninstall -y jiraorm
pip uninstall -y xdev


pip install -e ./xdev
pip install -e ./jiraorm
pip install -e ./jiraautomation
cd ..

rem Installing package
rem pip install -e .

rem Preparing default folders for scripts
mkdir "results"

rem testing command line
echo
echo
echo
arcjiraautomation-main