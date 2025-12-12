import re

# Load guidelines
with open("guidelines.txt", "r", encoding="utf-8") as f:
    guidelines_text = f.read()

# Split by major headings (A., B., C., etc.)
sections = re.split(r'\n([A-Z]\..*?)\n', guidelines_text)
word_limit = 300  # maximum words per chunk
chunks = []

# Function to split text into word-based chunks
def split_by_word_count(text, max_words):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

# Combine heading + content and then split into word-limited chunks
for i in range(1, len(sections), 2):
    heading = sections[i].strip()
    content = sections[i+1].strip()
    full_text = f"{heading}\n{content}"
    chunks.extend(split_by_word_count(full_text, word_limit))

print(f"Created {len(chunks)} word-limited chunks")

# Check first few chunks
for i, chunk in enumerate(chunks[:5]):
    word_count = len(chunk.split())
    print(f"Chunk {i+1} ({word_count} words):\n{chunk[:200]}...\n")  # print first 200 chars

# Check all chunks to ensure they are within limit
if all(len(c.split()) <= word_limit for c in chunks):
    print("All chunks are within the word limit!")
else:
    print("Some chunks exceed the word limit.")
