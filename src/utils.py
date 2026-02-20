import pandas as pd
import io

def clean_column_names(df):
    """
    Cleans column names to be Python-friendly (removes spaces, special chars).
    """
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace(r'[^a-zA-Z0-9_]', '', regex=True)
    return df

def get_csv_summary(file_path: str):
    """
    Reads a CSV and returns a 'Text Summary' optimized for LLM context.
    Instead of sending the whole file, we send the Structure + Sample.
    """
    try:
        # 1. Load Data
        df = pd.read_csv(file_path)
        df = clean_column_names(df)
        
        # 2. Extract Key Info
        rows, cols = df.shape
        columns = list(df.columns)
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
            summary_text += f"\n- {col}: {types[col]} | {missing[col]} missing"
            
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