# A Dashboard to Calculate Rheological Properties from 6-Speed API Viscometer Measurements

## Installation

In the  terminal from the home directory, use the command git clone, then paste the link from your clipboard, or copy the command and link from below:

```bash
git clone https://github.com/sercangul/apiviscometer.git
```

Change directories to the new ~/FluidLab_GUI directory:

```bash
cd apiviscometer
```

To ensure that your master branch is up-to-date, use the pull command:

```bash
git pull https://github.com/sercangul/apiviscometer.git
```

Install required python packages using requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

Change directories to the new ~/apiviscometer directory:

```bash
cd apiviscometer
```

Run the script using Streamlit:

```bash
streamlit run app.py
```

The same app is also deployed to Heroku: http://apiviscometer.herokuapp.com/

Enter your dial readings obtained from a 6-speed API viscometer and investigate the rheological behavior of your fluid with curve fit results provided for Bingham Plastic, Power-Law and Yield-Power Law rheological models.
