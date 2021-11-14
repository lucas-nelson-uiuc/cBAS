# College Basketball Analysis Scoresheet System (cBASS)

![newer Text](https://media.giphy.com/media/y7X27SNnBws4KhhXTB/giphy.gif)

## Installation

**Clone this repository from the command line** by running the following command (must have `git` installed)

```
$ git clone https://github.com/lucas-nelson-uiuc/cBASS.git
```

(Optional) **Create a virtual envrionment** and activate virtual environment. For current and future uses, this environment must be active in order to run the script.

```
$ python3 -m venv name-of-virtual-environment
$ . name-of-virtual-environment/bin/activate
```

**Install required packages**. If package cannot be installed, remove package from `requirements.txt` and run `pip install -r requirements.txt` again

```
$ pip install -r requirements.txt
```

The environment should be set to run!

## Men's CBB Data

Locate the directory for the `cBASS` repository and `cd` into `mens_cbb`. Run `python3 cbbMens.py` and follow the on-screen prompts. The resulting `.xlsx` file will be saved to the same repository, but can be changed in the source file.

```
$ cd mens_cbb
$ python3 cbbMens.py
```

## Women's CBB Data

Locate the directory for the `cBASS` repository and `cd` into `womens_cbb`. Run `Rscript cbbWomens.R` and follow the on-screen prompts. The resulting `.xlsx` file will be saved to the same repository, but can be changed in the source file.

```
$ cd womens_cbb
$ Rscript cbbWomens.R
```
