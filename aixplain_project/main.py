import os
import json
import requests
from dotenv import load_dotenv
from aixplain.factories import PipelineFactory

# Load environment variables from .env
load_dotenv()

# Retrieve required variables
API_KEY = os.getenv("TEAM_API_KEY")
PIPELINE_ID = os.getenv("AIXPLAIN_PIPELINE_ID")
INPUT_AUDIO_PATH = os.getenv("INPUT_AUDIO_PATH")

if not API_KEY or not PIPELINE_ID or not INPUT_AUDIO_PATH:
    raise ValueError("[ERROR]: Missing TEAM_API_KEY, AIXPLAIN_PIPELINE_ID, or INPUT_AUDIO_PATH in .env.")

print("✅ Environment variables loaded successfully!")

# Initialize the pipeline
pipeline = PipelineFactory.get(PIPELINE_ID)

# Run the pipeline synchronously (passing the input file path)
print("[INFO]: Running pipeline with file:", INPUT_AUDIO_PATH)
output = pipeline.run({"Input 1": INPUT_AUDIO_PATH})

# Prepare output directory for JSON
current_dir = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(current_dir, "output_texts")
os.makedirs(output_dir, exist_ok=True)

# Save the pipeline output as JSON
json_file_path = os.path.join(output_dir, "pipeline_output.json")
with open(json_file_path, "w", encoding="utf-8") as f:
    json.dump({"data": output.get("data", [])}, f, indent=4, ensure_ascii=False)
print(f"[INFO]: JSON output written to {json_file_path}")

# Now, extract the response URL from the JSON output
try:
    response_url = output["data"][0]["segments"][0]["response"]
except Exception as e:
    raise Exception(f"[ERROR]: Unable to extract response URL: {e}")

print(f"[INFO]: Extracted response URL: {response_url}")

# Download the file from the response URL
r = requests.get(response_url)
if r.status_code == 200:
    # Save the downloaded file's text content to output.txt in the current directory
    output_txt_path = os.path.join(current_dir, "output.txt")
    try:
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        print(f"✅ File downloaded and written to {output_txt_path}")
    except Exception as e:
        print(f"[ERROR]: Could not write content as text: {e}")
else:
    print(f"[ERROR]: Failed to download file. Status code: {r.status_code}")
