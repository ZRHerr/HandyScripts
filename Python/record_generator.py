import json
import math
import random
import sys
import boto3
from datetime import datetime
from time import time, sleep

#################################################################
# TO RUN:                                                       #
# CD ./HandyScripts/Python                                      #
# python record_generator.py <Firstname> <Lastname>             # 
################################################################# 

def generate_random(no_of_digits, prefix=""):
    """generates a random set of numbers used in some of the records attributes

    Args:
        no_of_digits (Int): defaulted to 6 in the script but, this is for generating the random requestId
        prefix (str, optional): Defaults to "".

    Returns:
        [string]: requestId = userId_[random generated nums]_to
    """    
    num = random.randrange(1, 10 ** no_of_digits)
    return prefix + str(num).zfill(no_of_digits)


def time_to_str(timestamp): # Convert dateTime into formatted dateTime string YYYY-MM-DDTHH:MM:SS.###Z
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def generate_doc(record_id, emp_id, created_time, first_name="Test", last_name="User"):
    """generate_doc(str, str, str, str, str)

    Args:
        record_id (String): same as requestId
        emp_id (String): same as userId
        created_time (String): current date time formatted string
        first_name (str, optional): Defaults to "Test".
        last_name (str, optional): Defaults to "User".

    Returns:
        [document]: [description] returns individual json record document field for each of the 3 baker_request items
    """    
    short_date = datetime.fromtimestamp(created_time).strftime("%Y-%m-%d")
    return json.dumps(
        {
            "id": record_id,
            "requestedByEmployeeId": emp_id,
            "createdInstant": time_to_str(created_time),
            "createdDate": short_date,
            "status": "NEW",
            "statusDescription": "null",
            "isEmptySolution": False,
            "isSentToSwift": False,
            "requestedByFirstName": first_name,
            "requestedByLastName": last_name,
            "scenarioName": "SCENARIO NAME",
            "scenarioDateTime": time_to_str(created_time),
            "notes": "",
            "manualSolution": "",
            "manualSolutionSchedule": "null",
            "whatIfs": [
                {"type": "SCENARIO TYPE", "fromDate": short_date, "untilDate": short_date}
            ],
            "protections": [],
            "lastUpdatedDateTime": time_to_str(created_time),
        }
    )


def generate_record(
    user_id, timestamp, document, recordType, requestId, status, solution_id=False
):
    """Generates the records main values outside of the document string

    Args:
        user_id (String): employeeID
        timestamp (String): dateTimeStamp
        document (String): generate_document()
        recordType (String): BAKER_REQUEST or BAKER_SOLUTION
        requestId (String): userId_<generate_random(no_of_digits, prefix="")>_to
        status (String): NEW or COMPLETED
        solution_id (bool, optional): Defaults to False. used to determine creation of BAKER_SOLUTION recordtype:

    Returns:
        [Record]: Required fields in the baker_request table
    """
    record = {
        "userId": user_id,
        "dateTimestamp": time_to_str(timestamp),
        "document": document,
        "recordType": recordType,
        "requestId": requestId,
        "status": status,
        "timeToLive": int(math.floor(timestamp * 1000 + 7 * 24 * 60 * 60 * 1000)),
    }

    if solution_id:
        record["solutionId"] = solution_id

    return json.dumps(record, indent=4)


def put_item_in_dynamodb(jsondata):
    #API expects data in dictionary format
    datadict = json.loads(jsondata)
    database = boto3.resource('dynamodb')
    table = database.Table('DYNAMODB_TABLE_NAME') # TODO: make value more dynamic
    table.put_item(Item = datadict)    


def write_to_file(output, request_id):
    filename = "./records/" + request_id + ".json"
    f = open(filename, "w")
    f.write(output)
    f.close()


def write_scores_to_file(output, request_id, solution_id): # TODO: Finish generating scores document
    filename = "./records/scores/" + request_id + "/" + solution_id + "/Scores.json"
    f = open (filename, "w")
    f.write(output)
    f.close()


if __name__ == "__main__":
    user_id = generate_random(6, "e")
    request_id_second = generate_random(13, "")
    request_id = user_id + "_" + request_id_second + "_to"
    solution_id = "Run_" + request_id_second + "_to.11.1"
    timestamp = time()
    document = generate_doc(request_id, user_id, timestamp, sys.argv[1], sys.argv[2])

    # Record 1 creation and put into dynamodb STATUS NEW
    rec1 = generate_record(user_id, timestamp, document, "BAKER_REQUEST", request_id, "NEW")
    put_item_in_dynamodb(rec1)
    # Sleep in order to create new timestamp with later time
    sleep(3.3)
    timestamp_in_progress = time()
    # Record 1 with IN_PROGRESS status inserted into dyanmodb
    rec1_in_progress = generate_record(user_id, timestamp_in_progress, document, "BAKER_REQUEST", request_id, "IN_PROGRESS")
    put_item_in_dynamodb(rec1_in_progress)
    # Sleep in order to create new timestamp with later time
    sleep(3.3)
    timestamp2 = time()
    # Record 2 with STATUS BAKE_COMPLETE inserted into dynamodb
    rec2 = generate_record(user_id, timestamp2, document, "BAKER_REQUEST", request_id, "COMPLETE")
    put_item_in_dynamodb(rec2)
    # Sleep in order to create new timestamp with later time
    sleep(3.3)
    timestamp3 = time()
    # Record 3 BAKER_SOLUTION created and inserted into dynamodb with NEW STATUS
    rec3 = generate_record(
        user_id, timestamp3, document, "BAKER_SOLUTION", request_id, "NEW", solution_id
    )
    put_item_in_dynamodb(rec3)

    # Writing the file with requestId.json into dir (src/scripts/record_generator/records) for reference but, not needed.
    final_str = rec1 + "\n" + rec2 + "\n" + rec3
    write_to_file(final_str, request_id)
