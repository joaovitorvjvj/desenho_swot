import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors as rl_colors
    import io
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EPROC/SEPLAN — Planejamento Estratégico",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ══════════════════════════════════════════════════════════════════
ORANGE = "#EC671C"
DARK_BLUE = "#0D1B2A"
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F4F5F7"

# Gradiente de progressão: da base (azul escuro) ao topo (laranja) —
# usado no Mapa Estratégico para reforçar visualmente "da fundação ao resultado"
LAYER_COLORS = {1: "#0D1B2A", 2: "#3D4F63", 3: "#B85C2E", 4: "#EC671C"}

STEPS = [
    {"label": "Diagnóstico", "icon": "📊", "sub": "SWOT consolidada"},
    {"label": "Cruzamentos", "icon": "🧩", "sub": "Cascata TOWS"},
    {"label": "Direcionadores", "icon": "🧭", "sub": "Estratégias TOWS"},
    {"label": "Objetivos", "icon": "🎯", "sub": "Perspectivas BSC"},
    {"label": "Mapa", "icon": "🗺️", "sub": "Causa e efeito"},
    {"label": "Ações", "icon": "📋", "sub": "Plano de execução"},
    {"label": "Indicadores", "icon": "📈", "sub": "KPIs"},
    {"label": "Metodologia", "icon": "ℹ️", "sub": "Fontes e critérios"},
]

