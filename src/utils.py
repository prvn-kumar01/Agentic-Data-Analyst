import re
import io
import pandas as pd

def clean_column_names(df):
    """
    Cleans column names to be Python-friendly (removes spaces, special chars, handles duplicates).
    """
    new_cols = []
    seen = {}
    for i, col in enumerate(df.columns):
        c_str = str(col).strip().lower().replace(' ', '_')
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', c_str)
        if not cleaned:
            cleaned = f"col_{i+1}"
        
        # Deduplicate
        if cleaned in seen:
            seen[cleaned] += 1
            cleaned = f"{cleaned}_{seen[cleaned]}"
        else:
            seen[cleaned] = 0
        new_cols.append(cleaned)
        
    df.columns = new_cols
    return df

def get_csv_summary(file_path: str):
    """
    Reads a CSV and returns a 'Text Summary' optimized for LLM context.
    Instead of sending the whole file, we send the Structure + Sample.
    """
    try:
        # 1. Load Data with encoding fallbacks
        try:
            df = pd.read_csv(file_path)
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(file_path, encoding="latin-1")
            except Exception:
                df = pd.read_csv(file_path, encoding_errors="replace")
        
        df = clean_column_names(df)
        
        # 2. Extract Key Info
        rows, cols = df.shape
        columns = [str(c) for c in df.columns]
        missing = df.isnull().sum().to_dict()
        types = df.dtypes.astype(str).to_dict()
        
        # 3. Create Text Representation (For the LLM Brain)
        buffer = io.StringIO()
        df.head(5).to_csv(buffer, index=False) # Top 5 rows only
        sample_data = buffer.getvalue()
        
        summary_text = f"""
        DATASET SHAPE:
        - Rows: {rows}
        - Columns: {cols}
        
        COLUMN DETAILS (Name: Type | Missing Values):
        """
        
        for col in columns:
            summary_text += f"\n- {col}: {types.get(col, 'unknown')} | {missing.get(col, 0)} missing"
            
        summary_text += f"\n\nSAMPLE DATA (Top 5 Rows):\n{sample_data}"
        
        return {
            "success": True,
            "df": df,              
            "text": summary_text,  
            "columns": columns
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

# --- Quick Test ---
if __name__ == "__main__":
    # Create a dummy CSV to test
    dummy_data = "name,age,salary\nAlice,30,50000\nBob,25,60000\nCharlie,35,NaN"
    with open("test.csv", "w") as f:
        f.write(dummy_data)
        
    result = get_csv_summary("test.csv")
    print(result["text"])