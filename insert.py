import fasttext
import fasttext.util
from pgvector.psycopg2.register import psycopg2, register_vector
from psycopg2.extras import execute_values
from dotenv import load_dotenv, find_dotenv
import numpy as np
import os

# Load environment variables from .env file
load_dotenv(find_dotenv())

LOAD_DIR = "models"
FILE_NAME = "custom_fasttext_model.bin"  # Change this to your FastText model file if different
TOTAL_KEYS = 200000  # Ensure this matches the total number of keys you want to process
NEON_URL="postgresql://awssimilar_owner:K5jvuhLpS1Ye@ep-tight-cake-a1iqjx0p.ap-southeast-1.aws.neon.tech/awssimilar?sslmode=require"
# Load PostgreSQL connection URL from environment variable
neon_url = os.environ["Neon_URL"]

# Connect to PostgreSQL
conn = psycopg2.connect(neon_url)
cursor = conn.cursor()

# Load FastText model
ft_model = fasttext.load_model(os.path.join(LOAD_DIR, FILE_NAME))

# Prepare data for insertion
data_list = []
words = ft_model.get_words()[:TOTAL_KEYS]  # Get the words up to TOTAL_KEYS

for i, word in enumerate(words):
    print(i)
    embedding = ft_model.get_word_vector(word)

    data_list.append((word, embedding))

# Register vector type with PostgreSQL
register_vector(conn)

# Insert data into PostgreSQL
execute_values(
    cursor, 
    "INSERT INTO public.embeddings (word, embedding) VALUES %s", 
    data_list
)

# Commit transaction
conn.commit()
print("Data insertion completed successfully.")
conn.close()
