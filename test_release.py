"""
Script de Teste - Verificar Release no GitHub
Execute este script para diagnosticar problemas com o release
"""

import requests
import json

# ===== CONFIGURAÇÕES =====
REPO_OWNER = "Marco-Antonio-2003"
REPO_NAME = "Sistema-de-Gerenciamento-de-Mercado"
VERSAO_PARA_TESTAR = "v0.1.5.4.1"  # <<<< MUDE AQUI PARA A VERSÃO QUE VOCÊ CRIOU

print("=" * 70)
print("🔍 DIAGNÓSTICO DE RELEASE NO GITHUB")
print("=" * 70)
print()

# ===== TESTE 1: Verificar se o release existe =====
print("📋 TESTE 1: Verificando se o release existe...")
print(f"   Tag procurada: {VERSAO_PARA_TESTAR}")
print()

api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{VERSAO_PARA_TESTAR}"

headers = {
    'User-Agent': 'MBSistema-UpdateChecker/1.0',
    'Accept': 'application/vnd.github.v3+json'
}

try:
    response = requests.get(api_url, headers=headers, timeout=10)
    
    if response.status_code == 404:
        print("❌ ERRO: Release não encontrado!")
        print()
        print("   Possíveis causas:")
        print("   1. A tag não existe no GitHub")
        print("   2. A tag está escrita diferente (ex: 'v0.1.5.4.1' vs '0.1.5.4.1')")
        print()
        print("   🔧 SOLUÇÃO:")
        print("   - Vá em: https://github.com/{}/{}/releases".format(REPO_OWNER, REPO_NAME))
        print("   - Crie um novo release com a tag EXATA: {}".format(VERSAO_PARA_TESTAR))
        print()
        
        # Listar releases existentes
        print("   📌 Verificando releases existentes...")
        all_releases_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
        all_response = requests.get(all_releases_url, headers=headers, timeout=10)
        
        if all_response.status_code == 200:
            releases = all_response.json()
            if releases:
                print(f"   ✅ Encontrados {len(releases)} release(s):")
                for rel in releases[:5]:  # Mostrar apenas os 5 mais recentes
                    print(f"      • Tag: {rel.get('tag_name')} | Nome: {rel.get('name')}")
            else:
                print("   ⚠️  Nenhum release encontrado no repositório")
        
        exit(1)
    
    response.raise_for_status()
    release_data = response.json()
    
    print("✅ Release encontrado!")
    print(f"   Nome: {release_data.get('name')}")
    print(f"   Tag: {release_data.get('tag_name')}")
    print(f"   Criado em: {release_data.get('created_at')}")
    print()
    
except requests.exceptions.RequestException as e:
    print(f"❌ ERRO ao conectar: {e}")
    exit(1)

# ===== TESTE 2: Verificar assets (arquivos) =====
print("📦 TESTE 2: Verificando arquivos anexados (assets)...")
print()

assets = release_data.get('assets', [])

if not assets:
    print("❌ ERRO: Nenhum arquivo foi anexado a este release!")
    print()
    print("   🔧 SOLUÇÃO:")
    print("   1. Vá em: https://github.com/{}/{}/releases/tag/{}".format(
        REPO_OWNER, REPO_NAME, VERSAO_PARA_TESTAR
    ))
    print("   2. Clique em 'Edit'")
    print("   3. Arraste seu arquivo .exe para a área de 'Attach binaries'")
    print("   4. Clique em 'Update release'")
    print()
    exit(1)

print(f"✅ Encontrados {len(assets)} arquivo(s):")
print()

exe_encontrado = False

for i, asset in enumerate(assets, 1):
    nome = asset.get('name', 'sem nome')
    tamanho = asset.get('size', 0)
    tamanho_mb = tamanho / (1024 * 1024)
    download_url = asset.get('browser_download_url', '')
    
    print(f"   {i}. {nome}")
    print(f"      Tamanho: {tamanho_mb:.2f} MB")
    print(f"      URL: {download_url}")
    
    if nome.lower().endswith('.exe'):
        print(f"      ✅ É um arquivo .exe - SERÁ USADO PARA ATUALIZAÇÃO")
        exe_encontrado = True
    else:
        print(f"      ⚠️  Não é um arquivo .exe")
    
    print()

# ===== TESTE 3: Verificar se há pelo menos um .exe =====
print("🎯 TESTE 3: Verificando compatibilidade...")
print()

if not exe_encontrado:
    print("❌ ERRO: Nenhum arquivo .exe encontrado!")
    print()
    print("   O sistema de atualização automática precisa de pelo menos")
    print("   um arquivo .exe anexado ao release.")
    print()
    print("   🔧 SOLUÇÃO:")
    print("   - Anexe seu arquivo executável (ex: MBSistema.exe)")
    print()
    exit(1)

print("✅ Pelo menos um arquivo .exe foi encontrado!")
print()

# ===== TESTE 4: Testar download =====
print("🌐 TESTE 4: Testando se o arquivo pode ser baixado...")
print()

# Pegar o primeiro .exe encontrado
exe_asset = None
for asset in assets:
    if asset.get('name', '').lower().endswith('.exe'):
        exe_asset = asset
        break

if exe_asset:
    download_url = exe_asset.get('browser_download_url')
    print(f"   Testando URL: {download_url}")
    
    try:
        # Fazer requisição HEAD para verificar se o arquivo existe
        head_response = requests.head(download_url, timeout=10)
        
        if head_response.status_code == 200:
            print("   ✅ Arquivo acessível e pronto para download!")
            print()
        else:
            print(f"   ❌ ERRO: Status code {head_response.status_code}")
            print()
    except Exception as e:
        print(f"   ❌ ERRO ao testar download: {e}")
        print()

# ===== RESULTADO FINAL =====
print("=" * 70)
print("📊 RESUMO DO DIAGNÓSTICO")
print("=" * 70)
print()
print(f"Release: {release_data.get('tag_name')} - {release_data.get('name')}")
print(f"Assets: {len(assets)} arquivo(s)")
print(f"Arquivos .exe: {'✅ Encontrado' if exe_encontrado else '❌ Não encontrado'}")
print()

if exe_encontrado:
    print("✅ TUDO CERTO! O sistema de atualização automática deve funcionar.")
    print()
    print("🔗 Link do release:")
    print(f"   https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{VERSAO_PARA_TESTAR}")
else:
    print("❌ AÇÃO NECESSÁRIA: Adicione um arquivo .exe ao release.")

print()
print("=" * 70)