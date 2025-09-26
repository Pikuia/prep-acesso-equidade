# supabase_client.py
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# tenta carregar .env no diretório do script; se não achar, tenta no CWD
here = Path(__file__).resolve().parent
env_file = here / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

def get_supabase(backend: bool = False) -> Client:
    """
    backend=False -> ANON (inserts do formulário, respeitando RLS)
    backend=True  -> SERVICE ROLE (leituras/ML no servidor)
    """
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY" if backend else "SUPABASE_ANON_KEY"]
    return create_client(url, key)