# ══════════════════════════════════════════════════════════════════
# ESTILO GLOBAL
# ══════════════════════════════════════════════════════════════════
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {{
        font-family: 'Roboto Condensed', sans-serif;
    }}
    .stApp {{
        background-color: {LIGHT_GRAY};
    }}
    h1, h2, h3, .brand-title, .layer-title {{
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 1px;
    }}

    /* ---------- HEADER ---------- */
    .brand-title {{
        font-size: 42px;
        color: {DARK_BLUE};
        text-transform: uppercase;
        margin-bottom: 0px;
        line-height: 1;
    }}
    .brand-sub {{
        font-family: 'Roboto Condensed', sans-serif;
        font-size: 15px;
        color: #64748B;
        margin-top: 4px;
        margin-bottom: 22px;
        font-weight: 300;
    }}

    /* ---------- STEPPER ---------- */
    .stepper-wrap {{ margin-bottom: 6px; }}
    .stepper-track {{
        position: relative;
        height: 4px;
        background: #E2E4E9;
        border-radius: 4px;
        margin: 0 24px 18px 24px;
    }}
    .stepper-fill {{
        position: absolute; top: 0; left: 0; height: 4px;
        background: linear-gradient(90deg, {DARK_BLUE}, {ORANGE});
        border-radius: 4px;
        transition: width 0.4s ease;
    }}
    .step-node {{
        text-align: center;
        font-family: 'Roboto Condensed', sans-serif;
    }}
    .step-circle {{
        width: 40px; height: 40px; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 6px auto;
        font-size: 17px;
        border: 2px solid #D8DBE2;
        background: {WHITE};
        color: #94A0B3;
    }}
    .step-circle.done {{
        background: {DARK_BLUE}; border-color: {DARK_BLUE}; color: {WHITE};
    }}
    .step-circle.current {{
        background: {ORANGE}; border-color: {ORANGE}; color: {WHITE};
        box-shadow: 0 0 0 5px rgba(236,103,28,0.18);
    }}
    .step-label {{
        font-size: 12.5px; font-weight: 700; color: {DARK_BLUE};
        text-transform: uppercase;
    }}
    .step-sub {{
        font-size: 10.5px; color: #8A93A3;
    }}

    /* ---------- CARDS ---------- */
    .card-box {{
        background-color: {WHITE};
        padding: 18px 20px;
        border-radius: 10px;
        border-left: 6px solid {DARK_BLUE};
        box-shadow: 0 2px 10px rgba(13,27,42,0.06);
        margin-bottom: 14px;
    }}
    .card-box.accent {{ border-left-color: {ORANGE}; }}
    .note-card {{
        background-color: #FFF4EC; border: 1px solid {ORANGE};
        padding: 14px 16px; border-radius: 10px; margin-bottom: 15px;
        font-size: 14px; color: #7A3B12;
    }}
    .source-card {{
        background-color: #EEF2F6; border: 1px solid {DARK_BLUE};
        padding: 16px 18px; border-radius: 10px; margin-bottom: 15px;
        font-size: 14px; color: {DARK_BLUE};
    }}
    .metric-badge {{
        background-color: {DARK_BLUE}; color: {WHITE}; padding: 4px 12px;
        border-radius: 20px; font-weight: 700; font-size: 11px;
        text-transform: uppercase; letter-spacing: 0.5px;
    }}
    .metric-badge.orange {{ background-color: {ORANGE}; }}

    /* ---------- MAP LAYERS ---------- */
    .layer-header {{
        font-family: 'Bebas Neue', sans-serif;
        font-size: 15px; letter-spacing: 1.5px;
        color: {DARK_BLUE}; margin: 4px 0 8px 0;
    }}
    .node-card {{
        color: {WHITE}; padding: 14px 12px; border-radius: 10px;
        text-align: center; font-family: 'Roboto Condensed', sans-serif;
        box-shadow: 0 3px 8px rgba(0,0,0,0.15);
        min-height: 78px; display: flex; flex-direction: column; justify-content: center;
    }}
    .node-num {{ font-family: 'Bebas Neue', sans-serif; font-size: 20px; letter-spacing: 1px; }}
    .node-persp {{ font-size: 12px; opacity: 0.9; }}
    .flow-arrow {{ text-align:center; font-size: 22px; color: {ORANGE}; margin: 2px 0 10px 0; }}

    /* ---------- KPI CARDS (tab 6) ---------- */
    .kpi-icon-card {{
        background: {WHITE}; border-radius: 12px; padding: 16px;
        box-shadow: 0 3px 12px rgba(13,27,42,0.08); margin-bottom: 14px;
        border-top: 4px solid {ORANGE};
    }}
    .kpi-icon {{ font-size: 26px; }}
    .kpi-title {{ font-family: 'Bebas Neue', sans-serif; font-size: 17px; color: {DARK_BLUE}; letter-spacing: 0.5px; }}
    .kpi-meta {{ font-size: 12.5px; color: #64748B; }}

    /* ---------- NAV BUTTONS ---------- */
    div.stButton > button {{
        border-radius: 8px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# DADOS (idênticos à versão anterior — reaproveitados)
# ══════════════════════════════════════════════════════════════════
swot_data = pd.DataFrame([
    {"Dimensão": "Força", "Conceito": "Equipe técnica qualificada", "Frequência": 13, "Detalhe": "Equipe multidisciplinar qualificada em gestão de processos."},
    {"Dimensão": "Força", "Conceito": "Organização e padronização dos processos", "Frequência": 9, "Detalhe": "Condução bem definida na implantação da gestão por processos."},
    {"Dimensão": "Força", "Conceito": "Metodologia padronizada", "Frequência": 8, "Detalhe": "Metodologia própria garante consistência e alinhamento estratégico."},
    {"Dimensão": "Força", "Conceito": "Padronização (geral)", "Frequência": 6, "Detalhe": "Padronização como diferencial de atuação do escritório."},
    {"Dimensão": "Força", "Conceito": "Identidade institucional EPROC", "Frequência": 4, "Detalhe": "Equipe com conhecimento técnico consolidado em mapeamento e melhoria contínua."},
    {"Dimensão": "Força", "Conceito": "Capacidade técnica", "Frequência": 3, "Detalhe": "Produção de materiais técnicos e treinamentos robustos."},
    {"Dimensão": "Força", "Conceito": "Conhecimento e organização da equipe", "Frequência": 3, "Detalhe": "Profissionais competentes e eventos com boa organização."},
    {"Dimensão": "Força", "Conceito": "Capacidades e expertises diversas", "Frequência": 3, "Detalhe": "Capacitação contínua dos especialistas."},
    {"Dimensão": "Força", "Conceito": "Patrocínio da alta gestão", "Frequência": 2, "Detalhe": "Posicionamento institucional forte e legítimo."},
    {"Dimensão": "Força", "Conceito": "Padrão único entre secretarias", "Frequência": 1, "Detalhe": "Capacidade de criar um guia de processos único para o Estado."},
    {"Dimensão": "Fraqueza", "Conceito": "Oscilação na aplicação de diretrizes", "Frequência": 15, "Detalhe": "Ausência de modelos consolidados; iniciativa pioneira no Estado exige validação contínua."},
    {"Dimensão": "Fraqueza", "Conceito": "Limitação de recursos", "Frequência": 6, "Detalhe": "Déficit de pessoal e sobrecarga de demandas."},
    {"Dimensão": "Fraqueza", "Conceito": "Dependência de outros órgãos", "Frequência": 6, "Detalhe": "Baixo nível de maturidade em gestão de processos nos órgãos atendidos."},
    {"Dimensão": "Fraqueza", "Conceito": "Baixa força política institucional", "Frequência": 5, "Detalhe": "Baixo nível de padronização e formalização institucional."},
    {"Dimensão": "Fraqueza", "Conceito": "Quantidade de servidores efetivos", "Frequência": 4, "Detalhe": "Alta rotatividade de servidores terceirizados/bolsistas."},
    {"Dimensão": "Fraqueza", "Conceito": "Rotatividade", "Frequência": 3, "Detalhe": "Alta dependência de bolsistas gera rotatividade estrutural."},
    {"Dimensão": "Fraqueza", "Conceito": "Dificuldade de engajamento das secretarias", "Frequência": 3, "Detalhe": "Barreiras de comunicação sobre o valor gerado pelo EPROC."},
    {"Dimensão": "Fraqueza", "Conceito": "Informações espalhadas", "Frequência": 3, "Detalhe": "Proposta de valor pouco traduzida para o público externo."},
    {"Dimensão": "Fraqueza", "Conceito": "Baixo nível de automação", "Frequência": 3, "Detalhe": "Ausência de sistema próprio para automatizar processos mapeados."},
    {"Dimensão": "Fraqueza", "Conceito": "Baixa visibilidade externa", "Frequência": 2, "Detalhe": "Pouca comunicação institucional para fora do EPROC."},
    {"Dimensão": "Oportunidade", "Conceito": "Transformação digital", "Frequência": 15, "Detalhe": "RPA, IA e análise de dados criam espaço para o EPROC liderar a modernização digital do governo."},
    {"Dimensão": "Oportunidade", "Conceito": "Demanda por modernização da gestão pública", "Frequência": 7, "Detalhe": "Crescente exigência de eficiência e transparência, com apoio potencial da alta gestão."},
    {"Dimensão": "Oportunidade", "Conceito": "Cultura de gestão por processos", "Frequência": 6, "Detalhe": "Parcerias e programas de fomento fortalecem a disseminação da cultura de processos."},
    {"Dimensão": "Oportunidade", "Conceito": "Parcerias institucionais", "Frequência": 5, "Detalhe": "Parcerias com universidades e órgãos ampliam acesso a recursos."},
    {"Dimensão": "Oportunidade", "Conceito": "Fortalecimento da rede NUPROC", "Frequência": 5, "Detalhe": "Ampliação da capilaridade via núcleos já institucionalizados nos órgãos."},
    {"Dimensão": "Oportunidade", "Conceito": "Eventos e capacitações", "Frequência": 3, "Detalhe": "Capilaridade ampliada por eventos de capacitação."},
    {"Dimensão": "Oportunidade", "Conceito": "Alinhamento a planos de governo", "Frequência": 3, "Detalhe": "Avanço de metodologias de planejamento fortalece a atuação da SEPLAN junto aos órgãos."},
    {"Dimensão": "Oportunidade", "Conceito": "Possibilidade de concurso público", "Frequência": 2, "Detalhe": "Oportunidade de concurso para fortalecer o corpo funcional."},
    {"Dimensão": "Oportunidade", "Conceito": "Aquisição de sistema de gestão de processos", "Frequência": 2, "Detalhe": "Grande volume de processos mapeados em BPMN abre caminho para automação futura."},
    {"Dimensão": "Oportunidade", "Conceito": "Ampliação do quadro de pessoal", "Frequência": 2, "Detalhe": "Intranet e padronização como instrumentos de cultura institucional."},
    {"Dimensão": "Ameaça", "Conceito": "Mudanças políticas e institucionais", "Frequência": 28, "Detalhe": "Item de maior recorrência em toda a coleta — instabilidade política pode afetar continuidade de projetos."},
    {"Dimensão": "Ameaça", "Conceito": "Troca de governo", "Frequência": 4, "Detalhe": "Falta de apoio e corte orçamentário associados à troca de gestão."},
    {"Dimensão": "Ameaça", "Conceito": "Concorrência de consultorias externas", "Frequência": 4, "Detalhe": "Baixo engajamento dos órgãos e baixo conhecimento sobre a importância da gestão de processos."},
    {"Dimensão": "Ameaça", "Conceito": "Resistência cultural à mudança", "Frequência": 3, "Detalhe": "Risco de manutenção de práticas antigas e ineficientes."},
    {"Dimensão": "Ameaça", "Conceito": "Extinção ou reestruturação da Secretaria", "Frequência": 2, "Detalhe": "Perda de conhecimento com a saída de servidores e colaboradores."},
    {"Dimensão": "Ameaça", "Conceito": "Baixo reconhecimento institucional", "Frequência": 2, "Detalhe": "Falta de blindagem do EPROC diante de mudanças de gestão."},
    {"Dimensão": "Ameaça", "Conceito": "Falta de interesse dos órgãos", "Frequência": 2, "Detalhe": "Baixa participação dos órgãos dificulta a atuação do EPROC."},
    {"Dimensão": "Ameaça", "Conceito": "Rotatividade de bolsistas", "Frequência": 2, "Detalhe": "Cargos com alta rotatividade comprometem continuidade técnica."},
    {"Dimensão": "Ameaça", "Conceito": "Instabilidade de infraestrutura tecnológica", "Frequência": 2, "Detalhe": "Indisponibilidade de sistemas pode paralisar o atendimento."},
    {"Dimensão": "Ameaça", "Conceito": "Baixa adesão às orientações do EPROC", "Frequência": 2, "Detalhe": "Dificuldade de priorização das demandas formalizadas via EPROC."},
])

tows_data = pd.DataFrame([
    {
        "Tipo": "SO",
        "Estratégia": "Crescimento",
        "Origem": "FORÇAS\nMetodologia padronizada (8)\nCapacidade técnica (3)",
        "Cruzado com": "OPORTUNIDADES\nTransformação digital (15)",
        "Direcionador": "Crescimento",
        "Texto_direcionador": "Posicionar o EPROC como referência técnica nas iniciativas de modernização e transformação digital do Estado, ampliando sua atuação além do mapeamento tradicional de processos.",
        "Objetivo gerado": "Processos Internos + Tecnologia e Inovação",
    },
    {
        "Tipo": "WO",
        "Estratégia": "Desenvolvimento",
        "Origem": "FRAQUEZAS\nQtd. servidores efetivos (4)\nRotatividade (3)\nDependência de outros órgãos (6)",
        "Cruzado com": "OPORTUNIDADES\nFortalecimento da rede NUPROC (5)\nParcerias institucionais (5)",
        "Direcionador": "Desenvolvimento",
        "Texto_direcionador": "Fortalecer a estrutura interna do EPROC aproveitando as oportunidades disponíveis no curto prazo, reduzindo vulnerabilidades operacionais sem depender de soluções externas de prazo incerto.",
        "Objetivo gerado": "Pessoas",
    },
    {
        "Tipo": "ST",
        "Estratégia": "Defesa",
        "Origem": "FORÇAS\nPatrocínio da alta gestão (2)\nMetodologia (8)",
        "Cruzado com": "AMEAÇAS\nTroca de governo (4)\nConcorrência de consultorias externas (4)",
        "Direcionador": "Defesa",
        "Texto_direcionador": "Converter as forças institucionais em mecanismos de proteção contra descontinuidade administrativa, demonstrando objetivamente o valor gerado pelo EPROC para o Poder Executivo estadual.",

        "Objetivo gerado": "Resultados",
    },
    {
        "Tipo": "WT",
        "Estratégia": "Sobrevivência",
        "Origem": "FRAQUEZAS\nBaixa força política (5)\nBaixo nível de automação (3)",
        "Cruzado com": "AMEAÇAS\nMudanças políticas (28)\nInfraestrutura (2)",
        "Direcionador": "Sobrevivência",
        "Texto_direcionador": "Reduzir as vulnerabilidades internas que mais expõem o EPROC às ameaças externas de maior impacto, priorizando formalização institucional e comprovação de resultados como escudos contra descontinuidade.",
        "Objetivo gerado": "Governança",
    },
])

# Direcionadores Estratégicos — intenção ampla de cada postura.
# São a bússola que orienta a formulação dos objetivos, não o objetivo em si.
DIRECIONADORES = [
    {
        "Tipo": "SO", "Nome": "Estratégia de Crescimento",
        "Subtitulo": "Expansão e Posicionamento Institucional",
        "Texto": (
            "Posicionar o EPROC como referência técnica nas iniciativas de modernização "
            "e transformação digital do Estado, ampliando sua atuação além do mapeamento "
            "tradicional de processos e consolidando presença estratégica nos projetos "
            "prioritários do governo."
        ),
    },
    {
        "Tipo": "WO", "Nome": "Estratégia de Desenvolvimento",
        "Subtitulo": "Modernização Estrutural e Fortalecimento Interno",
        "Texto": (
            "Fortalecer a estrutura interna do EPROC aproveitando as oportunidades "
            "disponíveis no curto prazo, com foco na redução das vulnerabilidades "
            "operacionais geradas pela rotatividade e pela limitação de recursos humanos."
        ),
    },
    {
        "Tipo": "ST", "Nome": "Estratégia de Defesa",
        "Subtitulo": "Proteção Institucional e Resiliência",
        "Texto": (
            "Converter as forças institucionais do EPROC em mecanismos de proteção "
            "contra ameaças externas, especialmente a descontinuidade administrativa "
            "e a concorrência de soluções externas, demonstrando de forma objetiva "
            "o valor gerado pelo escritório para o Poder Executivo estadual."
        ),
    },
    {
        "Tipo": "WT", "Nome": "Estratégia de Sobrevivência",
        "Subtitulo": "Governança, Controle e Mitigação de Riscos",
        "Texto": (
            "Reduzir as vulnerabilidades internas do EPROC que mais o expõem às ameaças "
            "externas de maior impacto, priorizando a formalização institucional e a "
            "comprovação de resultados como escudos contra descontinuidade, "
            "instabilidade política e perda de relevância."
        ),
    },
]

# Objetivos alinhados à planilha da Equipe 4 e às 5 perspectivas do BSC para gestão pública:
# Resultados | Processos Internos | Pessoas | Tecnologia e Inovação | Governança
objetivos_data = pd.DataFrame([
    {
        "Nº": 1,
        "Perspectiva": "Resultados",
        "Objetivo": "Comprovar a redução de tempo e/ou etapas em pelo menos 15 processos finalísticos com impacto direto ao cidadão, demonstrando o retorno institucional da atuação do EPROC.",
        "Direcionador": "Defesa",
    },
    {
        "Nº": 2,
        "Perspectiva": "Processos Internos",
        "Objetivo": "Atuar em 100% das iniciativas de automação priorizadas pelo Estado que demandem mapeamento ou análise de processos, com requisitos de negócio formalizados e entregáveis definidos.",
        "Direcionador": "Crescimento",
    },
    {
        "Nº": 3,
        "Perspectiva": "Pessoas",
        "Objetivo": "Ampliar em X% a capacidade de atendimento do EPROC sem aumento proporcional de equipe, por meio de padronização de métodos, automação de rotinas administrativas e fortalecimento da rede NUPROC.",
        "Direcionador": "Desenvolvimento",
    },
    {
        "Nº": 4,
        "Perspectiva": "Tecnologia e Inovação",
        "Objetivo": "Atualizar a metodologia EPROC anualmente, incorporando pelo menos 2 novas práticas ou ferramentas de gestão de processos a cada ciclo de atualização.",
        "Direcionador": "Crescimento",
    },
    {
        "Nº": 5,
        "Perspectiva": "Governança",
        "Objetivo": "Institucionalizar, por meio de normativo formal, a participação do EPROC em 100% das iniciativas de criação, reestruturação ou extinção de secretarias, diretorias e empresas públicas que envolvam revisão de processos.",
        "Direcionador": "Sobrevivência",
    },
])

INDICADORES = {
    1: [
        ("Processos finalísticos com redução comprovada", "Nº de processos com TO-BE implementado e delta medido", "≥ 15 até 2027", "Anual", "⚡"),
        ("Redução média de tempo/etapas (AS-IS × TO-BE)", "(Etapas AS-IS − TO-BE) / AS-IS × 100", "Meta a definir após baseline", "Anual", "📉"),
    ],
    2: [
        ("Cobertura nas iniciativas de automação do Estado", "Iniciativas com EPROC / total priorizadas", "100%", "Semestral", "⚙️"),
        ("Aderência ao checklist de requisitos de negócio", "% de entregas com requisitos formalizados", "100%", "Contínua", "✅"),
    ],
    3: [
        ("Capacidade de atendimento por colaborador", "Demandas atendidas / nº de colaboradores ativos", "Ampliar X% vs. baseline", "Semestral", "📈"),
        ("Processos padronizados em playbook", "Fluxos documentados / total de fluxos críticos do EPROC", "100% dos fluxos críticos", "Anual", "📋"),
        ("NUPROCs com execução autônoma de mapeamentos", "NUPROCs autônomos / total de NUPROCs ativos", "Meta a definir", "Semestral", "🌐"),
    ],
    4: [
        ("Novas práticas incorporadas por ciclo", "Práticas documentadas / ciclo de atualização", "≥ 2 por ano", "Anual", "🔎"),
        ("Versão da metodologia publicada", "Nº de revisões formais realizadas", "1 por ano", "Anual", "📘"),
    ],
    5: [
        ("Normativo formal publicado", "Existência de decreto/instrução normativa vigente", "Publicado até 2027", "Marco único", "📜"),
        ("Iniciativas acompanhadas pelo EPROC após normativo", "Iniciativas com EPROC / total pós-publicação", "100%", "Semestral", "🏛️"),
    ],
}

ACOES = {
    1: [
        ("Estabelecer linha de base (AS-IS) de tempo e etapas dos processos prioritários", "Equipe EPROC", "T1"),
        ("Mensurar redução (TO-BE) a cada processo remapeado", "Equipe EPROC", "Contínuo"),
        ("Consolidar e apresentar relatório anual de impacto à alta gestão", "Gerência EPROC", "Anual"),
    ],
    2: [
        ("Mapear iniciativas de automação priorizadas no plano de governo", "Equipe EPROC", "T1"),
        ("Formalizar protocolo de atuação como consultoria de negócio pré-automação", "Coordenação EPROC", "T1"),
        ("Criar checklist padrão de levantamento de requisitos de negócio", "Equipe EPROC", "T1-T2"),
    ],
    3: [
        ("Mapear e padronizar os principais fluxos de trabalho do EPROC em playbooks reutilizáveis", "Equipe EPROC", "T1-T2"),
        ("Identificar e automatizar rotinas administrativas repetitivas (agendamentos, registros, relatórios)", "Equipe EPROC", "T2"),
        ("Ampliar a rede NUPROC com novos pontos focais capacitados para execução autônoma de mapeamentos", "Coordenação EPROC", "Contínuo"),
    ],
    4: [
        ("Realizar benchmarking com metodologias de BPM (setor público e privado)", "Equipe EPROC", "Semestral"),
        ("Revisar e publicar nova versão da metodologia EPROC/SEPLAN", "Coordenação EPROC", "Anual"),
        ("Criar repositório interno de boas práticas por tipo de processo mapeado", "Equipe EPROC", "Contínuo"),
    ],
    5: [
        ("Redigir minuta de normativo/decreto de participação obrigatória do EPROC", "Coordenação EPROC", "T1-T2"),
        ("Articular validação jurídica e política junto à SEPLAN e Casa Civil", "Coordenação + Gerência", "T2"),
        ("Elaborar playbook de atuação em processos de criação/reestruturação de órgãos", "Equipe EPROC", "T2-T3"),
    ],
}

CAUSAL_LINKS = [
    ("3", "2", "Bolsistas qualificados sustentam a capacidade de atuar em 100% das automações."),
    ("3", "4", "Equipe capacitada viabiliza a atualização metodológica contínua."),
    ("4", "2", "Metodologia atualizada é o instrumento da consultoria de negócio."),
    ("5", "2", "Mandato formal garante que o EPROC seja acionado nas iniciativas de automação."),
    ("2", "1", "Consultoria bem executada gera desburocratização mensurável."),
    ("5", "1", "Institucionalização formal protege a continuidade e legitima os resultados."),
]

PERSPECTIVA_LAYER = {
    "Pessoas": 1,
    "Tecnologia e Inovação": 2,
    "Governança": 2,
    "Processos Internos": 3,
    "Resultados": 4,
}

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="brand-title">Escritório de Gestão e Desburocratização de Processos</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">EPROC / SEPLAN · Plano Estratégico 2026 — Metodologia BSC + SWOT · Consolidado das Etapas 1 a 4</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# STEPPER — navegação sequencial
# ══════════════════════════════════════════════════════════════════
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0

n_steps = len(STEPS)
fill_pct = (st.session_state.step_idx / (n_steps - 1)) * 100

st.markdown(f"""
<div class="stepper-wrap">
    <div class="stepper-track"><div class="stepper-fill" style="width:{fill_pct}%;"></div></div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(n_steps)
for i, (col, step_info) in enumerate(zip(cols, STEPS)):
    with col:
        state = "current" if i == st.session_state.step_idx else ("done" if i < st.session_state.step_idx else "")
        icon = step_info["icon"]
        sub_label = step_info["sub"]
        st.markdown(f"""
        <div class="step-node">
            <div class="step-circle {state}">{icon}</div>
            <div class="step-label">{step_info['label']}</div>
            <div class="step-sub">{sub_label}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(" ", key=f"nav_{i}", use_container_width=True):
            st.session_state.step_idx = i

st.write("")
step = st.session_state.step_idx

# ══════════════════════════════════════════════════════════════════
# STEP 0 — DIAGNÓSTICO SWOT
# ══════════════════════════════════════════════════════════════════
if step == 0:
    st.subheader("📊 Diagnóstico Consolidado (Análise dos Ambientes)")
    st.caption("Consolidação semântica de ~600 respostas brutas de 57 respondentes, reduzidas a 60 conceitos (40 exibidos abaixo, os mais representativos por quadrante).")

    dim_filter = st.multiselect("Filtrar por dimensão", options=swot_data["Dimensão"].unique().tolist(),
                                 default=swot_data["Dimensão"].unique().tolist())
    filtered = swot_data[swot_data["Dimensão"].isin(dim_filter)]

    colors = {"Força": DARK_BLUE, "Fraqueza": "#3D4F63", "Oportunidade": ORANGE, "Ameaça": "#B85C2E"}
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        for dim in ["Força", "Fraqueza"]:
            if dim in dim_filter:
                d = filtered[filtered["Dimensão"] == dim].sort_values("Frequência", ascending=True)
                fig = px.bar(d, x="Frequência", y="Conceito", orientation="h",
                             title=f"{'💪' if dim=='Força' else '⚠️'} {dim}s", color_discrete_sequence=[colors[dim]])
                fig.update_layout(height=320, margin=dict(l=0, r=10, t=35, b=0),
                                   font_family="Roboto Condensed", plot_bgcolor=WHITE, paper_bgcolor=WHITE)
                st.plotly_chart(fig, use_container_width=True)
    with col_chart2:
        for dim in ["Oportunidade", "Ameaça"]:
            if dim in dim_filter:
                d = filtered[filtered["Dimensão"] == dim].sort_values("Frequência", ascending=True)
                fig = px.bar(d, x="Frequência", y="Conceito", orientation="h",
                             title=f"{'🚀' if dim=='Oportunidade' else '🔴'} {dim}s", color_discrete_sequence=[colors[dim]])
                fig.update_layout(height=320, margin=dict(l=0, r=10, t=35, b=0),
                                   font_family="Roboto Condensed", plot_bgcolor=WHITE, paper_bgcolor=WHITE)
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="note-card">
    ⚠️ <b>Nota metodológica sobre o volume de menções:</b> a frequência de cada conceito reflete recorrência
    percebida, mas <b>não</b> foi usada como critério único de priorização — foi combinada com julgamento
    qualitativo da equipe (detalhes na etapa "Metodologia").
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Explorar todos os conceitos e detalhes"):
        st.dataframe(filtered[["Dimensão", "Conceito", "Frequência", "Detalhe"]], use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════
# STEP 1 — CRUZAMENTOS TOWS (cascata de decisão — estático)
# ══════════════════════════════════════════════════════════════════
elif step == 1:
    st.subheader("🧩 Cascata de Decisão TOWS")
    st.caption("Cada cruzamento combina um fator interno (Força ou Fraqueza) com um fator externo (Oportunidade ou Ameaça), gerando um direcionador estratégico que orienta os objetivos.")

    TIPO_CONFIG = {
        "SO": {"label": "🟢 Crescimento",   "cor": "#2E8B3A", "combo": "Forças × Oportunidades",  "pergunta": "Como usar uma força para aproveitar uma oportunidade?"},
        "WO": {"label": "🔵 Desenvolvimento","cor": "#2980B9", "combo": "Fraquezas × Oportunidades","pergunta": "Como aproveitar uma oportunidade para reduzir uma fraqueza?"},
        "ST": {"label": "🟠 Defesa",         "cor": "#EC671C", "combo": "Forças × Ameaças",         "pergunta": "Como usar uma força para se proteger de uma ameaça?"},
        "WT": {"label": "🔴 Sobrevivência",  "cor": "#B85C2E", "combo": "Fraquezas × Ameaças",      "pergunta": "Como reduzir uma fraqueza para não ficar exposto a uma ameaça?"},
    }

    for _, row in tows_data.iterrows():
        cfg = TIPO_CONFIG.get(row["Tipo"], {})
        cor = cfg.get("cor", DARK_BLUE)
        label = cfg.get("label", row["Tipo"])
        combo = cfg.get("combo", "")
        pergunta = cfg.get("pergunta", "")

        st.markdown(f"""
        <div style="background:{WHITE}; border-radius:12px; border-left:6px solid {cor};
                    box-shadow:0 2px 10px rgba(13,27,42,0.07); padding:18px 22px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="background:{cor}; color:#fff; padding:4px 14px; border-radius:20px;
                             font-weight:700; font-size:12px; text-transform:uppercase;">{label}</span>
                <span style="color:#8A93A3; font-size:12px;">{combo}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:12px;">
                <div style="background:#EEF2F6; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">Fator Interno</div>
                    <div style="font-size:12.5px; color:{DARK_BLUE}; white-space:pre-line;">{row["Origem"]}</div>
                </div>
                <div style="background:#FFF4EC; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">Fator Externo</div>
                    <div style="font-size:12.5px; color:{DARK_BLUE}; white-space:pre-line;">{row["Cruzado com"]}</div>
                </div>
            </div>
            <div style="background:#F4F5F7; border-radius:8px; padding:10px 14px; margin-bottom:8px;">
                <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">↓ Direcionador Estratégico</div>
                <div style="font-size:13px; color:{DARK_BLUE}; font-style:italic;">{row["Texto_direcionador"]}</div>
            </div>
            <div style="font-size:11.5px; color:#64748B;">
                <b>Origina:</b> perspectiva <b>{row["Objetivo gerado"]}</b>
                &nbsp;·&nbsp; <i>{pergunta}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STEP 2 — DIRECIONADORES ESTRATÉGICOS
# ══════════════════════════════════════════════════════════════════
elif step == 2:
    st.subheader("🧭 Direcionadores Estratégicos")
    st.caption("Intenção estratégica de cada postura TOWS — bússola que orienta a formulação dos objetivos, não o objetivo em si.")

    DIRECIONADOR_COLOR = {"SO": "#0D1B2A", "WO": "#2980B9", "ST": "#EC671C", "WT": "#B85C2E"}
    TIPO_NOME = {"SO": "Crescimento", "WO": "Desenvolvimento", "ST": "Defesa", "WT": "Sobrevivência"}
    dir_cols = st.columns(4)
    for col, d in zip(dir_cols, DIRECIONADORES):
        with col:
            cor = DIRECIONADOR_COLOR[d["Tipo"]]
            st.markdown(f"""
            <div class="card-box" style="border-left-color:{cor}; min-height:260px;">
                <span class="metric-badge" style="background-color:{cor};">{d["Tipo"]}</span>
                <h5 style="margin:8px 0 2px 0; color:{cor};">{d["Nome"]}</h5>
                <small style="color:#8A93A3;">{d["Subtitulo"]}</small>
                <p style="font-size:12.5px; color:#334155; margin-top:10px;">{d["Texto"]}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 📋 Cascata de Decisão — Cruzamentos que originaram cada direcionador")
    TIPO_CONFIG = {
        "SO": {"label": "🟢 SO — Crescimento",    "cor": "#2E8B3A"},
        "WO": {"label": "🔵 WO — Desenvolvimento", "cor": "#2980B9"},
        "ST": {"label": "🟠 ST — Defesa",          "cor": "#EC671C"},
        "WT": {"label": "🔴 WT — Sobrevivência",   "cor": "#B85C2E"},
    }
    for _, row in tows_data.iterrows():
        cfg = TIPO_CONFIG.get(row["Tipo"], {"label": row["Tipo"], "cor": "#0D1B2A"})
        cor = cfg["cor"]
        st.markdown(f"""
        <div style="background:#FFFFFF; border-radius:12px; border-left:6px solid {cor};
                    box-shadow:0 2px 8px rgba(13,27,42,0.07); padding:16px 20px; margin-bottom:14px;">
            <div style="margin-bottom:10px;">
                <span style="background:{cor}; color:#fff; padding:3px 12px; border-radius:20px;
                             font-weight:700; font-size:11px;">{cfg["label"]}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                <div style="background:#EEF2F6; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:10px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">Fator Interno</div>
                    <div style="font-size:12px; color:#0D1B2A; white-space:pre-line;">{row["Origem"]}</div>
                </div>
                <div style="background:#FFF4EC; border-radius:8px; padding:10px 14px;">
                    <div style="font-size:10px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">Fator Externo</div>
                    <div style="font-size:12px; color:#0D1B2A; white-space:pre-line;">{row["Cruzado com"]}</div>
                </div>
            </div>
            <div style="background:#F4F5F7; border-radius:8px; padding:10px 14px;">
                <div style="font-size:10px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:4px;">↓ Direcionador</div>
                <div style="font-size:12.5px; color:#0D1B2A; font-style:italic;">{row["Texto_direcionador"]}</div>
            </div>
            <div style="font-size:11px; color:#64748B; margin-top:8px;">
                <b>Perspectiva gerada:</b> {row["Objetivo gerado"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STEP 3 — OBJETIVOS ESTRATÉGICOS
# ══════════════════════════════════════════════════════════════════
elif step == 3:
    st.subheader("🎯 Objetivos Estratégicos — Perspectivas BSC")
    st.markdown("""
    <div class="source-card">
    💡 <b>Alinhamento de escopo institucional:</b> o EPROC posiciona-se como <b>consultoria interna de negócios
    e desburocratização</b>. O escritório mapeia, simplifica e entrega requisitos prontos para as equipes técnicas responsáveis pela implementação.
    </div>
    """, unsafe_allow_html=True)

    dir_filter = st.multiselect(
        "Filtrar por direcionador estratégico",
        options=objetivos_data["Direcionador"].unique().tolist(),
        default=objetivos_data["Direcionador"].unique().tolist()
    )
    obj_filtered = objetivos_data[objetivos_data["Direcionador"].isin(dir_filter)]

    for _, row in obj_filtered.iterrows():
        st.markdown(f"""
        <div class="card-box">
            <span class="metric-badge">{row['Perspectiva']}</span>
            <span class="metric-badge orange" style="margin-left:6px;">{row['Direcionador']}</span>
            <h4 style="margin-top:8px; margin-bottom:5px; color:#0D1B2A; font-family:'Bebas Neue'; letter-spacing:0.5px;">OBJETIVO {row['Nº']}</h4>
            <p style="color:#334155;">{row['Objetivo']}</p>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STEP 4 — MAPA ESTRATÉGICO
# ══════════════════════════════════════════════════════════════════
elif step == 4:
    st.subheader("🗺️ Mapa Estratégico")
    st.markdown("""
    <div class="source-card">
    <b>Como ler este mapa:</b> os 5 objetivos estão organizados em 4 camadas de causa e efeito — de baixo para cima.
    A cor evolui do azul escuro (fundação: Pessoas) ao laranja (resultado: Resultados).
    Cada camada sustenta a superior: <b>Pessoas → Tecnologia/Governança → Processos Internos → Resultados.</b>
    </div>
    """, unsafe_allow_html=True)

    layer_info = {
        4: ("RESULTADOS 📈", "O que a sociedade e a alta gestão enxergam"),
        3: ("PROCESSOS INTERNOS ⚙️", "O que o EPROC entrega no dia a dia"),
        2: ("TECNOLOGIA E INOVAÇÃO 💻  |  GOVERNANÇA 🏛️", "O que viabiliza a operação e institucionaliza o EPROC"),
        1: ("PESSOAS 👥", "O que sustenta tudo o resto"),
    }
    layers = {1: [], 2: [], 3: [], 4: []}
    for _, row in objetivos_data.iterrows():
        layers[PERSPECTIVA_LAYER[row["Perspectiva"]]].append(row)

    for lvl in [4, 3, 2, 1]:
        title, desc = layer_info[lvl]
        st.markdown(
            f'<div class="layer-header">{title} <span style="color:#8A93A3; font-family:\'Roboto Condensed\'; font-size:12px;">— {desc}</span></div>',
            unsafe_allow_html=True
        )
        row_cols = st.columns(max(len(layers[lvl]), 1))
        for c, row in zip(row_cols, layers[lvl]):
            with c:
                st.markdown(f"""<div class="node-card" style="background-color:{LAYER_COLORS[lvl]};">
                    <div class="node-num">OBJ. {row['Nº']}</div>
                    <div class="node-persp">{row['Perspectiva']}</div>
                    </div>""", unsafe_allow_html=True)
        if lvl > 1:
            st.markdown('<div class="flow-arrow">⬆</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("##### 🔍 Explorar conexões de um objetivo")
    obj_lookup = objetivos_data.set_index("Nº")["Perspectiva"].to_dict()
    sel = st.selectbox(
        "Selecionar objetivo",
        options=objetivos_data["Nº"].tolist(),
        format_func=lambda n: f"Objetivo {n} — {obj_lookup[n]}"
    )
    alimenta       = [(b, r) for a, b, r in CAUSAL_LINKS if int(a) == sel]
    alimentado_por = [(a, r) for a, b, r in CAUSAL_LINKS if int(b) == sel]

    col_in, col_out = st.columns(2)
    with col_in:
        st.markdown(f"**⬅️ É alimentado por** ({len(alimentado_por)})")
        if alimentado_por:
            for a, r in alimentado_por:
                st.markdown(f"""<div class="card-box" style="padding:12px 14px;">
                    <b>Objetivo {a}</b> — {obj_lookup[int(a)]}<br>
                    <small style="color:#64748B;">{r}</small></div>""", unsafe_allow_html=True)
        else:
            st.caption("Objetivo de base — não depende de outros.")
    with col_out:
        st.markdown(f"**➡️ Alimenta** ({len(alimenta)})")
        if alimenta:
            for b, r in alimenta:
                st.markdown(f"""<div class="card-box accent" style="padding:12px 14px;">
                    <b>Objetivo {b}</b> — {obj_lookup[int(b)]}<br>
                    <small style="color:#64748B;">{r}</small></div>""", unsafe_allow_html=True)
        else:
            st.caption("Objetivo de topo — não alimenta outros.")

    st.caption("🔁 Os objetivos de base (Pessoas, Governança, Tecnologia) sustentam a operação (Processos Internos) que gera os Resultados no topo.")

# ══════════════════════════════════════════════════════════════════
# STEP 5 — PLANO DE AÇÃO
# ══════════════════════════════════════════════════════════════════
elif step == 5:
    st.subheader("📋 Plano de Ação por Objetivo")
    st.markdown("""
    <div class="note-card">
    📝 Ações em fase de validação de prazos e responsáveis reais — os prazos abaixo (T1, T2...) são
    relativos ao início do plano.
    </div>
    """, unsafe_allow_html=True)

    if "status_acoes" not in st.session_state:
        st.session_state["status_acoes"] = {}

    for _, row in objetivos_data.iterrows():
        with st.expander(f"Objetivo {row['Nº']} — {row['Perspectiva']}: {row['Objetivo'][:80]}..."):
            for i, (titulo, resp, prazo) in enumerate(ACOES[row["Nº"]]):
                key = f"acao_{row['Nº']}_{i}"
                if key not in st.session_state["status_acoes"]:
                    st.session_state["status_acoes"][key] = False
                checked = st.checkbox(f"**{titulo}**", value=st.session_state["status_acoes"][key], key=key)
                st.session_state["status_acoes"][key] = checked
                st.caption(f"👤 {resp} · 🗓️ {prazo}")

    concluidos = sum(st.session_state["status_acoes"].values())
    total = len(st.session_state["status_acoes"]) if st.session_state["status_acoes"] else 1
    st.divider()
    st.progress(concluidos / total)
    st.caption(f"**Progresso geral do plano de ação:** {concluidos} de {total} iniciativas concluídas ({int(concluidos/total*100)}%)")

# ══════════════════════════════════════════════════════════════════
# STEP 6 — INDICADORES
# ══════════════════════════════════════════════════════════════════
elif step == 6:
    st.subheader("📈 Indicadores de Desempenho por Objetivo")
    st.caption("Todos os objetivos possuem indicadores propostos. Os valores de meta e linha de base serão definidos na fase de implementação.")

    PERSP_COR = {
        "Resultados": "#EC671C",
        "Processos Internos": "#0D1B2A",
        "Pessoas": "#2980B9",
        "Tecnologia e Inovação": "#3D4F63",
        "Governança": "#B85C2E",
    }

    for _, row in objetivos_data.iterrows():
        kpis = INDICADORES[row["Nº"]]
        persp_key = row["Perspectiva"].replace(" 📈","").replace(" ⚙️","").replace(" 👥","").replace(" 💻","").replace(" 🏛️","")
        cor = PERSP_COR.get(persp_key, "#0D1B2A")

        with st.expander(f"OBJ. {row['Nº']} — {row['Perspectiva']}  ·  {row['Objetivo'][:70]}...", expanded=True):
            st.markdown(f"""
            <div style="background:#F4F5F7; border-radius:8px; padding:10px 14px; margin-bottom:12px; border-left:4px solid {cor};">
                <div style="font-size:11px; font-weight:700; color:#64748B; text-transform:uppercase;">Objetivo completo</div>
                <div style="font-size:13px; color:#0D1B2A; margin-top:4px;">{row['Objetivo']}</div>
            </div>
            """, unsafe_allow_html=True)

            kpi_cols = st.columns(len(kpis))
            for col, (nome, formula, meta, periodo, icon) in zip(kpi_cols, kpis):
                with col:
                    st.markdown(f"""
                    <div style="background:#FFFFFF; border-radius:10px; padding:14px;
                                box-shadow:0 2px 8px rgba(13,27,42,0.08); border-top:4px solid {cor}; height:100%;">
                        <div style="font-size:22px; margin-bottom:6px;">{icon}</div>
                        <div style="font-family:'Bebas Neue'; font-size:15px; color:#0D1B2A; letter-spacing:0.5px; margin-bottom:8px;">{nome}</div>
                        <div style="font-size:11px; color:#64748B; margin-bottom:4px;">📐 <b>Fórmula:</b> {formula}</div>
                        <div style="font-size:11px; color:#64748B; margin-bottom:4px;">🎯 <b>Meta:</b> {meta}</div>
                        <div style="font-size:11px; color:#64748B;">🗓️ <b>Periodicidade:</b> {periodo}</div>
                    </div>
                    """, unsafe_allow_html=True)
            st.write("")

    st.divider()
    st.markdown("##### 🌡️ Leitura visual (ilustrativa até termos linha de base real)")
    gauge_cols = st.columns(len(kpis))
    for c, (nome, formula, meta, periodo, icon) in zip(gauge_cols, kpis):
        with c:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=45,
                title={"text": nome[:28], "font": {"size": 13, "family": "Roboto Condensed"}},
                number={"suffix": "%", "font": {"color": DARK_BLUE}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"size": 9}},
                    "bar": {"color": ORANGE},
                    "bgcolor": WHITE,
                    "steps": [
                        {"range": [0, 40], "color": "#F1F1F3"},
                        {"range": [40, 75], "color": "#F4D9C6"},
                    ],
                }
            ))
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor=WHITE)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("##### ⚡ Simulador de impacto — Objetivo 4 (Desburocratização)")
    st.caption("Projeção ilustrativa a partir dos parâmetros ajustáveis abaixo — usar apenas como referência até termos dados reais de linha de base.")

    sim_col1, sim_col2 = st.columns([1, 2])
    with sim_col1:
        processos_ano = st.slider("Processos redesenhados / ano", 5, 50, 20, 5)
        reducao_dias = st.slider("Redução média no tempo de tramitação (dias)", 5, 60, 25, 5)
        horas_servidor = st.slider("Horas economizadas por processo/ano", 50, 500, 180, 10)
    with sim_col2:
        total_dias_salvos = processos_ano * reducao_dias
        total_horas_poupadas = processos_ano * horas_servidor
        equivalente_servidores = round(total_horas_poupadas / 1920, 1)

        m1, m2, m3 = st.columns(3)
        for col, icon, label, val in [
            (m1, "📅", "Dias agilizados", f"{total_dias_salvos:,}"),
            (m2, "⏱️", "Horas revertidas", f"{total_horas_poupadas:,} h"),
            (m3, "🧑‍💼", "Equivalente em FTEs", f"~{equivalente_servidores}"),
        ]:
            col.markdown(f"""
            <div class="kpi-icon-card" style="text-align:center;">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-title" style="font-size:22px;">{val}</div>
                <div class="kpi-meta">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        st.info(f"Redesenhando **{processos_ano} processos/ano**, o EPROC libera o equivalente a **{equivalente_servidores} servidores em tempo integral** para atendimento direto ao cidadão.")

# ══════════════════════════════════════════════════════════════════
# STEP 7 — METODOLOGIA & FONTES
# ══════════════════════════════════════════════════════════════════
elif step == 7:
    st.subheader("ℹ️ Metodologia e Fontes dos Dados")
    st.markdown("""
    #### Como chegamos até aqui

    **Etapa 1 — Alinhamento Inicial:** definição do Plano de Projeto (prazo de 1 mês), equipe responsável e
    as 8 perspectivas do Mapa Estratégico, seguindo a metodologia EPROC/SEPLAN versão 01/2026.

    **Etapa 2 — Análise dos Ambientes (SWOT):** coleta via formulário Google, com **57 respondentes** de
    múltiplos órgãos do Executivo de SC, gerando ~600 respostas brutas. Consolidação por agrupamento
    semântico com `paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers), limiar de similaridade
    **0.72**, resultando em 60 conceitos.

    **Etapa 3 — Formulação Estratégica:** cruzamentos TOWS priorizados combinando recorrência quantitativa
    com validação qualitativa da equipe — volume de menções não foi critério único. 7 objetivos redigidos
    em formato BSC.

    **Etapa 4 — Desdobramento:** Mapa Estratégico, Plano de Ação e Indicadores por objetivo.
    """)
    st.markdown("""
    <div class="note-card">
    ⚠️ <b>Nota de transparência sobre viés de amostragem:</b> o volume de respondentes por órgão não é
    proporcional, e a clusterização semântica envolve decisões técnicas que podem agrupar conceitos de
    forma diferente conforme o parâmetro. A frequência deve ser lida como <b>sinal de atenção</b>, não
    como <b>determinação automática</b> de prioridade.
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class="source-card">
    ✅ <b>Missão, Visão e Valores</b> (referência de alinhamento):<br><br>
    <b>Missão:</b> Conectar pessoas e tecnologias, por meio da Gestão por Processos de Negócio, proporcionando
    a melhoria dos serviços prestados à sociedade catarinense.<br>
    <b>Visão:</b> Consolidar a cultura de Gestão por Processos, com foco na experiência do usuário.<br>
    <b>Valores:</b> Colaboração, Visão Sistêmica, Melhoria Contínua, Inovação, Empatia, Resiliência,
    Otimismo e Pioneirismo.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# NAVEGAÇÃO PREV/NEXT
# ══════════════════════════════════════════════════════════════════
st.write("")
st.divider()
nav_prev, nav_mid, nav_next = st.columns([1, 3, 1])
with nav_prev:
    if step > 0:
        if st.button("← Anterior", use_container_width=True):
            st.session_state.step_idx = step - 1
            st.rerun()
with nav_mid:
    st.markdown(f'<div style="text-align:center;color:#8A93A3;font-size:13px;">Etapa {step+1} de {n_steps}</div>', unsafe_allow_html=True)
with nav_next:
    if step < n_steps - 1:
        if st.button("Próximo →", use_container_width=True):
            st.session_state.step_idx = step + 1
            st.rerun()
