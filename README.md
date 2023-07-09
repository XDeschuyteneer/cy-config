# cy-config
Cyanview device configuration library

## Usage

Install dependencies:
```bash
pip install -r requirements.txt
```

Update the main.py rcp/rio ip.
Then run:

```bash
./main.py
```

It will create:
* an ATEM on RCP
* setup remi on RIO/RCP
* 3 cams on RIO
* import 2 cams from RIO to RCP
* create 3rd cam on RCP
* 2 boxio on RCP
* link 3 channels to 3 RCP cams