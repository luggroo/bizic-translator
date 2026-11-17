from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from tujia_lex.loan_lookup import main
if __name__=='__main__':main()
