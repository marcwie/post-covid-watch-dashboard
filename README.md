# Premise

A dashboard to display wearable data collected in the [WATCH Project](https://www.uniklinikum-jena.de/cscc/Post_COVID_Zentrum/WATCH.html).

*WATCH – Mobile care close to home to manage cross-sector therapy for post-COVID-19 in Thuringia* is the name of the new care and therapy study at Jena University Hospital. 

The aim of the project is to improve the care structure and participation for Long COVID patients in rural areas. Towards this end, a bus is being converted into a mobile post-COVID ambulance, the so-called PoCO bus. The bus enables those affected to be examined and cared for close to home. Those affected will complete 12 weeks of training units on concentration and attention (BRAIN module), phased rehabilitation sports programmes (BODY module) and behavioural-therapy-related therapy offers (SOUL module).

# Installation

The package requires [poetry](https://python-poetry.org/). Make sure to have it installed and run `make install` after cloning this repository to install all dependencies.

# Setup

After gaining data access you will receive credentials for downloading. You can then create a file named `.env` in the root of the repository using the following template and filling in your credentials. Do not add this file to your git repository.

```
URL=
USER=
PW=
ZIPPW=
```

You can then download all data using ```make download```. You also need an `.xlsx` file containing data collected during outpatient visits to the PoCO bus. Put this file in `data/00_external` and adjust `data.files.users` in `config/main.yaml` accordingly. 

# Visualize

After finishing setup you can start the dashboard locally by first activating the virtual environment using `make activate`. Then type `make dashboard`. This should open a web-browser displaying the dashboard. Navigate to `localhost:8502` if the browser doesn't open the dashboard automatically.
