# High Proper Motion Stars (HPMS) Finder

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Advanced Options](#advanced-options)
- [Examples](#examples)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## Introduction

Welcome to the **High Proper Motion Stars (HPMS) Finder**! This Python-based tool allows astronomers and enthusiasts to identify and visualize high proper motion stars visible from Strasbourg at a specified local observation time. Leveraging data from the SIMBAD Astronomical Database via the TAP (Table Access Protocol) service, HPMS provides up-to-date information on stars with significant proper motion, enabling users to track their movement and visibility in the night sky.

## Features

- **Query High Proper Motion Stars:** Retrieve stars with proper motion exceeding a specified threshold.
- **Time-Based Position Updates:** Calculate and display updated positions based on proper motion for a given observation time.
- **Visibility Check:** Determine which stars are above a minimum altitude (e.g., 30 degrees) from Strasbourg at the specified time.
- **Sorting Options:** Sort the list of visible stars based on various parameters, including total movement, magnitude, and coordinates.
- **Cache Results:** Save query results to a cache to speed up subsequent runs.
- **User-Friendly Output:** Display results in a neatly formatted table, including both original (J2000) and updated coordinates.

## Installation

### Prerequisites

Ensure you have Python 3.6 or later installed on your system. You can download Python from the [official website](https://www.python.org/downloads/).

### Clone the Repository

```bash
git clone https://github.com/pierregab/HPMS.git
cd HPMS
```

### Create a Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install numpy astroquery astropy astroplan
```

## Usage

Run the `HPMS.py` script using Python. The script offers several options to customize the query and output.

### Basic Usage

```bash
python3 HPMS.py
```

This command will:

- Query the SIMBAD TAP service for high proper motion stars.
- Update their positions based on proper motion.
- Check their visibility from Strasbourg at the current local time.
- Display a list of visible stars with their details.

### Advanced Options

- **Specify Observation Time:**

  Use the `-t` or `--time` flag to set a specific observation hour in local time (24-hour format).

  ```bash
  python3 HPMS.py -t 22.5
  ```

  *Example:* `22.5` corresponds to 22:30 (10:30 PM).

- **Reuse Cached Results:**

  Use the `-r` or `--reuse` flag to load results from the cache instead of querying SIMBAD again.

  ```bash
  python3 HPMS.py -r
  ```

- **Combine Options:**

  You can combine both options to reuse cached data and specify an observation time.

  ```bash
  python3 HPMS.py -r -t 23.0
  ```

## Examples

### Example 1: Basic Usage

```bash
python3 HPMS.py
```

**Output:**

```
Querying SIMBAD TAP service for high proper motion stars...
Query completed and results cached.
Number of stars retrieved: 285
Columns returned by the query:
['oid', 'ra', 'dec', 'Main_Identifier', 'pmra', 'pmdec', 'V_Magnitude']
Updating star positions based on proper motion...

 /$$   /$$ /$$$$$$$  /$$      /$$  /$$$$$$ 
| $$  | $$| $$__  $$| $$$    /$$$ /$$__  $$
| $$  | $$| $$  \ $$| $$$$  /$$$$| $$  \__/
| $$$$$$$$| $$$$$$$/| $$ $$/$$ $$|  $$$$$$ 
| $$__  $$| $$____/ | $$  $$$| $$ \____  $$
| $$  | $$| $$      | $$\  $ | $$ /$$  \ $$
| $$  | $$| $$      | $$ \/  | $$|  $$$$$$/
|__/  |__/|__/      |__/     |__/ \______/ 

High Proper Motion Stars Visible from Strasbourg at 22:30

Checking visibility of stars at the specified observation time in Strasbourg...
Number of stars visible above 30.0 deg: 25

List of visible high proper motion stars:

Main Identifier             J2000 RA   J2000 Dec  Updated RA  Updated Dec  pmRA (mas/yr)  pmDEC (mas/yr)  Total Movement (mas/yr)  V_mag
Star A                      123.45678  -45.67890    124.00000    -45.50000         150.00          -200.00               250.00    12.34
Star B                       98.76543   12.34567     99.20000     12.80000         300.00           400.00               500.00    10.12
... (additional stars)

Sort Options:
1. Main Identifier
2. RA (deg)
3. DEC (deg)
4. pmRA (mas/yr)
5. pmDEC (mas/yr)
6. V_mag
7. Total Movement (mas/yr)
Enter the number corresponding to the column you want to sort by (or press Enter to skip): 7
Enter 'a' for ascending or 'd' for descending order: d

Stars sorted by Total Movement (mas/yr) in descending order:

Main Identifier             J2000 RA   J2000 Dec  Updated RA  Updated Dec  pmRA (mas/yr)  pmDEC (mas/yr)  Total Movement (mas/yr)  V_mag
Star B                       98.76543   12.34567     99.20000     12.80000         300.00           400.00               500.00    10.12
Star A                      123.45678  -45.67890    124.00000    -45.50000         150.00          -200.00               250.00    12.34
... (additional stars)
```

### Example 2: Specifying Observation Time and Reusing Cache

```bash
python3 HPMS.py -r -t 23.0
```

**Output:**

```
Reusing the last query result from the cache.
Number of stars retrieved: 285
Columns returned by the query:
['oid', 'ra', 'dec', 'Main_Identifier', 'pmra', 'pmdec', 'V_Magnitude']
Updating star positions based on proper motion...

 /$$   /$$ /$$$$$$$  /$$      /$$  /$$$$$$ 
| $$  | $$| $$__  $$| $$$    /$$$ /$$__  $$
| $$  | $$| $$  \ $$| $$$$  /$$$$| $$  \__/
| $$$$$$$$| $$$$$$$/| $$ $$/$$ $$|  $$$$$$ 
| $$__  $$| $$____/ | $$  $$$| $$ \____  $$
| $$  | $$| $$      | $$\  $ | $$ /$$  \ $$
| $$  | $$| $$      | $$ \/  | $$|  $$$$$$/
|__/  |__/|__/      |__/     |__/ \______/ 

High Proper Motion Stars Visible from Strasbourg at 23:00

Checking visibility of stars at the specified observation time in Strasbourg...
Number of stars visible above 30.0 deg: 22

List of visible high proper motion stars:

Main Identifier             J2000 RA   J2000 Dec  Updated RA  Updated Dec  pmRA (mas/yr)  pmDEC (mas/yr)  Total Movement (mas/yr)  V_mag
Star C                      110.12345  -30.54321    110.50000    -30.40000         180.00          -220.00               280.00    11.50
Star D                       75.65432   25.67890     75.90000     25.80000         200.00           350.00               390.00     9.80
... (additional stars)

Sort Options:
1. Main Identifier
2. RA (deg)
3. DEC (deg)
4. pmRA (mas/yr)
5. pmDEC (mas/yr)
6. V_mag
7. Total Movement (mas/yr)
Enter the number corresponding to the column you want to sort by (or press Enter to skip): 7
Enter 'a' for ascending or 'd' for descending order: d

Stars sorted by Total Movement (mas/yr) in descending order:

Main Identifier             J2000 RA   J2000 Dec  Updated RA  Updated Dec  pmRA (mas/yr)  pmDEC (mas/yr)  Total Movement (mas/yr)  V_mag
Star D                       75.65432   25.67890     75.90000     25.80000         200.00           350.00               390.00     9.80
Star C                      110.12345  -30.54321    110.50000    -30.40000         180.00          -220.00               280.00    11.50
... (additional stars)
```

## Dependencies

HPMS relies on several Python libraries to function correctly. Ensure all dependencies are installed before running the script.

- **numpy**: For numerical operations.
- **astroquery**: To query the SIMBAD TAP service.
- **astropy**: For handling astronomical data and units.
- **astroplan**: For observer-related calculations, such as determining night time and visibility.

### Installing Dependencies

Use `pip` to install the required packages:

```bash
pip install numpy astroquery astropy astroplan
```

Alternatively, if a `requirements.txt` file is provided, install all dependencies at once:

```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Whether it's fixing bugs, improving performance, or adding new features, your input is valuable to the HPMS project.

### Steps to Contribute

1. **Fork the Repository:** Click the "Fork" button at the top-right corner of the repository page.
2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/pierregab/HPMS.git
   cd HPMS
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:** Implement your feature or fix.

5. **Commit Your Changes:**

   ```bash
   git commit -m "Add feature: Your Feature Description"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request:** Navigate to the original repository and click "Compare & pull request."

### Code of Conduct

Please adhere to the [Code of Conduct](https://github.com/yourusername/HPMS/blob/main/CODE_OF_CONDUCT.md) in all interactions.

## License

Distributed under the GNU License. See `LICENSE` for more information.

## Contact

- **Project Lead:** Pierre Gabriel Bibal Sobeaux
- **Email:** pg.bibal@gmail.com
- **GitHub:** [pierregab](https://github.com/pierregab)

Feel free to reach out with questions, suggestions, or feedback!

## Acknowledgments

- **SIMBAD Astronomical Database:** For providing comprehensive astronomical data.
- **Astropy Community:** For the powerful tools that make this project possible.
- **Astroquery and Astroplan Developers:** For their invaluable libraries.

---

> **Disclaimer:** This project is for educational and personal use. Ensure compliance with SIMBAD's usage policies when querying their data.
