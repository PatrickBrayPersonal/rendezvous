# rendezvous
DVA Project
use our public application at https://rendezvous.streamlit.app/
## Installation
- Download python 3.7 (I chose this cus we used it for HW1)
- From the project directory, create environment
    - `virtualenv --python=3.7 env`
- Activate environment
    - Windows: `env\Scripts\activate`
- Install Requirements
    - `pip install -r requirements.txt`
- Install local rendez package
    - `pip install -e .`

## Environment Variables
add a file called "secrets.toml" to the `.streamlit` directory under `rendezvous`
add a single line to the file
API_KEY = <GOOGLE PLACES API KEY>
This will be the places api key used by the program
[Streamlit Secrets](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

## Optimizer
Passing data into the optimizer

### Graph
- nodes - businesses + single node for user's current location 

- edges - eligible travel links from one business to the next  
    - weight - distance, haversine (or time if you're ambitious)

Further detail can be found [here](https://gtvault.sharepoint.com/:w:/r/sites/DVAProject188/_layouts/15/Doc.aspx?action=edit&sourcedoc=%7B75f210af-3a92-469f-a8e6-f7c313652ad9%7D&wdOrigin=TEAMS-ELECTRON.teamsSdk.openFilePreview&wdExp=TEAMS-CONTROL&web=1)

### Usage
See the example code in `scripts/test_optimizer.py` for using the optimizer.

Create dataframes that resember the csv files present in `test_data/test_edges.csv` and `test_data/test_nodes.csv`.

Pass those dataframes and your desired parameters into the optimizer.
