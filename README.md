-- Installation :
git clone https://github.com/Tatalette/TPIA_Gateway.git
cd TPIA_Gateway

-- Environnement : 
#Complete Version
conda env create -f environment.yml
#Light version (without dependencies)
conda env create -f environmentLightVersion.yml
#Pdf version (obsolete)
conda env create -f environmentPdfVersion.yml

-- Concerning pip :
I try to use it for torch, but the downloading time was taking me down.
I recommand Conda.

-- Use :
Basic function:
python -m cli.main path/to/your/file.py
Advanced function (whole project):
python -m cli.main . --recursive
ACEOB optimization suggestion :
python -m cli.main path/to/file.py --suggest
Json output :
python -m cli.main . --recursive --output json --output-file report.json
Disabling checking :
python -m cli.main . --no-pylint --no-algorithm

-- Configuration :
Example :
style:
  snake_case: true
  camel_case: true
  trailing_whitespace: true
  quotes: true
pylint:
  enabled: true
  ignore: ["C0114", "C0116"]   # ignore missing docstring warnings
algorithm:
  enabled: true
  keywords_threshold: 1

-- Dataset ACEOB
The tool can suggest concrete optimisations using the ACEOB dataset.
It automatically downloads and indexes the dataset on the first run. You can control the number of examples used by editing sample_size in ai/code_indexer.py (default 5000).
VSCode Extension (Coming Soon)

-- Futur update
A Visual Studio Code extension is in development. Once published, you'll be able to run reviews directly from the editor with diagnostics and quick fixes.

Remerciement :
ACEOB team for the open datasets concerning python optimization code.