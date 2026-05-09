# Renomeação de Objetos - Mudanças Implementadas

## 📋 Resumo das Mudanças

Implementei um sistema completo de renomeação de objetos importados, permitindo que o usuário:
1. Veja o **nome original do arquivo** no JSON e na UI
2. **Renomeie** objetos com duplo clique
3. As mudanças sejam **refletidas** em tempo real

---

## 🔧 Alterações Técnicas

### 1️⃣ **object_manager.py** (Camada de Processamento)

#### Mudança: Nome do arquivo em vez de subcategoria

**Antes:**
```python
props = ObjectProperties(
    name=sub_category,  # "Importado" (genérico)
    type=folder,
    file_path=str(destination.relative_to(self.patient_path)),
    format=source.suffix.lower().replace(".", "")
)
```

**Depois:**
```python
props = ObjectProperties(
    name=destination.stem,  # "maxila01" (nome real do arquivo)
    type=folder,
    file_path=str(destination.relative_to(self.patient_path)),
    format=source.suffix.lower().replace(".", "")
)
```

**Resultado no JSON:**
```json
{
    "id": "53041a44-097c-40dc-9e6e-320a8079f665",
    "name": "maxila01",  // ✅ Nome original do arquivo
    "type": "surfaces",
    "file_path": "surfaces\\maxila01.stl"
}
```

---

### 2️⃣ **object_manager_toolbox.py** (UI - Gerenciador)

#### Mudança 1: Novo signal para renomeação
```python
nomeAlterado = QtCore.Signal(str, str)  # (nome_antigo, nome_novo)
```

#### Mudança 2: Suporte a duplo clique para editar
```python
def _on_double_clicked(self, index: QtCore.QModelIndex) -> None:
    item = self.tree_widget.itemFromIndex(index)
    nome_original = item.text(0)
    novo_nome, ok = QtWidgets.QInputDialog.getText(
        self,
        "Renomear Objeto",
        f"Nome atual: {nome_original}",
        QtWidgets.QLineEdit.Normal,
        nome_original
    )
    
    if ok and novo_nome and novo_nome != nome_original:
        item.setText(0, novo_nome)
        self.nomeAlterado.emit(nome_original, novo_nome)
```

#### Mudança 3: Mapeamento de objetos por ID
```python
def adicionar_objeto_lista(self, nome: str, categoria: str = "Superfícies", cor=None, objeto_id: str = None):
    # ...
    if objeto_id:
        self.objetos_mapeados[nome] = objeto_id
        item.setData(0, QtCore.Qt.UserRole, objeto_id)
```

#### Mudança 4: Type hints completos
```python
def _get_or_create_category(self, cat_name: str) -> QtWidgets.QTreeWidgetItem:
def _show_context_menu(self, position: QtCore.QPoint) -> None:
def _on_double_clicked(self, index: QtCore.QModelIndex) -> None:
def _pick_color(self, name: str, button: QtWidgets.QPushButton) -> None:
```

---

### 3️⃣ **registration.py** (Módulo - Lógica de Negócio)

#### Mudança 1: Conexão do sinal de renomeação
```python
def _conectar_sinais(self):
    # ... sinais existentes ...
    self.widget_objetos.nomeAlterado.connect(self._on_nome_alterado)
```

#### Mudança 2: Função para mapear categoria de volta
```python
def _mapear_categoria_para_tipo(self, tipo_pasta: str) -> str:
    mapeamento = {
        "surfaces": "Superfícies",
        "photos": "Fotografias",
        "volume": "Volume",
        "others": "Outros"
    }
    return mapeamento.get(tipo_pasta, "Outros")
```

#### Mudança 3: Passar ID ao adicionar objeto
```python
def _on_object_added_manager(self, props):
    categoria_mapeada = self._mapear_categoria_para_tipo(props.type)
    self.widget_objetos.adicionar_objeto_lista(
        props.name, 
        categoria_mapeada, 
        props.render["color"],
        objeto_id=props.id  # ✅ Novo
    )
```

#### Mudança 4: Manipular renomeação de objetos
```python
def _on_nome_alterado(self, nome_original: str, novo_nome: str) -> None:
    props = next((p for p in self.object_manager.objects.values() 
                 if p.name == nome_original), None)
    if props:
        props.name = novo_nome
        logger.info(f"Objeto renomeado: {nome_original} -> {novo_nome}")
        self.widget_reg.atualizar_combos(
            [obj.name for obj in self.object_manager.objects.values()]
        )
```

---

## 🖱️ Fluxo de Uso

### Importação Normal
```
1. Usuário clica em Importar
2. Seleciona "maxila01.stl"
3. Arquivo salvo em: surfaces/maxila01.stl
4. JSON criado com: "name": "maxila01"
5. UI mostra: "maxila01" na categoria "Superfícies"
```

### Renomeação
```
1. Usuário faz DUPLO CLIQUE no item "maxila01"
2. Diálogo aparece permitindo edição
3. Usuário digita: "Maxila do Paciente 1"
4. nomeAlterado.emit("maxila01", "Maxila do Paciente 1")
5. ObjectProperties.name atualizado em memória
6. UI atualiza para mostrar: "Maxila do Paciente 1"
```

---

## 📊 Estrutura de Dados Após Mudanças

### Arquivo JSON (surfaces/maxila01.json)
```json
{
    "id": "53041a44-097c-40dc-9e6e-320a8079f665",
    "name": "maxila01",
    "type": "surfaces",
    "file_path": "surfaces\\maxila01.stl",
    "format": "stl",
    "visible": true,
    "locked": false,
    "opacity": 1.0,
    "render": {
        "color": [0.3, 0.6, 1.0],
        ...
    }
}
```

### UI - TreeWidget
```
Superfícies                    Opacidade    Cor
├── crânio                       100%       ■
├── maxila01                     100%       ■
├── Maxila do Paciente 1         100%       ■ (renomeado)
└── mandíbula                    100%       ■

Fotografias
├── Frente                       100%       ■
└── Perfil                       100%       ■
```

---

## 🔍 Logging Adicionado

```
INFO - Objeto renomeado: maxila01 -> Maxila do Paciente 1
INFO - Objeto deletado: Maxila do Paciente 1
DEBUG - Objeto renomeado: maxila01 -> Maxila do Paciente 1
```

---

## ✅ Benefícios

1. ✅ **Identificação Clara**: Usuário sabe exatamente qual arquivo é qual
2. ✅ **Flexibilidade**: Pode renomear para nomes descritivos
3. ✅ **Rastreabilidade**: Nome original preservado no arquivo do disco
4. ✅ **Usabilidade**: Duplo clique é padrão em aplicações
5. ✅ **Robustez**: Validação e logging para debug

---

## 🧪 Como Testar

```shell
# 1. Execute a aplicação normalmente
python main.py

# 2. Importe um arquivo (ex: mandibula.stl)
# 3. Verifique o JSON:
cat patients/PRJ_xxx/surfaces/mandibula.json
# Deve showname": "mandibula"

# 4. Duplo clique na UI em "mandibula"
# 5. Digite novo nome: "Mandíbula Modificada"
# 6. Verifique os logs:
# INFO - Objeto renomeado: mandibula -> Mandíbula Modificada
```

---

## 📝 Notas

- O nome original do arquivo é **preservado no disco**
- Renomeações acontecem **apenas em memória** (ObjectProperties)
- Para persistir renomeações, seria necessário salvar JSON atualizado (feature futura)
- Type hints adicionados em todo o código para clareza

