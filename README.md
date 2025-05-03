# PBI Power Documenter

A Streamlit web app to generate business-friendly documentation for Power BI TMDL files using LLM (Qwen) and export the results to Excel.

---

## Features

- **Upload** one or more Power BI TMDL files
- **Parse** all measures and columns, including quoted names and special characters
- **AI-powered documentation**: Generates concise, business-friendly definitions for measures and columns
- **Excel export**: Download documentation with Table Overview, Measures, and Columns sheets
- **Modern UI**: Progress indicators, elapsed time, and preview of results
- **Sticky footer**: Credits and website link

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/PBIPowerDocumenter.git
   cd PBIPowerDocumenter
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

This app uses the Qwen LLM via the DashScope API.  
**You must provide your API key using Streamlit secrets.**

1. In your project root, create a folder called `.streamlit` (if it doesn't exist).
2. Create a file named `secrets.toml` inside `.streamlit`:

   ```
   [general]
   DASHSCOPE_API_KEY = "your_dashscope_api_key_here"
   ```

3. **If deploying to Streamlit Cloud:**  
   Set the secret in the app's dashboard under **Settings > Secrets**.

---

## Usage

1. **Run the app locally:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the provided local URL (usually http://localhost:8501).

3. **Upload one or more `.tmdl` files**.

4. Click **Generate Documentation**.

5. **Preview** the first 5 rows of Measures and Columns, and **download** the full Excel documentation.

---

## File Structure

- `app.py` — Main Streamlit app
- `tmdl_parser.py` — TMDL file parser
- `llm_documenter.py` — LLM-powered documentation generator
- `requirements.txt` — Python dependencies

---

## Credits

App developed by [Nicky](https://www.nickytan.com)

---

## License

MIT License 