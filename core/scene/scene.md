# Arquitetura de Cena OpenCMF

Este documento descreve a infraestrutura desacoplada entre **Lógica de Dados** e **Pipeline de Renderização**, garantindo escalabilidade, manutenção e reatividade global.

---

## 1. Definição de Componentes

Para manter o código limpo e modular, dividimos as responsabilidades em cinco pilares fundamentais:

- **SceneObject (Dados)**:  
  Representação lógica pura do objeto. Contém apenas metadados (ID, nome, tipo), caminho do arquivo e estado (cor, opacidade, visibilidade). **Não possui conhecimento do VTK.**

- **VTKActorFactory (Conversor)**:  
  Fábrica especializada responsável por transformar um `SceneObject` em um `vtkActor` pronto para renderização.

- **ActorRegistry (Armazenamento)**:  
  Dicionário central que mapeia `ID do Objeto` → `vtkActor`. Permite localização rápida do representante visual.

- **VTKSceneRenderer (Renderização)**:  
  Gerencia o motor VTK de uma janela específica. É responsável por adicionar e remover atores fisicamente do renderer.

- **PropertySync (Sincronização)**:  
  Camada de sincronização ("cola" do sistema). Garante que alterações nos dados (`SceneObject`) sejam refletidas automaticamente nos atores visuais.

---

## 2. Fluxo de Importação e Renderização

O ciclo de vida completo de um objeto, desde o arquivo no disco até a exibição na tela, segue o seguinte fluxo:

| Etapa | Componente           | Responsabilidade |
|-------|----------------------|------------------|
| 1     | **ObjectManager**    | I/O de Disco: Copia o arquivo para a pasta do paciente e cria o `SceneObject` inicial. |
| 2     | **SceneManager**     | Orquestração: Recebe o objeto, valida e coordena sua entrada no sistema. |
| 3     | **ObjectRegistry**   | Memória: Armazena o objeto. A partir deste ponto ele existe oficialmente. |
| 4     | **EventBus**         | Comunicação: Dispara o evento `OBJECT_ADDED`. |
| 5     | **SceneBridge**      | Intermediação: Escuta o evento, usa a `VTKActorFactory` e registra o ator no `ActorRegistry`. |
| 6     | **VTKSceneRenderer** | Exibição: Insere o ator no `vtkRenderer` da janela ativa. |

---

## 3. Resumo Estratégico

### 🛡️ Independência Total
A camada de **Lógica de Dados** (`ObjectRegistry` + `SceneObject`) não tem qualquer dependência direta do VTK. Caso seja necessário trocar o motor de renderização no futuro, apenas a `SceneBridge` e a `VTKActorFactory` precisarão ser adaptadas.

### 💾 Persistência Segura
O `ObjectManager` é responsável pelo sistema de arquivos de forma isolada. Problemas na renderização ou na interface não afetam a integridade dos dados salvos do paciente.

### ⚡ Reatividade Global
Qualquer alteração propagada via **EventBus** reflete automaticamente em três frentes:

1. **Visualização 3D** — Atualização imediata dos atores na cena.
2. **Interface Gráfica** — Listas, tabelas e painéis de propriedades.
3. **Persistência** — Salvamento automático do estado no arquivo `.cmf`.

---

**Próximos passos recomendados:**
- Documentar a `SceneBridge`
- Implementar sistema de Undo/Redo
- Adicionar suporte a múltiplas cenas
