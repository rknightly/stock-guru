# Stock Guru
A web scraper that rates over 2,000 stocks based on data collected from several websites per stock.

Results published at [The Market Index](http://marketindex.weebly.com/)

## Setup
```bash
virtualenv env
. env/bin/activate
pip install -r requirements.txt
```

## Running
```bash
. env/bin/activate
python main.py
```

## Example Results
| Rating  | Ticker |Company Name                |
| --------| ------ |--------------------------- |
| 95      | AERI   | Aerie Pharmaceuticals, Inc.|
| 94.26   | BA     | Boeing Company (The)       |
|92.4	    |ENSG	   | The Ensign Group, Inc.     |
|91.39	  |SSNC	   | SS&C Technologies Holdings, Inc. |
|91.33	  |SKYW	   | SkyWest, Inc.              |
|90.94	  |SNPS	   | Synopsys, Inc.             |
|90.06	  |PWR	   | Quanta Services, Inc.      |
|...	    |...	   | ...                        |
