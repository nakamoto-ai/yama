#!/usr/bin/env python3
import sqlite3
import json


def exportData(database, output):
    # Connect to the SQLite database
    con = sqlite3.connect(database)
    cur = con.cursor()

    # Fetch all job data from the jobs table
    cur.execute("SELECT job, description FROM jobs")
    rows = cur.fetchall()

    # Write job data to a JSON Lines file
    with open(output, 'w') as f:
        for row in rows:
            job, description = row
            data = {"job": job, "description": description}
            json.dump(data, f)
            f.write('\n')

    # Close the database connection
    con.close()


if __name__ == "__main__":
    database = "jobs.db"
    output = "jobTrainingData.jsonl"
    exportData(database, output)
    print(f"Successfully exported data from {database} to {output}")
