# codificar_chave.py
import base64

# COLOQUE SUA CHAVE REAL AQUI
api_key_original = "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" 

# Codifica a chave para Base64
chave_codificada_bytes = base64.b64encode(api_key_original.encode('utf-8'))
chave_codificada_string = chave_codificada_bytes.decode('utf-8')

print("Sua chave codificada em Base64 é:")
print(chave_codificada_string) 
