import pydicom
import numpy as np
import pytest
from pathlib import Path
from core.volume.dicom_engine import DicomEngine
from core.volume.validator import DicomValidator

PASTA_TESTE = r"D:/Jozeias Fernandes/Odontologia/Formação/5 Doutorado/Pacientes/Luzia Cicera - Patologia_Maxila/TC"

class TestDicomPipeline:

    def test_verificar_bibliotecas_compressao(self):
        from pydicom.pixels.decoders import base
        try:
            available_decoders = base._DECODERS.keys()
            print(f"\nDecodificadores registrados: {list(available_decoders)}")
            assert len(available_decoders) > 0, "Nenhum decodificador encontrado."
        except AttributeError:
            import pydicom.pixels.decoders as decoders
            print("\nVerificando suporte a pixels via pydicom.pixels...")
            assert hasattr(pydicom.pixels, 'pixel_array'), "Erro no suporte a pixels do pydicom."

    def test_leitura_individual_e_pixel_array(self):
        arquivos = list(Path(PASTA_TESTE).glob("*.dcm"))
        if not arquivos:
            arquivos = [f for f in Path(PASTA_TESTE).iterdir() if f.is_file()]

        assert len(arquivos) > 0, "Pasta vazia ou sem arquivos DICOM."

        exemplo = arquivos[0]
        try:
            ds = pydicom.dcmread(str(exemplo))
            pixels = ds.pixel_array
            print(f"\nFatia: {exemplo.name} | Resolução: {pixels.shape} | Tipo: {pixels.dtype}")
            assert pixels is not None
        except Exception as e:
            pytest.fail(f"Erro ao descompactar pixels de {exemplo.name}: {e}")

    def test_consistencia_geometrica_pelo_validador(self):
        validator = DicomValidator("temp_test_output")
        resultado = validator.analisar_caminho(PASTA_TESTE)

        assert resultado["sucesso"] is True, f"Validador falhou: {resultado.get('erro')}"

        for key, fatias in resultado["series"].items():
            print(f"\nSérie: {key} | Total fatias: {len(fatias)}")
            res_referencia = (fatias[0]['rows'], fatias[0]['cols'])
            for f in fatias:
                assert (f['rows'], f['cols']) == res_referencia, "Fatias com resoluções diferentes na mesma série!"

    def test_processamento_completo_engine(self):
        engine = DicomEngine()
        sucesso, msg = engine.carregar_pasta(PASTA_TESTE)

        print(f"\nResultado Engine: {msg}")
        assert sucesso is True, f"Engine não conseguiu montar o volume: {msg}"
        assert engine.vtk_volume is not None, "VTK Volume não foi gerado."
        assert engine.volume_data.ndim == 3, "O dado gerado não é um volume 3D."