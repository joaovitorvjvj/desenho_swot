import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    import streamlit_sortables as sortables
    SORTABLES_AVAILABLE = True
except ImportError:
    SORTABLES_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EPROC/SEPLAN — Planejamento Estratégico",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Senha para liberar as etapas já elaboradas pela coordenação.
# TROQUE por uma senha sua antes de usar com a equipe.
UNLOCK_PASSWORD = "eproc2026"

STEPS = [
    {"label": "Diagnóstico", "icon": "📊", "sub": "SWOT consolidada", "locked": False},
    {"label": "Cruzamentos", "icon": "🧩", "sub": "Dinâmica em equipe", "locked": False},
    {"label": "Cruzamentos TOWS", "icon": "🔗", "sub": "Matriz TOWS", "locked": True},
    {"label": "Objetivos", "icon": "🎯", "sub": "Formato BSC", "locked": True},
    {"label": "Mapa", "icon": "🗺️", "sub": "Causa e efeito", "locked": True},
    {"label": "Ações", "icon": "📋", "sub": "Plano de execução", "locked": True},
    {"label": "Indicadores", "icon": "📈", "sub": "KPIs", "locked": True},
    {"label": "Metodologia", "icon": "ℹ️", "sub": "Fontes e critérios", "locked": False},
]

