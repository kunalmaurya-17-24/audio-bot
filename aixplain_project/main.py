import os
import requests
import chardet
import ftfy
from dotenv import load_dotenv
from aixplain.factories import PipelineFactory

# Load environment variables
load_dotenv()

# Retrieve required variables
API_KEY = os.getenv("TEAM_API_KEY")
PIPELINE_ID = os.getenv("AIXPLAIN_PIPELINE_ID")
INPUT_AUDIO_PATH = os.getenv("INPUT_AUDIO_PATH")

if not API_KEY or not PIPELINE_ID or not INPUT_AUDIO_PATH:
    raise ValueError("[ERROR]: Missing TEAM_API_KEY, AIXPLAIN_PIPELINE_ID, or INPUT_AUDIO_PATH in .env.")

print("✅ Environment variables loaded successfully!")

# Initialize pipeline
pipeline = PipelineFactory.get(PIPELINE_ID)

# Run the pipeline synchronously (passing the MP3 file path)
print("[INFO]: Running pipeline with file:", INPUT_AUDIO_PATH)
output = pipeline.run({"Input 1": INPUT_AUDIO_PATH})

# Extract the output data
output_texts = output.get("data", [])
if not output_texts:
    print("[WARN]: No output data returned from the pipeline.")
    final_hex = ""
    final_text = ""
else:
    # For simplicity, process only the first output
    text_output = output_texts[0]
    response_val = text_output.get("response", "")
    if response_val.startswith("http"):
        print("[INFO]: Downloading content from URL...")
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}
        r = requests.get(response_val, headers=headers, stream=True)
        if r.status_code == 200:
            # Download full content as bytes
            content = b"".join(r.iter_content(chunk_size=1024))
            print(f"[DEBUG]: Downloaded {len(content)} bytes.")
            # Convert bytes to hex string (space separated for readability)
            final_hex = content.hex(" ")
            # Write the hex string to file later
            # Now, remove spaces and convert back to bytes
            hex_str_no_spaces = final_hex.replace(" ", "")
            converted_bytes = bytes.fromhex(hex_str_no_spaces)
            # Detect encoding; if chardet returns None, default to 'utf-8'
            detected = chardet.detect(converted_bytes)
            encoding = detected.get("encoding", "utf-8")
            print(f"[DEBUG]: Detected encoding: {encoding}")
            try:
                decoded_text = converted_bytes.decode(encoding, errors="replace")
            except Exception as e:
                print(f"[ERROR]: Decoding error: {e}")
                decoded_text = converted_bytes.decode("utf-8", errors="replace")
            # Optionally use ftfy to fix text
            final_text = ftfy.fix_text(decoded_text)
        else:
            final_hex = ""
            final_text = f"[ERROR]: Failed to download content. Status code: {r.status_code}"
    else:
        # If the response isn't a URL, assume it's direct text.
        final_text = response_val
        final_hex = response_val.encode("utf-8").hex(" ")

# Prepare output directory
output_dir = os.path.join(os.getcwd(), "output_texts")
os.makedirs(output_dir, exist_ok=True)

# Write hex output to file
hex_file_path = os.path.join(output_dir, "pipeline_output_hex.txt")
with open(hex_file_path, "w", encoding="utf-8") as f:
    f.write(final_hex)
print(f"[INFO]: Hex output written to {hex_file_path}")

# Write decoded text output to file
text_file_path = os.path.join(output_dir, "pipeline_output_text.txt")
with open(text_file_path, "w", encoding="utf-8") as f:
    f.write(final_text)
print(f"[INFO]: Text output written to {text_file_path}")
