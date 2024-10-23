import json
import csv

with open ("DisneylandReviews.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    data = []
    for row in reader:
        data.append({"ID": row[0],
                              "Rating": row[1],
                              "Year_Month": row[2],
                              "Reviewer_Location": row[3],
                              "Review": row[4],
                              "Branch": row[5],
                              })

with open("disneyReviews.json", "w") as f:
    json.dump(data, f, indent=4)
    f.close()