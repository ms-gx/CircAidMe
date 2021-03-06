# CircAidMe

CircAidMe is a tool designed to analyze data generated with [CircAID-p-seq for Oxford Nanopore Technologies](https://www.immaginabiotech.com/product/circaid-p-seq/).

In brief, it detects known adapter sequences used by CircAID-p-seq kit for every Oxford Nanopore read. After having detected the adapters it will extract the embedded insert sequences and calculate a consensus sequence for the insert.

CircAidMe was designed and implemented by Genexa (genexa.ch) in collaboration with Immagina Biotechnology. CircAidMe is free software and it is licensed under GPLv3.


# Table of contents

* [Requirements](#requirements)
* [Installation](#installation)
    * [Install from source](#install-from-source)
    * [Build and run without installation](#build-and-run-without-installation)
    * [Install via PyPI](#install-via-pypi)
* [Usage examples](#usage-examples)
* [Output of a CircAidMe run](#output-of-a-circaidme-run)
* [Full usage](#full-usage)
* [How it works](#how-it-works)
* [Known limitations](#known-limitations)
* [License](#license)
    


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
mkdir /home/user/testdir # make a test directory
circaidme-test /home/user/testdir # all tests have to pass with "OK"
rm -R /home/user/testdir # remove test directory if tests passed
```

Notes:
* If `python3 setup.py install` complains about permissions since you want to install it system-wide you have to run it with `sudo`
* Install just for your user: `python3 setup.py install --user`
* Install to a specific location: `python3 setup.py install --prefix=$HOME/.local`
* Install with pip (local copy, you might have to install Python package `wheel`): `pip3 install path/to/CircAidMe`
* Install with pip (from GitHub, you might have to install Python package `wheel`): `pip3 install git+https://github.com/ms-gx/CircAidMe.git


### Build and run without installation

By simply running `make` in CircAidMe's directory, you can compile the C++ components but not install an executable. The program can then be executed by directly calling the `circaidme-runner.py` script.

```bash
git clone https://github.com/ms-gx/CircAidMe.git
cd CircAidMe
make
./circaidme-runner.py -h
# test the installation with a toy data set inlcuded in the package:
mkdir /home/user/testdir # make a test directory
./circaidme-test.py /home/user/testdir # all tests have to pass with "OK"
rm -R /home/user/testdir # remove test directory if tests passed
```


### Install via PyPI

Installation via PyPI repository will be added later.



# Usage examples

__Minimally parameterized run of CircAidMe:__<br>
`circaidme --input-file input_reads.fastq --out-path path/to/output --adapter-name ADAPTER_NAME`

__If you want to overwrite the previous run use flag `--force-overwrite`:__<br>
`circaidme --input-file input_reads.fastq --out-path path/to/output --adapter-name ADAPTER_NAME --force-overwrite`

__Add an additional tag to the result names by setting parameter `--tag` (for example usefull when running CircAidMe with a different parametrization):__<br>
`circaidme --input-file input_reads.fastq --out-path path/to/output --adapter-name ADAPTER_NAME --tag TAG`

__Run CircAidMe multi-core with parameter `--threads`:__<br>
`circaidme --input-file input_reads.fastq --out-path path/to/output --adapter-name ADAPTER_NAME --threads N`

__CircAidMe does not exlcude "forward" inserts by setting parameter `--keep-forward`:__<br>
`circaidme --input-file input_reads.fastq --out-path path/to/output --adapter-name ADAPTER_NAME --keep-forward`



# Output of a CircAidMe run

CircAidMe outputs four files:
* *basename*.fasta: Contains the consensus sequences generated from CircAID-p-seq data (one consensus sequence per Oxford Nanopore (sub-)read -- not every (sub-)read results in a consensus sequence!).
* *basename*.csv: Contains statistics for every Oxford Nanopore (sub-)read analyzed. No matter if it results in a consensus sequence or not.
* *basename*.log: A logfile containing the parameterization of the CircAidMe run and some basic statistics.
* *basename*\_removed\_reads.fasta: Contains all Oxford Nanopore (sub-)reads which do not result in a consensus sequence. The reason for getting excluded is given in the Fasta headers. This is useful for debugging.


# Full usage

```
usage: circaidme [-h] --input-file INPUT_FILE --out-path OUT_PATH
                 --adapter-name ADAPTER_NAME [--adapter-list ADAPTER_LIST]
                 [--force-overwrite] [--tag TAG]
                 [--refine-adapter-alignment {True,False}]
                 [--min-inserts MIN_INSERTS] [--cons-min-len CONS_MIN_LEN]
                 [--cons-max-len CONS_MAX_LEN] [--keep-forward]
                 [--no-store-removed-reads] [--iter-first-muscle {1,2,3}]
                 [--iter-second-muscle {1,2,3,4}] [--threads THREADS]
                 [--version]

CircAidMe v0.1.0 -- Tool for the analysis of CircAID-p-seq data -- Designed
and implemented by Genexa AG, Switzerland (genexa.ch) & Immagina BioTechnology
S.R.L., Italy (immaginabiotech.com)

required arguments:
  --input-file INPUT_FILE
                        FASTA/FASTQ file with CircAID-p-seq data (default:
                        None)
  --out-path OUT_PATH   path to store results (also used for temp files)
                        (default: None)
  --adapter-name ADAPTER_NAME
                        define which adapter to be used OR "ALL" for all the
                        available adapters OR "LIST" if you want to provide
                        the list of adapters to be used with argument "--
                        adapter-list". Predefined adapters are: "Luc20_DNA,
                        ADR7391_RNA, ADR1_RNA, ADR2_RNA, ADR3_RNA,ADR4_RNA,
                        ADR1572_RNA, ADR1859_RNA, ADR2520_RNA, ADR2858_RNA,
                        ADR323_RNA, ADR4314_RNA, ADR4557_RNA, ADR4885_RNA,
                        ADR5555_RNA" (default: None)

optional arguments:
  --adapter-list ADAPTER_LIST
                        for user-defined adapter list (comma separated list)
                        (default: None)
  --force-overwrite     set flag if you want to overwrite result files
                        (default: False)
  --tag TAG             tag to be added to the output FASTA file (default:
                        none)
  --refine-adapter-alignment {True,False}
                        choose if adapter alignment has to be refined
                        (default: True)
  --min-inserts MIN_INSERTS
                        number of inserts which have to be present in order to
                        calculate a consensus sequence (default: 2)
  --cons-min-len CONS_MIN_LEN
                        minimal length of the consensus sequence (default: 15)
  --cons-max-len CONS_MAX_LEN
                        maximal length of the consensus sequence (default: 40)
  --keep-forward        set flag if reads with only "forward" inserts must be
                        kept (default: False)
  --no-store-removed-reads
                        set flag if removed reads do NOT have to be written to
                        a separate FASTA file (default: False)
  --iter-first-muscle {1,2,3}
                        number of iterations MUSCLE has to perform for first
                        MSA calculation (default: 2)
  --iter-second-muscle {1,2,3,4}
                        number of iterations MUSCLE has to perform for second
                        MSA calculation (default: 3)
  --threads THREADS     number of threads to be used (default: 1)
  --version             show program's version number and exit

```



# How CircAidMe works

A in-depth description of CircAidMe can be found [here](HOWITWORKS.md).



# Known limitations
* CircAidMe at this stage does not support Gzipped input or output (`*.fastq.gz`or `*.fasta.gz`). Might be addressed later if needed.
* CircAidMe has multi-core support (parameter `--threads`). However, the speed does not scale perfectly linear. Can be improved at a later stage.



# License

[GNU General Public License, version 3](https://www.gnu.org/licenses/gpl-3.0.html)
