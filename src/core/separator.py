import os
import uuid
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tempfile
import logging

from demucs import pretrained
from demucs.apply import apply_model
from demucs.audio import AudioFile
import torch
from pydub import AudioSegment
import torchaudio

# Configurar logging
logger = logging.getLogger(__name__)

# Usar apenas o modelo básico que funciona
DEFAULT_MODEL = 'mdx_extra_q'
# Definir stems disponíveis e suas configurações
AVAILABLE_STEMS = {
    'drums': {'index': 0, 'name': 'Bateria', 'icon': '🥁'},
    'bass': {'index': 1, 'name': 'Baixo', 'icon': '🎸'},
    'other': {'index': 2, 'name': 'Outros', 'icon': '🎵'},
    'vocals': {'index': 3, 'name': 'Vocais', 'icon': '🎤'},
    'instrumental': {'name': 'Instrumental', 'icon': '🎹'}  # Combinação de drums + bass + other
}


class AudioSeparator:
    def __init__(self, output_dir: str = "static/output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar otimizações de GPU
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Usar sempre o modelo básico que funciona
        self.model_name = DEFAULT_MODEL
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Carregar o modelo
        try:
            logger.info(f"🔄 Carregando modelo básico '{self.model_name}'...")
            self.model = pretrained.get_model(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"✅ Modelo carregado: {self.model_name}")
            logger.info(f"Dispositivo: {self.device}")
            if torch.cuda.is_available():
                logger.info(f"GPU detectada: {torch.cuda.get_device_name()}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo: {e}")
            raise Exception(f"Não foi possível carregar o modelo: {e}")

    def separate_stems(
        self, 
        input_file_path: str, 
        selected_stems: List[str] = None
    ) -> Dict[str, str]:
        """
        Separa o áudio nos stems selecionados usando o modelo Demucs.
        
        Args:
            input_file_path: Caminho para o arquivo de áudio de entrada
            selected_stems: Lista de stems para extrair. Se None, extrai apenas 'vocals'
            
        Returns:
            Dict com os caminhos relativos para os arquivos gerados
            
        Raises:
            ValueError: Se o arquivo de entrada não for válido ou stems inválidos
            Exception: Para outros erros durante o processamento
        """
        try:
            # Validar entrada
            if not os.path.exists(input_file_path):
                raise ValueError(f"Arquivo não encontrado: {input_file_path}")
            
            # Se não especificado, usar apenas vocals por padrão
            if selected_stems is None:
                selected_stems = ['vocals']
            
            # Validar stems selecionados
            invalid_stems = [stem for stem in selected_stems if stem not in AVAILABLE_STEMS]
            if invalid_stems:
                raise ValueError(f"Stems inválidos: {invalid_stems}. Disponíveis: {list(AVAILABLE_STEMS.keys())}")
            
            # Gerar ID único para os arquivos de saída
            unique_id = str(uuid.uuid4())[:8]
            
            logger.info(f"Processando stems: {selected_stems}")
            
            # Criar diretório temporário para o processamento
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                logger.info("Carregando arquivo de áudio...")
                # Carregar o áudio
                audio_file = AudioFile(input_file_path)
                wav_data = audio_file.read()
                
                # Aplicar o modelo para separação
                logger.info("Iniciando separação de áudio...")
                
                # Garantir que wav_data está no device correto
                if wav_data.device != torch.device(self.device):
                    wav_data = wav_data.to(self.device)
                
                logger.info(f"Tensor de entrada: {wav_data.shape}, device: {wav_data.device}, dtype: {wav_data.dtype}")
                
                # Usar separação simples sempre
                logger.info("🔄 Processando com modelo básico...")
                
                with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
                    sources = apply_model(
                        self.model, 
                        wav_data, 
                        device=self.device, 
                        progress=True,
                        segment=10,
                        overlap=0.25
                    )
                
                # Normalizar formato do tensor de forma simples
                logger.info(f"Formato original: {sources.shape}")
                
                # Se tensor tem 4 dimensões [batch, sources, channels, length], remover batch
                if len(sources.shape) == 4 and sources.shape[0] == 1:
                    sources = sources[0]
                    logger.info(f"Batch removido: {sources.shape}")
                
                # Verificar se temos formato [sources, channels, length]
                if len(sources.shape) != 3:
                    raise ValueError(f"Formato inesperado: {sources.shape}. Esperado: [sources, channels, length]")
                
                num_sources, num_channels, audio_length = sources.shape
                logger.info(f"✅ Tensor processado: {num_sources} sources, {num_channels} channels, {audio_length} samples")
                
                # Verificar se temos o número esperado de stems
                if num_sources < 4:
                    raise ValueError(f"Modelo retornou {num_sources} sources. Esperado: 4 (drums, bass, other, vocals)")
                
                # Processar cada stem selecionado
                result_paths = {}
                
                for stem in selected_stems:
                    logger.info(f"🎵 Processando stem: {stem}")
                    
                    if stem == 'instrumental':
                        # Instrumental é a combinação de drums + bass + other
                        audio_data = sources[0] + sources[1] + sources[2]
                        filename = f"instrumental_{unique_id}.mp3"
                    else:
                        # Stem individual
                        stem_index = AVAILABLE_STEMS[stem]['index']
                        audio_data = sources[stem_index]
                        filename = f"{stem}_{unique_id}.mp3"
                    
                    # Mover para CPU e garantir formato correto
                    audio_data = audio_data.cpu()
                    if audio_data.dtype == torch.float16:
                        audio_data = audio_data.float()
                    
                    # Salvar arquivo WAV temporário
                    wav_path = temp_path / f"{stem}_{unique_id}.wav"
                    sample_rate = getattr(self.model, 'samplerate', 44100)
                    torchaudio.save(str(wav_path), audio_data, sample_rate=sample_rate)
                    
                    # Converter para MP3
                    mp3_path = self.output_dir / filename
                    audio_segment = AudioSegment.from_wav(str(wav_path))
                    audio_segment.export(
                        str(mp3_path), 
                        format="mp3", 
                        bitrate="192k",
                        parameters=["-q:a", "4"]
                    )
                    
                    # Adicionar ao resultado
                    result_paths[stem] = f"static/output/{filename}"
                    logger.info(f"✅ Stem {stem} processado: {filename}")
                
                logger.info("✅ Separação concluída com sucesso!")
                
                # Limpar cache de GPU
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                
                return result_paths
                
        except Exception as e:
            logger.error(f"Erro durante a separação: {str(e)}")
            raise Exception(f"Erro durante a separação de áudio: {str(e)}")

    def _normalize_tensor_format(self, sources):
        """
        Normaliza formato do tensor - versão ULTRA SIMPLES.
        """
        logger.info(f"Tensor shape: {sources.shape}")
        
        # Apenas remover batch dimension se necessário
        if len(sources.shape) == 4:
            sources = sources.squeeze(0)
        
        if len(sources.shape) != 3:
            raise ValueError(f"Formato tensor inválido: {sources.shape}")
        
        return sources
        if len(sources.shape) != 3:
            raise ValueError(f"Formato inesperado: {sources.shape}. Esperado 3D após remoção de batch.")
        
        return sources

    def _needs_full_separation(self, selected_stems: List[str]) -> bool:
        """
        Verifica se é necessário fazer separação completa ou se pode otimizar.
        
        Returns:
            True se precisa separar todos os 4 stems
            False se pode otimizar para stems específicos
        """
        # TEMPORARIAMENTE FORÇAR SEPARAÇÃO COMPLETA PARA TODOS OS MODELOS
        # Isso garante estabilidade máxima e evita erros de tensor
        logger.info(f"🔒 Forçando separação completa para garantir estabilidade (modelo: {self.model_name})")
        return True
        
        # O código abaixo pode ser habilitado no futuro quando a otimização estiver 100% estável
        """
        # Modelos mais complexos sempre precisam de separação completa
        complex_models = ['htdemucs', 'htdemucs_ft']
        if self.model_name in complex_models:
            logger.info(f"Modelo {self.model_name} requer separação completa")
            return True
        
        # Para modelos MDX, pode otimizar em casos específicos
        # Se só quer vocals, pode otimizar
        if selected_stems == ['vocals']:
            return False
            
        # Se só quer instrumental, pode otimizar (= não vocals)
        if selected_stems == ['instrumental']:
            return False
            
        # Se quer vocals + instrumental, pode otimizar
        if set(selected_stems) == {'vocals', 'instrumental'}:
            return False
            
        # Para outros casos, precisa da separação completa
        return True
        """

    def _separate_optimized(self, wav_data, selected_stems: List[str]):
        """
        Separação otimizada para casos específicos usando modelo de vocals apenas.
        """
        logger.info("🚀 Usando separação OTIMIZADA (apenas vocals)")
        
        # Para casos otimizados, usar modelo específico de vocals se disponível
        # Por enquanto, usar o modelo completo mas com processamento mais rápido
        with torch.amp.autocast('cuda', enabled=torch.cuda.is_available()):
            sources = apply_model(
                self.model, 
                wav_data, 
                device=self.device, 
                progress=True,
                segment=15,  # Segments maiores para vocals
                overlap=0.1   # Menos overlap para velocidade
            )
        
        # Normalizar formato do tensor usando o método robusto
        sources = self._normalize_tensor_format(sources)
        
        # Verificar se temos o número esperado de stems
        num_sources, num_channels, audio_length = sources.shape
        if num_sources < 4:
            raise ValueError(f"Modelo retornou {num_sources} sources (otimizado). Esperado: 4 (drums, bass, other, vocals)")
            
        return sources

    @staticmethod
    def get_available_stems() -> Dict[str, Dict[str, str]]:
        """Retorna informações sobre os stems disponíveis."""
        return AVAILABLE_STEMS

    def estimate_processing_time(self, selected_stems: List[str]) -> str:
        """
        Estima o tempo de processamento baseado nos stems selecionados e modelo atual.
        """
        # Fatores baseados no modelo
        model_speed_factor = {
            'mdx_extra_q': 1.0,    # Mais rápido
            'mdx': 1.5,            # Moderado
            'htdemucs': 2.5,       # Lento
            'htdemucs_ft': 4.0     # Muito lento
        }
        
        # Fator baseado no dispositivo
        device_factor = 1.0 if torch.cuda.is_available() else 2.0
        
        # Fator baseado na seleção de stems
        stem_factor = 1.0
        if len(selected_stems) == 1 and selected_stems[0] == 'vocals':
            stem_factor = 1.0  # Otimizado
        elif len(selected_stems) == 1 and selected_stems[0] == 'instrumental':
            stem_factor = 1.0  # Otimizado
        elif len(selected_stems) == 2 and 'vocals' in selected_stems and 'instrumental' in selected_stems:
            stem_factor = 1.2  # Karaoke
        elif len(selected_stems) <= 2:
            stem_factor = 1.5  # Poucos stems
        else:
            stem_factor = 2.0  # Múltiplos stems
        
        # Calcular tempo estimado em segundos
        base_time = 30  # Tempo base para mdx_extra_q + GPU + vocals
        total_factor = model_speed_factor.get(self.model_name, 2.0) * device_factor * stem_factor
        estimated_seconds = base_time * total_factor
        
        # Converter para descrição amigável
        if estimated_seconds <= 60:
            return "muito rápido (30-60 segundos)"
        elif estimated_seconds <= 120:
            return "rápido (1-2 minutos)"
        elif estimated_seconds <= 180:
            return "moderado (2-3 minutos)"
        elif estimated_seconds <= 300:
            return "lento (3-5 minutos)"
        else:
            return "muito lento (5+ minutos)"
    
    def _cleanup_gpu_memory(self):
        """Limpa cache de GPU para liberar memória."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()


# Instância global do separador (singleton)
_audio_separator_instance = None

def get_audio_separator():
    """Retorna instância singleton do separador."""
    global _audio_separator_instance
    
    if _audio_separator_instance is None:
        _audio_separator_instance = AudioSeparator()
    
    return _audio_separator_instance

# Compatibilidade
audio_separator = get_audio_separator()


def separate_audio(input_file_path: str, selected_stems: List[str] = None) -> Dict[str, str]:
    """
    Função de conveniência para separar áudio nos stems selecionados.
    """
    separator = get_audio_separator()
    return separator.separate_stems(input_file_path, selected_stems)


# Manter compatibilidade com a função antiga
def separate_vocals(input_file_path: str) -> Tuple[str, str]:
    """
    Função legada para compatibilidade. Separa apenas vocals e instrumental.
    Otimizada para velocidade máxima.
    """
    separator = get_audio_separator()
    result = separator.separate_stems(input_file_path, ['vocals', 'instrumental'])
    return result['vocals'], result['instrumental']
