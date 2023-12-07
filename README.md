1. **Architecture Overview**:
   - Briefly outline the architecture and the technologies or services you would use. As we use AWS, mention any relevant AWS services.
   - Include a simple data model diagram.

   The architecture I would use for a system pulling data the open library API would include a lambda, S3, and a cloudwatch trigger for scheduling regular pulls.

   Running on a cloudwatch scheduled trigger, the lambda would run at a monthly interval to pull data on Bowling to find any new books on the topic. The JSON data that is pulled from the API is flattened and cleaned up before being written to s3 as a csv. 
   
   After being written to s3, an s3 alert would trigger a second lambda to clean the data more, formatting dates and removing bad records, and writing to a "cleaned" s3 folder.

   After the data is written to a "clean" s3 folder, a third lambda would be triggered to do an upsert to the data.

2. **Python Script**:
   - openLibrary.py is able to be run
      This currently handles some of the cleaning that would be better handled in the second lambda, where the first would ideally just write directly from the API
   - open-library/lambda.py is not currently running, but would be the starting point to setting up the working lambda.

3. **Sample Data Output**:
   - Provide CSV outputs for 'Authors' and 'Books'.
   - Include a simple 'Authors and Books' relation (no need for a full bridge table).
   authors20231203-162743.csv
   books20231203-162743.csv
   bridge20231203-162743.csv

4. **Data Processing**:
   - Write a SQL query (or Python equivalent) to aggregate:
     - books_by_author.csv
     
   - Discuss how you would optimize this for a larger dataset.
   For a larger data set, I would either set up partitioning on the dataset, or create keys for it, specificially on the publishing date and authors_key.
   When reading from the dataset, I would make sure to include one of the keys for filtering the data.

5. **Presentation**:
   - Prepare a short presentation explaining your approach, decisions made, and any assumptions.
   - Discuss what you would do differently in a production environment and potential enhancements.

   Production Environment:
   The first lambda would only be for reading from the API and not making any changes to the data that is pulled.
   Rather than doing a full pull, as it currently does, only new or records modified after the last run date would be pulled from the API
   Before doing the initial first run, I would download files for all the data for the specific topic.

6. **ReadMe & Documentation**:
   - Include a brief ReadMe file explaining your approach.
   - Document any setup instructions or prerequisites.