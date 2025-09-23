# Controle de Acesso ao Módulo E-commerce (Mercado Livre)

## Visão Geral

O sistema agora inclui controle de acesso granular para o módulo Mercado Livre (e-commerce), permitindo que administradores bloqueiem ou concedam acesso individualmente para cada usuário.

## Como Funciona

### Campo de Controle
- **Campo**: `ACESSO_ECOMMERCE` na tabela `USUARIOS`
- **Tipo**: `CHAR(1)`
- **Valores**:
  - `'S'` = Acesso permitido (padrão)  
  - `'N'` = Acesso bloqueado

### Verificação de Acesso
1. **Usuário Individual**: Sistema verifica o campo `ACESSO_ECOMMERCE` do usuário
2. **Usuário Vinculado**: Se o usuário está vinculado a um master, também verifica o acesso do usuário master
3. **Segurança**: Em caso de erro na verificação, o acesso é negado por segurança

## Interface do Usuário

### Menu Principal
- Novo botão "MERCADO LIVRE" adicionado ao menu principal
- Acesso controlado automaticamente quando o usuário clica no menu

### Mensagens de Erro
Quando o acesso é negado, o usuário vê uma mensagem clara:
```
Acesso Bloqueado
Acesso ao módulo Mercado Livre negado.

[Motivo específico]

Entre em contato com o administrador.
```

## Funcionalidades Técnicas

### Funções de Banco de Dados

#### `verificar_acesso_ecommerce(usuario, empresa=None)`
Verifica se um usuário tem acesso ao módulo e-commerce.

**Parâmetros:**
- `usuario` (str): Nome do usuário
- `empresa` (str, opcional): Nome da empresa

**Retorna:**
- `tuple`: `(bool, str)` - `(tem_acesso, motivo_bloqueio)`

#### `alterar_acesso_ecommerce(usuario_id, permitir_acesso, empresa=None)`
Altera o acesso ao e-commerce para um usuário específico.

**Parâmetros:**
- `usuario_id` (int): ID do usuário
- `permitir_acesso` (bool): True para permitir, False para bloquear
- `empresa` (str, opcional): Nome da empresa

#### `listar_usuarios_sem_acesso_ecommerce()`
Lista todos os usuários que não têm acesso ao e-commerce.

**Retorna:**
- `list`: Lista de usuários bloqueados

### Migração Automática
- O sistema automaticamente adiciona o campo `ACESSO_ECOMMERCE` em tabelas existentes
- Usuários existentes recebem acesso por padrão (`'S'`)
- Processo executado durante a inicialização do sistema

## Cenários de Uso

### Scenario 1: Usuário com Acesso
```python
# Usuário: joao, Empresa: TESTE
# ACESSO_ECOMMERCE = 'S'
tem_acesso, motivo = verificar_acesso_ecommerce("joao", "TESTE")
# Resultado: (True, "")
```

### Scenario 2: Usuário Bloqueado
```python
# Usuário: maria, Empresa: TESTE  
# ACESSO_ECOMMERCE = 'N'
tem_acesso, motivo = verificar_acesso_ecommerce("maria", "TESTE")
# Resultado: (False, "Acesso ao módulo Mercado Livre (e-commerce) está bloqueado para este usuário")
```

### Scenario 3: Usuário Vinculado com Master Bloqueado
```python
# Usuário: funcionario (vinculado ao master ID 1)
# Usuário funcionario: ACESSO_ECOMMERCE = 'S'
# Master (ID 1): ACESSO_ECOMMERCE = 'N'
tem_acesso, motivo = verificar_acesso_ecommerce("funcionario", "TESTE")
# Resultado: (False, "Acesso ao módulo Mercado Livre (e-commerce) está bloqueado para a conta principal")
```

## Administração

### Bloquear Acesso de um Usuário
```python
# Via SQL direto
UPDATE USUARIOS SET ACESSO_ECOMMERCE = 'N' WHERE ID = 123;

# Via função do sistema
alterar_acesso_ecommerce(123, False)
```

### Conceder Acesso de um Usuário
```python
# Via SQL direto
UPDATE USUARIOS SET ACESSO_ECOMMERCE = 'S' WHERE ID = 123;

# Via função do sistema  
alterar_acesso_ecommerce(123, True)
```

### Listar Usuários Bloqueados
```python
usuarios_bloqueados = listar_usuarios_sem_acesso_ecommerce()
for usuario in usuarios_bloqueados:
    print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Empresa: {usuario[2]}")
```

## Estrutura de Arquivos

```
ecommerce/
├── __init__.py                 # Módulo de inicialização
└── mercado_livre.py           # Interface principal do e-commerce

base/
└── banco.py                   # Funções de controle de acesso adicionadas

principal.py                   # Menu principal atualizado com botão Mercado Livre
```

## Segurança

### Princípios de Segurança
1. **Fail-Safe**: Em caso de erro, o acesso é negado
2. **Validação Dupla**: Usuários vinculados têm seu master verificado também
3. **Logging**: Todas as verificações são registradas para auditoria
4. **Mensagens Claras**: Usuários recebem feedback claro sobre bloqueios

### Recomendações
- Revisar periodicamente usuários com acesso ao e-commerce
- Monitorar logs de acesso negado para detectar tentativas não autorizadas
- Manter backup das configurações de acesso antes de fazer alterações em massa

## Troubleshooting

### Problema: Usuário não consegue acessar o módulo
1. Verificar campo `ACESSO_ECOMMERCE` do usuário
2. Se usuário vinculado, verificar acesso do master
3. Verificar logs do sistema para erros de banco de dados

### Problema: Campo ACESSO_ECOMMERCE não existe
- O sistema deve criar automaticamente na primeira execução
- Se não criou, executar manualmente: `verificar_e_adicionar_campo_ecommerce()`

### Problema: Erro de permissão
- Verificar se o usuário do banco tem permissão para ALTER TABLE
- Verificar conectividade com o banco de dados