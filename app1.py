import os
import openai
import streamlit as st
import fitz  # PyMuPDF
import markdown2
from dotenv import load_dotenv
import bleach  # Import bleach for sanitizing HTML

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Function to extract text from PDF while preserving formatting
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text")  # Extract plain text; consider using "dict" for more control
    return text

# Function to sanitize HTML content
def sanitize_html(content):
    allowed_tags = ['b', 'i', 'u', 'span', 'hr']  # Specify allowed tags directly
    allowed_attrs = {'span': ['style']}  # Allow style attributes on span tags
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)

# Function to translate content using OpenAI's API
def translate_content(content, target_language):
    messages = [
        {"role": "user", "content": f"Translate the following text to {target_language}:\n\n{content}"}
    ]
    
    # Use OpenAI's ChatCompletion for translation
    client = openai.OpenAI(api_key=openai_api_key)  # Set API key here
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use a suitable model; adjust as needed
        messages=messages,
        max_tokens=2048,  # Adjust as needed
        temperature=0.7
    )
    translated_text = response['choices'][0]['message']['content'].strip()
    return translated_text

# Function to download translated content in Markdown format
def download_markdown(content, filename="translated_content.md"):
    st.download_button(
        label="Download Translated Content",
        data=content,
        file_name=filename,
        mime="text/markdown",
        key="download_button"  # Add a key to avoid duplicate button warnings
    )

# Streamlit app title and layout configuration
st.set_page_config(page_title="Markdown Content Translator", layout="wide")
st.title("Markdown Content Translator")
st.markdown("""
    Upload a PDF or text file to translate its content into your desired language while retaining the original Markdown formatting.
""")

# Create a two-column layout for file upload and language selection
upload_col, lang_col = st.columns([3, 1])

# Left column: File uploader and language selection
with upload_col:
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a PDF or Text file", type=["pdf", "txt", "md"], label_visibility="collapsed")

with lang_col:
    # Language selection for translation
    target_language = st.selectbox("Select Target Language", [
        "German", "French", "Chinese", "Japanese",
        "Spanish", "Italian", "Russian", "Portuguese",
        "Dutch", "Korean", "Arabic", "Turkish",
        "Hindi", "Swedish", "Norwegian", "Danish"
    ])

    # Translate button below the language selector
    translate_button = st.button("Translate", key="translate_button", help="Click to translate the uploaded content")

if uploaded_file is not None:
    # Extract content based on file type
    if uploaded_file.type == "application/pdf":
        content = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain" or uploaded_file.type == "text/markdown":
        content = uploaded_file.read().decode("utf-8")

    # Sanitize the content before rendering
    sanitized_content = sanitize_html(content)

    # Display original and translated content in the same row
    content_col1, content_col2 = st.columns(2)

    with content_col1:
        st.subheader("Original Content")
        # Create a scrollable container for original content with increased height
        st.markdown(
            f'<div class="content-box">{markdown2.markdown(sanitized_content)}</div>',
            unsafe_allow_html=True
        )

    with content_col2:
        st.subheader("Translated Content")
        if translate_button:
            with st.spinner("Translating..."):
                # Translate the content while preserving Markdown
                translated_text = translate_content(sanitized_content, target_language)
                # Create a scrollable container for translated content with increased height
                st.markdown(
                    f'<div class="content-box">{markdown2.markdown(translated_text)}</div>',
                    unsafe_allow_html=True
                )
                # Add some space before the download button
                st.markdown("<br>", unsafe_allow_html=True)
                download_markdown(translated_text)

else:
    st.markdown("Upload a file to see the original content here.")

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f4;
        color: #333;
        margin: 0;
        padding: 0;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 10px 0;
        cursor: pointer;
        border-radius: 5px;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
        transform: scale(1.05); /* Slightly enlarge on hover */
    }
    .content-box {
        height: 600px;
        overflow-y: scroll;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s;
    }
    .content-box:hover {
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); /* Increase shadow on hover */
    }
    @media (max-width: 768px) {
        .content-box {
            height: 400px; /* Reduce height on smaller screens */
        }
    }
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #333;
            color: #f4f4f4;
        }
        .content-box {
            background-color: #444;
            border: 1px solid #555;
        }
        .stButton>button {
            background-color: #5cb85c; /* Lighter green for dark mode */
        }
        .stButton>button:hover {
            background-color: #4cae4c; /* Darker green on hover for dark mode */
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)