def render_lock_screen(label):
    st.markdown(f"""
    <div class="note-card" style="text-align:center; padding:46px 24px;">
        <div style="font-size:44px; margin-bottom:8px;">🔒</div>
        <div style="font-family:'Bebas Neue'; font-size:22px; letter-spacing:1px; color:{DARK_BLUE};">EM CONSTRUÇÃO</div>
        <p style="max-width:520px; margin:10px auto 0 auto; color:#7A3B12;">
            O conteúdo de <b>{label}</b> já foi elaborado pela coordenação, mas fica reservado até a equipe
            concluir a dinâmica de cruzamentos. Peça a senha ao facilitador para liberar a visualização.
        </p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        pwd = st.text_input("Senha de desbloqueio", type="password", key=f"pwd_inline_{label}")
        if st.button("Desbloquear", key=f"btn_inline_{label}", use_container_width=True):
            if pwd == UNLOCK_PASSWORD:
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Senha incorreta.")

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
    {"Tipo": "SO", "Origem": "Metodologia padronizada + Capacidade técnica", "Cruzado com": "Transformação digital / demanda por modernização",
     "Racional": "Usar a metodologia e a expertise consolidada para se posicionar como consultoria de negócio nas iniciativas de automação do Estado.",
     "Objetivo gerado": "1 — Consultoria de negócio em automação"},
    {"Tipo": "WT", "Origem": "Baixa força política institucional + Quantidade de servidores efetivos", "Cruzado com": "Mudanças políticas e institucionais (maior ameaça: 28 menções)",
     "Racional": "A maior ameaça identificada na coleta (mudança política) só é mitigada com mandato formal — não apenas apoio informal da gestão vigente.",
     "Objetivo gerado": "2 — Institucionalização via normativo formal"},
    {"Tipo": "SO", "Origem": "Capacidade técnica + Patrocínio da alta gestão", "Cruzado com": "Transformação digital",
     "Racional": "Direcionado para atualização metodológica contínua (benchmarking), não para desenvolvimento tecnológico próprio — fora do escopo real do EPROC.",
     "Objetivo gerado": "3 — Atualização metodológica contínua"},
    {"Tipo": "WT", "Origem": "Baixo nível de automação", "Cruzado com": "Instabilidade de infraestrutura tecnológica",
     "Racional": "Consolidado dentro do Objetivo 4 como indicador de resultado (redução de etapas/tempo), em vez de meta de automação própria.",
     "Objetivo gerado": "4 — Desburocratização comprovada por indicadores"},
    {"Tipo": "WO", "Origem": "Quantidade de servidores efetivos + Rotatividade", "Cruzado com": "Possibilidade de concurso público",
     "Racional": "Sem viabilidade de concurso no curto prazo, o objetivo foi redirecionado para qualificação do processo de seleção/desenvolvimento de bolsistas.",
     "Objetivo gerado": "5 — Qualificação de bolsistas"},
    {"Tipo": "ST", "Origem": "Patrocínio da alta gestão", "Cruzado com": "Limitação de recursos orçamentários",
     "Racional": "Reformulado de 'defesa de orçamento' para 'comprovação de retorno institucional' do orçamento já existente (~R$2M/ano).",
     "Objetivo gerado": "6 — Retorno institucional do investimento"},
    {"Tipo": "SO", "Origem": "Capilaridade institucional e rede de NUPROCs", "Cruzado com": "Fortalecimento da rede NUPROC / baixa visibilidade externa",
     "Racional": "Legitimidade institucional construída via relacionamento contínuo com a rede, não via menção a ciclos político-administrativos.",
     "Objetivo gerado": "7 — Relacionamento institucional e rede NUPROC"},
])

objetivos_data = pd.DataFrame([
    {"Nº": 1, "Perspectiva": "Processos Internos / Tecnologia",
     "Objetivo": "Consolidar o EPROC como unidade de referência em mapeamento de processos e levantamento de requisitos, atuando como consultoria de negócio nas iniciativas de automação conduzidas pelo Estado.",
     "Eixo": "Desburocratização"},
    {"Nº": 2, "Perspectiva": "Governança",
     "Objetivo": "Institucionalizar, via normativo formal, a participação obrigatória do EPROC em processos de criação, reestruturação ou extinção de secretarias, diretorias, gerências e empresas públicas, padronizando a transferência de conhecimento, papéis e atividades.",
     "Eixo": "Autonomia"},
    {"Nº": 3, "Perspectiva": "Inovação",
     "Objetivo": "Atualizar continuamente a metodologia EPROC com base em práticas de mercado e benchmarking interinstitucional, consolidando-se como referência metodológica em gestão por processos no setor público estadual.",
     "Eixo": "Empreendedorismo/Inovação"},
    {"Nº": 4, "Perspectiva": "Resultados",
     "Objetivo": "Consolidar o EPROC como agente de desburocratização do Poder Executivo estadual.",
     "Eixo": "Desburocratização"},
    {"Nº": 5, "Perspectiva": "Pessoas",
     "Objetivo": "Qualificar o processo de seleção e desenvolvimento de bolsistas do EPROC, com foco em perfil de negócio em processos e automação, para sustentar a qualidade técnica independentemente da rotatividade inerente ao modelo de bolsas.",
     "Eixo": "Autonomia"},
    {"Nº": 6, "Perspectiva": "Orçamentária",
     "Objetivo": "Maximizar o retorno institucional do investimento orçamentário do EPROC, direcionando recursos para a formação de corpo técnico especializado e comprovando ganhos de eficiência nos órgãos atendidos.",
     "Eixo": "Autonomia"},
    {"Nº": 7, "Perspectiva": "Sustentabilidade",
     "Objetivo": "Fortalecer o relacionamento institucional do EPROC com os órgãos atendidos, consolidando a rede de NUPROCs como canal permanente de engajamento e colaboração.",
     "Eixo": "Autonomia"},
])

INDICADORES = {
    1: [("Processos mapeados como consultoria pré-automação", "Contagem de entregas BPMN + IT", "A definir", "Trimestral", "🗂️"),
        ("Aderência ao checklist de requisitos", "% de processos que seguiram o checklist padrão", "100%", "Contínua", "✅")],
    2: [("Normativo formal publicado", "Existência de decreto/instrução vigente", "Publicado", "Marco único", "📜"),
        ("Transições acompanhadas pelo EPROC", "Transições com EPROC envolvido / total", "100% pós-normativo", "Semestral", "🏛️")],
    3: [("Benchmarkings realizados", "Contagem de benchmarkings documentados", "2/ano", "Semestral", "🔎"),
        ("Versão da metodologia publicada", "Nº de revisões formais", "1/ano", "Anual", "📘")],
    4: [("Redução média de etapas (AS-IS x TO-BE)", "(Etapas AS-IS − TO-BE) / AS-IS", "A definir", "Anual", "⚡"),
        ("Órgãos atendidos com processo desburocratizado", "Órgãos distintos com TO-BE implementado", "A definir", "Anual", "🏢")],
    5: [("Rotatividade de bolsistas", "Saídas / média de bolsistas ativos", "Reduzir vs. baseline", "Semestral", "🔄"),
        ("Onboarding concluído", "Concluintes / total admitidos", "100%", "Contínua", "🎓")],
    6: [("ROI institucional do EPROC", "Ganhos de eficiência valorados / custo total", "A definir", "Anual", "💰"),
        ("Custo médio por processo mapeado", "Custo total / nº de processos", "Reduzir vs. baseline", "Semestral", "📉")],
    7: [("Pontos focais NUPROC ativos", "Atualizados / total de órgãos c/ NUPROC", "100%", "Semestral", "🌐"),
        ("Encontros de alinhamento com a rede", "Reuniões formais registradas", "4/ano", "Trimestral", "🤝")],
}

ACOES = {
    1: [("Formalizar protocolo de atuação como consultoria de negócio para automação de terceiros", "Coordenação EPROC", "T1"),
        ("Criar checklist padrão de levantamento de requisitos pré-automação", "Equipe EPROC", "T1"),
        ("Mapear e documentar novos processos nos órgãos prioritários", "Equipe EPROC", "Contínuo")],
    2: [("Redigir minuta de normativo/decreto de participação obrigatória", "Coordenação EPROC", "T1-T2"),
        ("Articular validação jurídica e política junto à SEPLAN", "Coordenação + Gerência", "T2"),
        ("Elaborar playbook de transferência de conhecimento em transições", "Equipe EPROC", "T2")],
    3: [("Realizar benchmarking com metodologias de BPM (setor público/privado)", "Equipe EPROC", "Semestral"),
        ("Revisar e publicar nova versão da metodologia EPROC/SEPLAN", "Coordenação EPROC", "Anual"),
        ("Criar repositório interno de boas práticas por projeto mapeado", "Equipe EPROC", "Contínuo")],
    4: [("Estabelecer linha de base (AS-IS) de tempo/etapas dos processos mapeados", "Equipe EPROC", "T1"),
        ("Medir redução de tempo/etapas (TO-BE) a cada processo remapeado", "Equipe EPROC", "Contínuo"),
        ("Consolidar relatório anual de impacto", "Gerência EPROC", "Anual")],
    5: [("Revisar critérios do plano de trabalho FAPESC para priorizar perfil de negócio/automação", "Coordenação EPROC", "T1"),
        ("Estruturar trilha de onboarding técnico padronizado", "Gerência EPROC", "T1-T2"),
        ("Criar programa interno de capacitação continuada", "Equipe EPROC", "Contínuo")],
    6: [("Mapear custo do EPROC por processo (horas/pessoa alocadas)", "Gerência EPROC", "T1"),
        ("Cruzar custo com ganhos de eficiência comprovados (Obj. 4) para ROI", "Gerência EPROC", "Semestral"),
        ("Apresentar relatório de retorno orçamentário à alta gestão", "Coordenação EPROC", "Anual")],
    7: [("Mapear e atualizar cadastro de pontos focais NUPROC", "Equipe EPROC", "T1"),
        ("Realizar encontros periódicos de alinhamento com a rede", "Coordenação EPROC", "Trimestral"),
        ("Criar canal permanente de comunicação com os órgãos atendidos", "Equipe EPROC", "T2 em diante")],
}

CAUSAL_LINKS = [
    ("5", "3", "Bolsistas com perfil de negócio/automação sustentam a atualização contínua da metodologia."),
    ("5", "2", "Corpo técnico qualificado dá credibilidade para sustentar o pedido de mandato formal."),
    ("6", "1", "Investimento bem direcionado sustenta a capacidade de atuação como consultoria de negócio."),
    ("6", "2", "Comprovação de eficiência do investimento é argumento político para formalizar o normativo."),
    ("2", "1", "Mandato formal garante que o EPROC seja acionado nas transições e automações."),
    ("3", "1", "Metodologia atualizada é o 'como' da consultoria de negócio."),
    ("1", "4", "Consultoria de negócio bem executada gera desburocratização mensurável."),
    ("1", "7", "Entregas consistentes fortalecem o relacionamento com os órgãos (rede NUPROC)."),
    ("4", "7", "Resultado comprovado retroalimenta a legitimidade institucional."),
    ("7", "6", "Legitimidade e relacionamento forte facilitam sustentar orçamento no ciclo seguinte (laço de retroalimentação)."),
]

PERSPECTIVA_LAYER = {
    "Pessoas": 1, "Orçamentária": 1,
    "Governança": 2, "Inovação": 2,
    "Processos Internos / Tecnologia": 3,
    "Resultados": 4, "Sustentabilidade": 4,
}

# ══════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="brand-title">Escritório de Gestão e Desburocratização de Processos</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">EPROC / SEPLAN · Plano Estratégico 2026 — Metodologia BSC + SWOT · Consolidado das Etapas 1 a 4</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<div style="font-family:\'Bebas Neue\';font-size:26px;color:{DARK_BLUE};">EPROC / SEPLAN</div>', unsafe_allow_html=True)
    st.markdown("**Missão**")
    st.caption("Conectar pessoas e tecnologias, por meio da Gestão por Processos de Negócio, proporcionando a melhoria dos serviços prestados à sociedade catarinense.")
    st.markdown("**Visão**")
    st.caption("Consolidar a cultura de Gestão por Processos, com foco na experiência do usuário, como estratégia para melhoria dos serviços prestados pelo Governo do Estado de SC.")
    st.markdown("**Valores**")
    st.caption("Colaboração • Visão Sistêmica • Melhoria Contínua • Inovação • Empatia • Resiliência • Otimismo • Pioneirismo")
    st.divider()
    st.markdown("### 📌 Fronteira de Atuação")
    st.success("✅ **Faz:** mapeamento, redesenho, requisitos de negócio, consultoria de processos.")
    st.error("❌ **Não faz:** codificação/desenvolvimento de sistemas (papel da TI/SCTI).")

    st.divider()
    if st.session_state.get("unlocked", False):
        st.markdown("### 🔓 Conteúdo avançado liberado")
        if st.button("Bloquear novamente", use_container_width=True):
            st.session_state.unlocked = False
            st.rerun()
    else:
        st.markdown("### 🔒 Conteúdo avançado")
        st.caption("Objetivos, Mapa, Ações e Indicadores ficam reservados até a equipe concluir a dinâmica de cruzamentos.")
        pwd_sidebar = st.text_input("Senha do facilitador", type="password", key="pwd_sidebar")
        if st.button("Desbloquear", use_container_width=True, key="btn_sidebar"):
            if pwd_sidebar == UNLOCK_PASSWORD:
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Senha incorreta.")

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
        is_locked = step_info["locked"] and not st.session_state.get("unlocked", False)
        icon = "🔒" if is_locked else step_info["icon"]
        sub_label = "Em construção" if is_locked else step_info["sub"]
        st.markdown(f"""
        <div class="step-node">
            <div class="step-circle {state}" style="{'opacity:0.55;' if is_locked else ''}">{icon}</div>
            <div class="step-label">{step_info['label']}</div>
            <div class="step-sub" style="{'color:#B85C2E;font-weight:700;' if is_locked else ''}">{sub_label}</div>
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
# STEP 1 — FOLHA DE CRUZAMENTOS (dinâmica em equipe, interativa)
# ══════════════════════════════════════════════════════════════════
elif step == 1:
    st.subheader("🧩 Folha de Cruzamentos TOWS — Dinâmica em Equipe")
    st.caption("Arrastem os conceitos da SWOT para dentro do quadrante de cruzamento correspondente. Um mesmo conceito pode ser usado em mais de um cruzamento — copiem o texto de volta pro banco se precisarem reutilizá-lo.")

    st.markdown("""
    <div class="note-card">
    📝 <b>Como funciona:</b> os conceitos abaixo vêm direto do diagnóstico SWOT já consolidado, ordenados do mais
    citado pro menos citado. Arrastem Forças/Fraquezas e Oportunidades/Ameaças para o quadrante certo (SO, WO, ST
    ou WT) e escrevam, no campo de observação, a ideia de objetivo que surge da combinação. Ao final, cliquem em
    <b>"Exportar resultado"</b> — sem isso, o trabalho se perde se a página for recarregada.
    </div>
    """, unsafe_allow_html=True)

    if "tows_board" not in st.session_state:
        banco_inicial = []
        for _, r in swot_data.sort_values("Frequência", ascending=False).iterrows():
            prefixo = {"Força": "💪", "Fraqueza": "⚠️", "Oportunidade": "🚀", "Ameaça": "🔴"}[r["Dimensão"]]
            banco_inicial.append(f"{prefixo} {r['Conceito']}")
        st.session_state.tows_board = [
            {"header": "🏦 Banco de Conceitos", "items": banco_inicial},
            {"header": "🟢 SO — Ofensiva", "items": []},
            {"header": "🔵 WO — Reforço", "items": []},
            {"header": "🟠 ST — Proteção", "items": []},
            {"header": "🔴 WT — Defensiva", "items": []},
        ]

    if SORTABLES_AVAILABLE:
        # CSS ajustado para forçar layout lado a lado (row), com o banco mais largo
        # que os 4 quadrantes de cruzamento, e rolagem horizontal em telas estreitas.
        custom_style = f"""
        .sortable-component {{
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 12px;
            overflow-x: auto;
            padding-bottom: 8px;
            align-items: flex-start;
        }}
        .sortable-container {{
            background-color: {WHITE};
            border-radius: 12px;
            border: 1px solid #E2E4E9;
            box-shadow: 0 2px 10px rgba(13,27,42,0.05);
            flex: 0 0 220px;
            min-width: 220px;
        }}
        .sortable-container:first-child {{
            flex: 0 0 300px;
            min-width: 300px;
        }}
        .sortable-container-header {{
            background-color: {DARK_BLUE};
            color: {WHITE};
            font-weight: 700;
            padding: 10px 12px;
            border-radius: 12px 12px 0 0;
            font-size: 13px;
        }}
        .sortable-container-body {{
            background-color: {WHITE};
            min-height: 260px;
            padding: 8px;
        }}
        .sortable-item {{
            background-color: {LIGHT_GRAY};
            border: 1px solid #E2E4E9;
            border-radius: 8px;
            padding: 8px 10px;
            margin-bottom: 6px;
            font-size: 12.5px;
            color: {DARK_BLUE};
        }}
        .sortable-item:hover {{ border-color: {ORANGE}; }}
        """
        st.session_state.tows_board = sortables.sort_items(
            st.session_state.tows_board,
            multi_containers=True,
            direction="horizontal",
            custom_style=custom_style,
            key="tows_sortable_widget",
        )
    else:
        st.warning("A biblioteca `streamlit-sortables` não está instalada — usando alternativa por seleção. Rode `pip install streamlit-sortables` para arrastar de verdade.")
        board_lookup = {c["header"]: c["items"] for c in st.session_state.tows_board}
        todos_itens = st.session_state.tows_board[0]["items"] + [
            it for c in st.session_state.tows_board[1:] for it in c["items"]
        ]
        for c in st.session_state.tows_board[1:]:
            selecionados = st.multiselect(c["header"], options=sorted(set(todos_itens)), default=c["items"], key=f"ms_{c['header']}")
            c["items"] = selecionados

    st.write("")
    col_reset, col_count = st.columns([1, 3])
    with col_reset:
        if st.button("↺ Reiniciar quadro"):
            del st.session_state["tows_board"]
            st.rerun()
    with col_count:
        usados = sum(len(c["items"]) for c in st.session_state.tows_board[1:])
        st.caption(f"{usados} conceito(s) já posicionados nos quadrantes de cruzamento.")

    st.divider()
    st.markdown("##### 📝 Observações — ideia de objetivo por cruzamento")
    obs_cols = st.columns(4)
    labels_obs = ["🟢 SO — Ofensiva", "🔵 WO — Reforço", "🟠 ST — Proteção", "🔴 WT — Defensiva"]
    if "tows_obs" not in st.session_state:
        st.session_state.tows_obs = {l: "" for l in labels_obs}
    for c, label in zip(obs_cols, labels_obs):
        with c:
            st.session_state.tows_obs[label] = st.text_area(
                label, value=st.session_state.tows_obs.get(label, ""),
                height=140, key=f"obs_{label}",
                placeholder="Qual objetivo surge dessa combinação?"
            )

    # ---------- EXPORTAR RESULTADO ----------
    st.divider()
    st.markdown("##### 💾 Salvar o trabalho da equipe")
    st.caption("Isso gera um arquivo de texto com tudo que foi arrastado e escrito — guardem esse arquivo, é a partir dele que os Objetivos Estratégicos reais (não os que já estão pré-elaborados) devem ser construídos.")

    linhas_export = ["FOLHA DE CRUZAMENTOS TOWS — EPROC/SEPLAN", "=" * 50, ""]
    board_map = {c["header"]: c["items"] for c in st.session_state.tows_board}
    for label in labels_obs:
        linhas_export.append(f"\n{label}")
        linhas_export.append("-" * len(label))
        itens = board_map.get(label, [])
        if itens:
            for it in itens:
                linhas_export.append(f"  • {it}")
        else:
            linhas_export.append("  (nenhum conceito posicionado)")
        obs_texto = st.session_state.tows_obs.get(label, "").strip()
        linhas_export.append(f"  Ideia de objetivo: {obs_texto if obs_texto else '(não preenchido)'}")

    conteudo_export = "\n".join(linhas_export)
    st.download_button(
        "⬇️ Exportar resultado (.txt)",
        data=conteudo_export,
        file_name="cruzamentos_tows_equipe.txt",
        mime="text/plain",
        use_container_width=True,
    )
# ══════════════════════════════════════════════════════════════════
# STEP 2 — CRUZAMENTOS TOWS
# ══════════════════════════════════════════════════════════════════
elif step == 2:
    if not st.session_state.get("unlocked", False):
        render_lock_screen("Cruzamentos TOWS")
    else:
        st.subheader("🔗 Cruzamentos TOWS que originaram os Objetivos")
        st.caption("Cada cruzamento combina fatores internos (Força/Fraqueza) com fatores externos (Oportunidade/Ameaça) para gerar um objetivo estratégico.")

        tipo_labels = {"SO": "🟢 SO — Ofensiva", "WO": "🔵 WO — Reforço", "ST": "🟠 ST — Proteção", "WT": "🔴 WT — Defensiva"}
        for _, row in tows_data.iterrows():
            st.markdown(f"""
            <div class="card-box accent">
                <span class="metric-badge">{tipo_labels.get(row['Tipo'], row['Tipo'])}</span>
                <span class="metric-badge orange" style="margin-left:6px;">{row['Objetivo gerado']}</span>
                <p style="margin-top:10px; margin-bottom:4px;"><b>Origem (interno):</b> {row['Origem']}</p>
                <p style="margin-bottom:8px;"><b>Cruzado com (externo):</b> {row['Cruzado com']}</p>
                <small style="color:#64748B;"><b>Racional de validação:</b> {row['Racional']}</small>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STEP 3 — OBJETIVOS ESTRATÉGICOS
# ══════════════════════════════════════════════════════════════════
elif step == 3:
    if not st.session_state.get("unlocked", False):
        render_lock_screen("Objetivos Estratégicos")
    else:
        st.subheader("🎯 Objetivos Estratégicos (Formato BSC)")
        st.markdown("""
        <div class="source-card">
        💡 <b>Alinhamento de escopo institucional:</b> o EPROC posiciona-se como <b>consultoria interna de negócios
        e desburocratização</b>. O escritório mapeia, simplifica e entrega requisitos prontos — a codificação e o
        desenvolvimento tecnológico permanecem sob responsabilidade dos times de TI/SCTI.
        </div>
        """, unsafe_allow_html=True)

        eixo_filter = st.multiselect("Filtrar por eixo temático", options=objetivos_data["Eixo"].unique().tolist(),
                                      default=objetivos_data["Eixo"].unique().tolist())
        obj_filtered = objetivos_data[objetivos_data["Eixo"].isin(eixo_filter)]

        for _, row in obj_filtered.iterrows():
            st.markdown(f"""
            <div class="card-box">
                <span class="metric-badge">{row['Perspectiva']}</span>
                <span class="metric-badge orange" style="margin-left:6px;">{row['Eixo']}</span>
                <h4 style="margin-top: 8px; margin-bottom: 5px; color: {DARK_BLUE}; font-family:'Bebas Neue';letter-spacing:0.5px;">OBJETIVO {row['Nº']}</h4>
                <p style="color: #334155;">{row['Objetivo']}</p>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# STEP 4 — MAPA ESTRATÉGICO
# ══════════════════════════════════════════════════════════════════
elif step == 4:
    if not st.session_state.get("unlocked", False):
        render_lock_screen("Mapa Estratégico")
    else:
        st.subheader("🗺️ Mapa Estratégico")

        st.markdown(f"""
        <div class="source-card">
        <b>O que é este mapa e como usá-lo:</b> os 7 objetivos estratégicos estão organizados em <b>4 camadas de
        causa e efeito</b> — de baixo para cima. A cor evolui do azul escuro (fundação) ao laranja (resultado),
        reforçando a leitura: <b>investir na base sustenta a capacidade, que viabiliza a operação, que gera o
        resultado no topo.</b> Use o seletor abaixo para ver as conexões de um objetivo específico.
        </div>
        """, unsafe_allow_html=True)

        layer_info = {
            4: ("RESULTADO & LEGITIMIDADE", "O que a sociedade e a alta gestão enxergam"),
            3: ("OPERAÇÃO", "O que o EPROC entrega no dia a dia"),
            2: ("CAPACIDADE & MANDATO", "O que viabiliza a operação"),
            1: ("FUNDAÇÃO", "O que sustenta tudo o resto"),
        }
        layers = {1: [], 2: [], 3: [], 4: []}
        for _, row in objetivos_data.iterrows():
            layers[PERSPECTIVA_LAYER[row["Perspectiva"]]].append(row)

        for lvl in [4, 3, 2, 1]:
            title, desc = layer_info[lvl]
            st.markdown(f'<div class="layer-header">{title} <span style="color:#8A93A3;font-family:\'Roboto Condensed\';font-size:12px;">— {desc}</span></div>', unsafe_allow_html=True)
            cols = st.columns(len(layers[lvl]))
            for c, row in zip(cols, layers[lvl]):
                color = LAYER_COLORS[lvl]
                with c:
                    st.markdown(f"""<div class="node-card" style="background-color:{color};">
                        <div class="node-num">OBJ. {row['Nº']}</div>
                        <div class="node-persp">{row['Perspectiva']}</div>
                        </div>""", unsafe_allow_html=True)
            if lvl > 1:
                st.markdown('<div class="flow-arrow">⬆</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("##### 🔍 Explorar conexões de um objetivo")
        obj_lookup = objetivos_data.set_index("Nº")["Perspectiva"].to_dict()
        sel = st.selectbox("Selecionar objetivo", options=objetivos_data["Nº"].tolist(),
                            format_func=lambda n: f"Objetivo {n} — {obj_lookup[n]}")

        alimenta = [(b, r) for a, b, r in CAUSAL_LINKS if int(a) == sel]
        alimentado_por = [(a, r) for a, b, r in CAUSAL_LINKS if int(b) == sel]

        col_in, col_out = st.columns(2)
        with col_in:
            st.markdown(f"**⬅️ É alimentado por** ({len(alimentado_por)})")
            if alimentado_por:
                for a, r in alimentado_por:
                    st.markdown(f"""<div class="card-box" style="padding:12px 14px;">
                        <b>Objetivo {a}</b> — {obj_lookup[int(a)]}<br><small style="color:#64748B;">{r}</small>
                        </div>""", unsafe_allow_html=True)
            else:
                st.caption("Nenhuma dependência de entrada mapeada — este é um objetivo de base.")
        with col_out:
            st.markdown(f"**➡️ Alimenta** ({len(alimenta)})")
            if alimenta:
                for b, r in alimenta:
                    st.markdown(f"""<div class="card-box accent" style="padding:12px 14px;">
                        <b>Objetivo {b}</b> — {obj_lookup[int(b)]}<br><small style="color:#64748B;">{r}</small>
                        </div>""", unsafe_allow_html=True)
            else:
                st.caption("Nenhum objetivo dependente mapeado — este é um objetivo de topo.")

        st.caption("🔁 O laço Obj. 7 → Obj. 6 fecha um ciclo de retroalimentação: legitimidade institucional sustenta orçamento no ciclo seguinte.")

# ══════════════════════════════════════════════════════════════════
# STEP 5 — PLANO DE AÇÃO
# ══════════════════════════════════════════════════════════════════
elif step == 5:
    if not st.session_state.get("unlocked", False):
        render_lock_screen("Plano de Ação")
    else:
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
    if not st.session_state.get("unlocked", False):
        render_lock_screen("Indicadores")
    else:
        st.subheader("📈 Indicadores por Objetivo")

        obj_lookup_full = objetivos_data.set_index("Nº")
        obj_select = st.selectbox("Selecionar objetivo", options=objetivos_data["Nº"].tolist(),
                                   format_func=lambda n: f"Objetivo {n} — {obj_lookup_full.loc[n, 'Perspectiva']}")

        kpis = INDICADORES[obj_select]
        kcols = st.columns(len(kpis))
        for c, (nome, formula, meta, periodo, icon) in zip(kcols, kpis):
            with c:
                st.markdown(f"""
                <div class="kpi-icon-card">
                    <div class="kpi-icon">{icon}</div>
                    <div class="kpi-title">{nome}</div>
                    <div class="kpi-meta">📐 {formula}</div>
                    <div class="kpi-meta">🎯 Meta: <b>{meta}</b></div>
                    <div class="kpi-meta">🗓️ {periodo}</div>
                </div>
                """, unsafe_allow_html=True)

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
