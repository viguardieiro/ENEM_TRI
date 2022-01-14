# Analysis of the Brazilian National High School Exam (ENEM) 

Codes for analysis of the questions of the Brazilian National High School Exam (ENEM).

Codes in Python and R.

## Getting Started

### Data

We use the microdata provided by the National Institute of Educational Studies and Research Anísio Teixeira (Inep), which are available per year [here](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem). 

To run the scripts, please download and save the microdata in `Data/Original/microdados_enem_(year)`.

The processed data will be saved in `Data/Processed/ENEM(year)`

### Setup

To process the data from an specific year, run this inside the `Scripts/` folder:

```
python ProcessEnem(year).py
```

## Description of files


Python/R Scripts:

filename                          |  description
----------------------------------|------------------------------------------------------------------------------------
ProcessEnem(year).py              |  Clean and process the microdata from the specific year.
EstimateScoresENEM(year).py       |  Fit a 3 parameters logistic model (ML3P) from Item Response theory (IRT) to estimate the participants scores for the specific year.


Python Notebooks:

filename                           |  description
-----------------------------------|------------------------------------------------------------------------------------
Compare Regions ENEM (year).ipynb  |  Analysis and comparison of the proportion of correct answers per question given the participants' score for each region of Brazil.
Compare Races ENEM (year).ipynb    |  Analysis and comparison of the proportion of correct answers per question given the participants' score for the main self-declared races.