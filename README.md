# tally

A Flask application for parsing and categorizing transactions from RBC credit card statements. Transactions are stored in a local database and can be reviewed for personal finance tracking.

## Installation
To give tally a try, follow the steps below to install it and run it as a local server.

### External Dependencies

Tally depends on Apache Tika for PDF parsing, so Java 7+ must be installed prior to running the app ([download link](https://www.java.com/en/download/)).

### Python Dependencies

Once Java is installed, clone the repo and install using Poetry:
```ps
git clone https://github.com/scottdalgliesh/tally.git
cd tally
poetry install
```

### First-time Setup
Before running flask for the first time, issue the following command to initialize the database:
```ps
flask db upgrade
```

### Running tally
Now run the local server and follow the provided IP address to try it out!
```ps
flask run
```

## License
[MIT](LICENSE)
