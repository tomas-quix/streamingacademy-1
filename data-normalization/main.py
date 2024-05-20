import os
from quixstreams import Application
import uuid
import json

# for local dev, load env vars from a .env file
from dotenv import load_dotenv
load_dotenv()

app = Application.Quix(str(uuid.uuid4()), auto_offset_reset="earliest")

input_topic = app.topic(os.environ["input"])
#output_topic = app.topic(os.environ["output"])

sdf = app.dataframe(input_topic)

sdf = sdf.apply(lambda message: message["payload"], expand=True)

def transpose(message: dict):

    result_row = {
        "time": message["time"]
    }

    for key in message["values"]:
        result_row[message["name"] + "-" + key] = message["values"][key]
    
    return result_row


sdf = sdf.apply(transpose)

sdf = sdf[sdf.contains("location-speed")]

sdf = sdf[["time", "location-latitude", "location-longitude", "location-speed"]]

sdf["location-speed"] = sdf["location-speed"] * 3.6

sdf = sdf.update(lambda row: print(row))

#sdf = sdf.to_topic(output_topic)

if __name__ == "__main__":
    app.run(sdf)