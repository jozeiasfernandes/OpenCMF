Regras de Gestão de Ativos e Categorização 

1. Filosofia do Sistema
O OpenCMF utiliza agora um modelo de Persistência Centralizada.O Ficheiro Mestre: Toda a inteligência da cena reside em project/scene.cmf.O Gestor: O PatientFileManager (antigo ObjectManager) é o único responsável por tocar no disco.Caminhos: Todos os caminhos de ficheiros são relativos à raiz da pasta do paciente para garantir portabilidade total.
2. Mapeamento de Pastas e TiposO PatientFileManager organiza os ficheiros importados seguindo esta hierarquia rigorosa:Categoria TécnicaSubpasta FísicaFormatos SuportadosDescriçãosurfacessurfaces/.stl, .obj, .plyMalhas 3D e modelos anatómicos.photosphotos/.jpg, .png, .tiffFotografias clínicas e texturas.volumevolume/.vti, .vtpVolumes processados e segmentações VTK.dicomdicom/.dcmFicheiros brutos de tomografia.projectproject/.cmf, .jsonMetadados da cena e configurações.
3. Fluxo de Importação de ObjetosO fluxo foi desenhado para ser unidirecional e à prova de erros:Seleção (UI): O import_objects_panel.py solicita um ficheiro e define a categoria (ex: surfaces).Cópia Física: O PatientFileManager copia o ficheiro para a subpasta correta.Regra de Colisão: Se o ficheiro maxila.stl já existir, ele renomeia automaticamente para maxila_1.stl.Registo de Cena: Um novo SceneObject é instanciado com um UUID único.Serialização: O Serializer converte o objeto para JSON e atualiza o ficheiro scene.cmf.Evento: O sinal object_added é disparado, permitindo que o SceneManager crie o ator 3D correspondente.
4. Estrutura do Ficheiro .cmfO ficheiro de cena centraliza as propriedades que antes estavam espalhadas em múltiplos JSONs:JSON{
  "version": "2.0",
  "objects": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Mandíbula Inferior",
      "type": "surfaces",
      "file_path": "surfaces/mand_v1.stl",
      "render": {
        "color": [0.9, 0.8, 0.7],
        "opacity": 1.0,
        "visible": true
      },
      "transform": {
        "matrix": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
      }
    }
  ]
}
5. Manutenção e Boas Práticas⚠️ Importante: PortabilidadeNunca grave caminhos absolutos (ex: C:/Users/...). Use sempre o método destination.relative_to(self.patient_path) no PatientFileManager.🔄 SincronizaçãoSempre que uma propriedade visual (cor, visibilidade) for alterada na object_properties_toolbox, o método save_scene() deve ser chamado para garantir que o .cmf esteja atualizado.🗑️ Remoção de ObjetosAo remover um objeto, o PatientFileManager remove a entrada do ficheiro .cmf. Por segurança, o ficheiro físico (.stl, .vti) não deve ser apagado automaticamente, permitindo recuperação manual se necessário.
6. Logs e DiagnósticoINFO: "Objeto [Nome] registado com ID [UUID]" -> Sucesso total.WARNING: "Ficheiro já existe, renomeando para..." -> Conflito de nome resolvido.ERROR: "Falha ao serializar cena" -> Erro crítico de permissão de escrita ou JSON corrompido.