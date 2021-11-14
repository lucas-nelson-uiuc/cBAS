# College Basketball Analysis Scoresheet System (cBASS)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![GitHub stars](https://badgen.net/github/stars/lucas-nelson-uiuc/cBASS)](https://GitHub.com/lucas-nelson-uiuc/cBASS)
[![GitHub issues](https://badgen.net/github/issues/lucas-nelson-uiuc/cBASS/)](https://GitHub.com/lucas-nelson-uiuc/cBASS/issues/)
[![GitHub pull-requests](https://img.shields.io/github/issues-pr/lucas-nelson-uiuc/cBASS.svg)](https://GitHub.com/lucas-nelson-uiuc/cBASS/pull/)

![Animated GIF of CLI usage](https://media.giphy.com/media/y7X27SNnBws4KhhXTB/giphy.gif)

---

## Installation

**Clone this repository from the command line** by running the following command (must have `git` installed)

```
$ cd path/to/new/folder
$ git clone https://github.com/lucas-nelson-uiuc/cBASS.git
```

Further installation is dependent on your preferred data needs. The women's data pipeline makes use of the [R language](https://www.r-project.org/), whereas the men's data pipeline makes use of the [Python language](https://www.python.org/).

Familiarity with either language is not required, but proper installation of either language is required. Please follow the recommendations from both websites above before continuning if your language of choice is not already installed on your computer.

---

## Men's CBB Data

**(Optional) Create a virtual envrionment**. If environment uses libraries not already installed on your local computer, this environment must be activated (see below) in order to run the script.

```
$ cd path/to/cBASS
$ python3 -m venv name-of-virtual-environment
$ . name-of-virtual-environment/bin/activate
```

**Install required packages**. If package cannot be installed, remove package from `requirements.txt` and run `pip install -r requirements.txt` again

```
$ pip install -r requirements.txt
```

Locate the directory for the `cBASS` repository and `cd` into `mens_cbb`. Run `python3 cbbMens.py` and follow the on-screen prompts. The resulting `.xlsx` file will be saved to the same repository, but can be changed in the source file.

```
$ cd mens_cbb
$ python3 cbbMens.py
```

Follow the on-screen instructions. After the script finishes, you'll find a `.xlsx` file in the same folder as you ran the `cbbMens.py` file (although this can be changed), which should look like `hometeam-awayteam-YYYY-MM-DD.xlsx`

---

## Women's CBB Data

**(Optional) Create an R Project** to isolate newly (if any) installed libraries. I'm not sure how to generate a `requirements.txt` equivalent for `R`, but the loaded packages are below. Installation of more packages could be required depending on the current state of your `R` packages.

```
library(wehoop)
library(tidyverse)
library(glue)
library(xlsx)
```

Locate the directory for the `cBASS` repository and `cd` into `womens_cbb`. Run `Rscript cbbWomens.R` and follow the on-screen prompts. The resulting `.xlsx` file will be saved to the same repository, but can be changed in the source file.

```
$ cd womens_cbb
$ Rscript cbbWomens.R
```

Follow the on-screen instructions. After the script finishes, you'll find a `.xlsx` file in the same folder as you ran the `cbbWomens.R` file (although this can be changed), which should look like `hometeam-awayteam-YYYY-MM-DD.xlsx`

---

# Issues

1. The `Boxscore()` function in the `sportsipy` package does not work for any games in the 2021-2022 season. Although this doesn't impact the performance of `cbbMens.py`, it does not allow for single game statistics for any given player. Therefore, all men's data is currently left as season aggregates.
2. The `cbbWomens.R` file takes some time. If anyone has recommendations for how to speed up the process, feel free to create an Issue with a recommendation or even a pull request with updated code.
3. Some pulls may seem invalid, but it could be due to a poorly timed URL/HTML request. Rerun the file if you come across a bad request or timeout error.
