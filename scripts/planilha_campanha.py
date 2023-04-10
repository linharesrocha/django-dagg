import pandas as pd
import numpy as np
from io import BytesIO

def gerar_excel():
  data = np.array([['Portugal', 'Lisboa', 10000000],
                  ['Peru', 'Lima', 32000000],
                ['Chile', 'Santiago', 18000000],
                    ['Brasil', 'Brasília', 209000000]])

  df = pd.DataFrame(data, index=range(100, 104), columns=['País', 'Capital', 'População'])

  excel_bytes = BytesIO()
  df.to_excel(excel_bytes, index=False)
  
  excel_bytes.seek(0)
  bytes_data = excel_bytes.getvalue()
  
  return bytes_data