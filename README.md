## Fender Digital Data Engineering Exercise
This project communicates with the Open Library API to find some suggested books and authors by using the search API to get the top 100 books (with multiple editions for some) suggested from a keyword or keywords. It then exports the data to csv files.

Within the program a list of keywords is used to call the search API to just initially get some ISBN values to gather book data for. Once the ISBNs are available, the ISBN portion of the API can be called for each value to obtain the book data JSONs.

After all of the book data is gathered, it is flattened out so it'll be easier to view later in the csv. To flatten the data, it iteratively goes through each layer and determines what its structure is. Each layer has the cartesian product taken between it and the layer nested below it so that each nested object gets it's own line, keeping the information for the outer layer. Lists at the lowest level keep the list as a single line, separated by commas; so ['spooky', 'scary', 'skeletons'] would become 'spooky, scary, skeletons'.

Within the book data, the authors key exists, which can be used to get JSON data for each author. Prior to making the calls to get the data, rows with null author keys are dropped so that there aren't any issues with it. Since the key has the '/authors/' at the beginning, the string is split by '/' then only the last position is kept to look up the authors. The author data is found for each unique authors key in the books table. After the authors JSON is found, it is flattened as well.

After both tables are found, the bridge csv file is created with the key and author key fields from the books table. A handful of columns are dropped from the books and authors tables, and any remaining key fields are stripped down to just the key value.

The three tables are then written to their individual csv files.

How to use?
Prior to running the project, setup the environment by issuing the command
pip install -r requirements.txt
The openLibrary.py file can then be run as is; if you want to change the search terms, the openLibrary.py file will need to be opened and the list keywords will need to be updated.


Future Enhancements
	* Allow input for the search terms
	* Create automated process to import the data directly into the database
	* Find a way to grab multiple books at once to limit API calls
	* Add tests to track how long it takes for each step in the process
	* Adjust the keywords to allow for use of the other customizability in the search API
	* Grab all the data in works API for additional information on books
	* Clean the data up a little more by trying to format column as date / fixing ones missing days / months
	* Include more error handling

Notes
There are a lot of calls to the API, once for each ISBN and then again for each author. This causes it to be slow, so more specific searches could potentially help speed it up. The API only gives the first 100, even if there are thousands of matches for the keyword.
------------------------------------------------------------------------------
Design and implement a data pipeline that that pulls data from [Open Library.]https://openlibrary.org/dev/docs/api/books As an out put of this exercise we expect to see a minimum of the following:

1. Python program that pulls data from the rest api
2. CSV files for the following:
	* Authors
	* Books
	* Authors and Books (a bridge table between the previous entities)
3. DDL to create a hypothetical database schema ( you don't have to create a DB but you are welcome to)

The objective of this exercise is to have you walk us through a solution you have created. Do as much or as little as you would like.


# ReadMe
Please include:
* a readme file that explains your thinking
* a data model showing your design, explain why you designed the db and include the DDL used to generate the tables in your database
* how to run and set up your project
* if you have tests, include instructions on how to run them
* a description of:
	* enhancements you might make
	* additional features you have added to help or that you found interesting
* questions you have
* recommendations for us


# Additional Info:
* we expect that this will take you a few hours to complete
* use any language or framework you are comfortable with we prefer Python
* Bonus points for setting up a db
* Bonus points for security, specs, etc.
* Do as little or as much as you like.

Please fork this repo and commit your code into that fork. Show your work and process through those commits.
