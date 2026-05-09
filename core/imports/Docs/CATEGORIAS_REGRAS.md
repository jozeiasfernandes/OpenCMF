# Regras de Categorização de Importação

## Visão Geral

O sistema de importação de objetos no OpenCMF funciona em duas camadas:

### 1️⃣ Camada de Apresentação (import_panel.py)
- Exibe categorias e subcategorias ao usuário
- Emite sinais: `importRequested(categoria, subcategoria)`

### 2️⃣ Camada de Processamento (object_manager.py)
- Recebe categoria e subcategoria do painel
- Mapeia para estrutura de pastas e tipos de arquivo
- Valida a combinação categoria/subcategoria
- Salva na pasta correta com metadados

---

## Mapeamento de Categorias

| Categoria UI | Pasta Salva | Tipo em ObjectProperties |
|---|---|---|
| **Superfícies** | `surfaces/` | `"surfaces"` |
| **Fotografias** | `photos/` | `"photos"` |
| **Volume** | `volume/` | `"volume"` |
| (Inválida) | `others/` | `"others"` |

---

## Subcategorias Válidas

### 📦 Superfícies → surfaces/
- Crânio → `"cranio"`
- Maxila → `"maxila"`
- Mandíbula → `"mandibula"`
- Pele → `"pele"`
- Outros → `"outros"`

### 📷 Fotografias → photos/
- Frente → `"frente"`
- Perfil → `"perfil"`
- Intrabucal → `"intrabucal"`
- Outros → `"outros"`

### 📊 Volume → volume/
- Volume .vti → `"volume_vti"`

---

## Fluxo de Exemplo

### Cenário: Usuário importa Mandíbula

```
1. Usuario clica em: Superfícies > Mandíbula
   ↓
2. import_panel.py emite: 
   importRequested("Superfícies", "Mandíbula")
   ↓
3. registration.py recebe e chama:
   object_manager.import_object(file_path, "Superfícies", "Mandíbula")
   ↓
4. object_manager.py processa:
   - Valida: "Superfícies" existe? ✓ SIM
   - Valida: "Mandíbula" existe para superfícies? ✓ SIM
   - Mapeia pasta: "Superfícies" → "surfaces"
   - Cria: patient_path/surfaces/Mandibula.stl
   - Cria: patient_path/surfaces/Mandibula.json (metadados)
   ↓
5. ObjectProperties criado com:
   - type: "surfaces"
   - name: "Mandíbula" (nome amigável exibido na UI)
   - file_path: "surfaces/Mandibula.stl" (relativo ao paciente)
```

---

## Validação e Tratamento de Erros

### ✅ Caso Válido
```
Categoria: "Superfícies" ✓ (existe em CATEGORIA_MAPPING)
Subcategoria: "Maxila" ✓ (existe em SUBCATEGORIA_MAPPING["surfaces"])
→ Arquivo salvo em: surfaces/Maxila_001.stl
```

### ⚠️ Categoria Inválida
```
Categoria: "Superfície" ✗ (não existe)
→ Log WARNING: "Categoria não mapeada"
→ Usa fallback: "others"
→ Arquivo salvo em: others/arquivo.stl
```

### ⚠️ Subcategoria Inválida
```
Categoria: "Superfícies" ✓ (válida)
Subcategoria: "Perna" ✗ (não existe para surfaces)
→ Log WARNING: "Subcategoria não reconhecida"
→ Continua normalmente mas registra aviso
→ Arquivo salvo em: surfaces/arquivo.stl
```

---

## Estrutura de Pastas do Paciente

```
PRJ_xxxx_PACIENTE/
├── surfaces/
│   ├── Mandibula.stl
│   ├── Mandibula.json
│   ├── Maxila.stl
│   └── Maxila.json
├── photos/
│   ├── Frente.jpg
│   └── Frente.json
├── volume/
│   ├── Volume.vti
│   └── Volume.json
└── others/
    └── (arquivos sem categoria definida)
```

---

## Como Adicionar Nova Subcategoria

### 1. Atualizar import_panel.py

```python
def _setup_sections(self, layout: QVBoxLayout) -> None:
    superficies = [
        (tr("import.superficies.cranio", "Crânio"), "cranio.svg"),
        # ... adicionar aqui:
        (tr("import.superficies.nova", "Nova Estrutura"), "nova.svg")
    ]
```

### 2. Atualizar SUBCATEGORIA_MAPPING em object_manager.py

```python
SUBCATEGORIA_MAPPING = {
    "surfaces": {
        # ... existentes ...
        "Nova Estrutura": "nova_estrutura"  # ← ADICIONAR AQUI
    }
}
```

### 3. Atualizar traduções
- `core/localization/translations/pt_BR.json`
- `core/localization/translations/en_US.json`
- `core/localization/translations/es_ES.json`

---

## Logs Gerados

```
DEBUG - ObjectManager inicializado para paciente: C:\OpenCMF\patients\PRJ_xxx
DEBUG - Caminho único gerado: Mandibula.stl
INFO - Arquivo importado: Mandibula.stl -> surfaces\Mandibula.stl
DEBUG - Metadados salvos: C:\OpenCMF\patients\PRJ_xxx\surfaces\Mandibula.json
DEBUG - Objeto adicionado ao gerenciador: UUID - Mandíbula
```

---

## Dicas de Debug

1. **Arquivo vai para "others"?**
   - Verifique se categoria está exatamente igual em CATEGORIA_MAPPING
   - Sensível a maiúsculas/minúsculas e acentos

2. **Arquivo não aparece na UI?**
   - Verifique se metadados .json foi salvo
   - Verifique log: "Objeto adicionado ao gerenciador"

3. **Subcategoria não validada?**
   - Log WARNING: "Subcategoria não reconhecida"
   - Arquivo ainda será salvo, mas com aviso

