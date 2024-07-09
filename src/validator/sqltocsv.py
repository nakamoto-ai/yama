#!/usr/bin/env python3
import sqlite3
import csv


def exportData(database, output):
    # Connect to the SQLite database
    con = sqlite3.connect(database)
    cur = con.cursor()

    # Fetch all job data from the jobs table
    cur.execute("SELECT job, description FROM jobs")
    rows = cur.fetchall()

    # Write job data to a CSV file
    with open(output, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write the header
        writer.writerow(["job", "description"])
        # Write the rows
        writer.writerows(rows)

    # Close the database connection
    con.close()


if __name__ == "__main__":
    database = "jobs.db"
    output = "jobTrainingData.csv"
    exportData(database, output)
    print(f"Successfully exported data from {database} to {output}")
