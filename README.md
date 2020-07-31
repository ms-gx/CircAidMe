# CircAidMe



# Table of contents

* [Requirements](#requirements)
* [Installation](#installation)
    * [Install from source](#install-from-source)
    * [Build and run without installation](#build-and-run-without-installation)
    


# Requirements

* Linux
* [Python](https://www.python.org/) 3.5 or later
* Python packages: Biopython, pandas, regex 
* C++ compiler


CircAidMe is currently not running on macOS or Windows. However, porting it to macOS should be possible without much effort. Please let us know if you need support for macOS or just fork the project and make a pull request.



#  Installation

### Install from source

Running the `setup.py` script will compile the C++ components of CircAidMe and install a `circaidme` executable:

```bash
git clone https://github.com/ms-gx/CircAidMe.git
cd CircAidMe
python3 setup.py install
circaidme -h
# test the installation with a toy data set inlcuded in the package:
mkdir /home/user/testdir # make any new and empty test directory
circaidme-test /home/user/testdir # all tests have to pass with "OK"
```

Notes:
* If `python3 setup.py install` complains about permissions since you want to install it system-wide you have to run it with `sudo`.
* Install just for your user: `python3 setup.py install --user`
* Install to a specific location: `python3 setup.py install --prefix=$HOME/.local`
* Install with pip (local copy): `pip3 install path/to/CircAidMe`
* Install with pip (from GitHub): `pip3 install git+https://github.com/ms-gx/CircAidMe.git


### Build and run without installation

By simply running `make` in CircAidMe's directory, you can compile the C++ components but not install an executable. The program can then be executed by directly calling the `circaidme-runner.py` script.

```bash
git clone https://github.com/ms-gx/CircAidMe.git
cd CircAidMe
make
./circaidme-runner.py -h
# test the installation with a toy data set inlcuded in the package:
mkdir /home/user/testdir # make any new and empty test directory
./circaidme-test.py /home/user/testdir # all tests have to pass with "OK"
```
