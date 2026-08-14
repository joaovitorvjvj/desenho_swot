import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA & ESTILOS
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EPROC/SEPLAN - Planejamento Estratégico",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 800; color: #1E3A8A; margin-bottom: 0px; }
    .sub-title { font-size: 16px; color: #64748B; margin-bottom: 20px; }
    .card-box {
        background-color: #F8FAFC; padding: 18px; border-radius: 10px;
        border-left: 6px solid #1E3A8A; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 15px;
    }
    .note-card {
        background-color: #FFFBEB; border: 1px solid #F59E0B; padding: 14px;
        border-radius: 10px; margin-bottom: 15px; font-size: 14px; color: #78350F;
    }
    .source-card {
        background-color: #F0FDF4; border: 1px solid #22C55E; padding: 14px;
        border-radius: 10px; margin-bottom: 15px; font-size: 14px; color: #14532D;
    }
    .metric-badge {
        background-color: #DBEAFE; color: #1E40AF; padding: 4px 10px;
        border-radius: 12px; font-weight: bold; font-size: 12px;
    }
    .layer-box {
        color: white; padding: 14px; border-radius: 8px; font-weight: bold;
        text-align: center; margin-bottom: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CABEÇALHO & SIDEBAR
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">🎯 Escritório de Gestão e Desburocratização de Processos (EPROC/SEPLAN)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plano Estratégico 2026 — Metodologia EPROC/SEPLAN (BSC + SWOT) | Consolidado das Etapas 1 a 4</div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/strategy.png", width=70)
    st.title("EPROC/SEPLAN")
    st.markdown("**Missão:**")
    st.caption("Conectar pessoas e tecnologias, por meio da Gestão por Processos de Negócio, proporcionando a melhoria dos serviços prestados à sociedade catarinense.")
    st.markdown("**Visão:**")
    st.caption("Consolidar a cultura de Gestão por Processos, com foco na experiência do usuário, como estratégia para melhoria dos serviços prestados pelo Governo do Estado de SC.")
    st.markdown("**Valores:**")
    st.caption("Colaboração • Visão Sistêmica • Melhoria Contínua • Inovação • Empatia • Resiliência • Otimismo • Pioneirismo")

    st.divider()
    st.markdown("### 📌 Fronteira de Atuação")
    st.success("✅ **O EPROC faz:** mapeamento, redesenho, levantamento de requisitos de negócio e consultoria de processos.")
    st.error("❌ **O EPROC NÃO faz:** codificação de sistemas ou desenvolvimento de software — isso é papel dos times de TI/SCTI.")

    st.divider()
    st.caption("⚡ Painel de apoio à Capacitação de Planejamento Estratégico — EPROC/SEPLAN 2026")

# ══════════════════════════════════════════════════════════════════
# DADOS — SWOT CONSOLIDADA (fonte: formulário Google, 57 respondentes,
# ~600 respostas brutas, clusterizadas por similaridade semântica)
# ══════════════════════════════════════════════════════════════════
swot_data = pd.DataFrame([
    # FORÇAS
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

    # FRAQUEZAS
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

    # OPORTUNIDADES
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

    # AMEAÇAS
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

# ══════════════════════════════════════════════════════════════════
# DADOS — CRUZAMENTOS TOWS QUE ORIGINARAM OS OBJETIVOS
# ══════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════
# DADOS — OBJETIVOS ESTRATÉGICOS (validados)
# ══════════════════════════════════════════════════════════════════
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
    1: [("Nº de processos mapeados como consultoria de negócio pré-automação", "Contagem de entregas BPMN + IT", "A definir", "Trimestral"),
        ("Taxa de aderência ao checklist de requisitos", "% de processos que seguiram o checklist padrão", "100%", "Contínua")],
    2: [("Normativo formal publicado", "Existência de decreto/instrução normativa vigente", "Publicado", "Marco único"),
        ("% de transições acompanhadas pelo EPROC", "Transições com EPROC envolvido / total de transições", "100% pós-normativo", "Semestral")],
    3: [("Nº de benchmarkings realizados", "Contagem de benchmarkings documentados", "2/ano", "Semestral"),
        ("Versão da metodologia publicada", "Nº de revisões formais", "1/ano", "Anual")],
    4: [("% de redução média de etapas (AS-IS x TO-BE)", "(Etapas AS-IS − TO-BE) / AS-IS, média", "A definir", "Anual"),
        ("Nº de órgãos atendidos com processo desburocratizado", "Órgãos distintos com TO-BE implementado", "A definir", "Anual")],
    5: [("Taxa de rotatividade de bolsistas", "Saídas / média de bolsistas ativos", "Reduzir vs. baseline", "Semestral"),
        ("% de bolsistas com onboarding concluído", "Concluintes / total admitidos", "100%", "Contínua")],
    6: [("ROI institucional do EPROC", "Ganhos de eficiência valorados / custo total", "A definir", "Anual"),
        ("Custo médio por processo mapeado", "Custo total / nº de processos mapeados", "Reduzir vs. baseline", "Semestral")],
    7: [("% de pontos focais NUPROC ativos", "Pontos focais atualizados / total de órgãos c/ NUPROC", "100%", "Semestral"),
        ("Nº de encontros de alinhamento com a rede", "Reuniões formais registradas", "4/ano", "Trimestral")],
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
PERSPECTIVA_COLOR = {
    "Pessoas": "#0F766E", "Orçamentária": "#0F766E",
    "Governança": "#0284C7", "Inovação": "#0284C7",
    "Processos Internos / Tecnologia": "#2563EB",
    "Resultados": "#1E3A8A", "Sustentabilidade": "#1E3A8A",
}

# ══════════════════════════════════════════════════════════════════
# ABAS
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 1. Diagnóstico SWOT",
    "🔗 2. Cruzamentos TOWS",
    "🎯 3. Objetivos Estratégicos",
    "🗺️ 4. Mapa Estratégico",
    "📋 5. Plano de Ação",
    "📈 6. Indicadores (KPI)",
    "ℹ️ Metodologia & Fontes",
])

# ------------------------------------------------------------------
# TAB 1: DIAGNÓSTICO SWOT
# ------------------------------------------------------------------
with tab1:
    st.subheader("📊 Diagnóstico Consolidado (Análise dos Ambientes)")
    st.caption("Consolidação semântica de ~600 respostas brutas de 57 respondentes, reduzidas a 60 conceitos (40 exibidos abaixo, os mais representativos por quadrante).")

    dim_filter = st.multiselect("Filtrar por dimensão", options=swot_data["Dimensão"].unique().tolist(),
                                 default=swot_data["Dimensão"].unique().tolist())
    filtered = swot_data[swot_data["Dimensão"].isin(dim_filter)]

    col_chart1, col_chart2 = st.columns(2)
    colors = {"Força": "#2E8B3A", "Fraqueza": "#E67E22", "Oportunidade": "#2980B9", "Ameaça": "#C0392B"}

    with col_chart1:
        for dim in ["Força", "Fraqueza"]:
            if dim in dim_filter:
                d = filtered[filtered["Dimensão"] == dim].sort_values("Frequência", ascending=True)
                fig = px.bar(d, x="Frequência", y="Conceito", orientation="h",
                             title=f"{'💪' if dim=='Força' else '⚠️'} {dim}s", color_discrete_sequence=[colors[dim]])
                fig.update_layout(height=320, margin=dict(l=0, r=10, t=35, b=0))
                st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        for dim in ["Oportunidade", "Ameaça"]:
            if dim in dim_filter:
                d = filtered[filtered["Dimensão"] == dim].sort_values("Frequência", ascending=True)
                fig = px.bar(d, x="Frequência", y="Conceito", orientation="h",
                             title=f"{'🚀' if dim=='Oportunidade' else '🔴'} {dim}s", color_discrete_sequence=[colors[dim]])
                fig.update_layout(height=320, margin=dict(l=0, r=10, t=35, b=0))
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="note-card">
    ⚠️ <b>Nota metodológica sobre o volume de menções:</b> a frequência de cada conceito reflete a recorrência
    percebida entre os respondentes, mas <b>não</b> foi usada como critério único de priorização dos objetivos —
    ela foi combinada com julgamento qualitativo da equipe de planejamento. Volume alto indica atenção, não
    determina automaticamente peso estratégico (mais detalhes na aba "Metodologia & Fontes").
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 Explorar todos os conceitos e detalhes"):
        st.dataframe(filtered[["Dimensão", "Conceito", "Frequência", "Detalhe"]], use_container_width=True, hide_index=True)

# ------------------------------------------------------------------
# TAB 2: CRUZAMENTOS TOWS
# ------------------------------------------------------------------
with tab2:
    st.subheader("🔗 Cruzamentos TOWS que originaram os Objetivos")
    st.caption("Cada cruzamento combina fatores internos (Força/Fraqueza) com fatores externos (Oportunidade/Ameaça) para gerar um objetivo estratégico.")

    tipo_labels = {"SO": "🟢 SO — Ofensiva", "WO": "🔵 WO — Reforço", "ST": "🟠 ST — Proteção", "WT": "🔴 WT — Defensiva"}
    for _, row in tows_data.iterrows():
        st.markdown(f"""
        <div class="card-box">
            <span class="metric-badge">{tipo_labels.get(row['Tipo'], row['Tipo'])}</span>
            <span class="metric-badge" style="background-color:#E0E7FF;color:#3730A3;margin-left:6px;">{row['Objetivo gerado']}</span>
            <p style="margin-top:10px; margin-bottom:4px;"><b>Origem (interno):</b> {row['Origem']}</p>
            <p style="margin-bottom:8px;"><b>Cruzado com (externo):</b> {row['Cruzado com']}</p>
            <small style="color:#64748B;"><b>Racional de validação:</b> {row['Racional']}</small>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 3: OBJETIVOS ESTRATÉGICOS
# ------------------------------------------------------------------
with tab3:
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
            <span class="metric-badge" style="background-color:#FEF3C7;color:#92400E;margin-left:6px;">{row['Eixo']}</span>
            <h4 style="margin-top: 8px; margin-bottom: 5px; color: #1E3A8A;">Objetivo {row['Nº']}</h4>
            <p style="color: #334155;">{row['Objetivo']}</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 4: MAPA ESTRATÉGICO
# ------------------------------------------------------------------
with tab4:
    st.subheader("🗺️ Mapa Estratégico (Cadeia de Causa e Efeito)")
    st.markdown("Relações entre os 7 objetivos, organizadas em 4 camadas causais — da base (viabilizadores) ao topo (resultado e legitimidade).")

    layers = {1: [], 2: [], 3: [], 4: []}
    for _, row in objetivos_data.iterrows():
        layers[PERSPECTIVA_LAYER[row["Perspectiva"]]].append(row)

    layer_titles = {4: "🏆 RESULTADO & LEGITIMIDADE", 3: "⚙️ OPERAÇÃO", 2: "🏛️ CAPACIDADE & MANDATO", 1: "🧱 VIABILIZADORES"}

    for lvl in [4, 3, 2, 1]:
        st.markdown(f"**{layer_titles[lvl]}**")
        cols = st.columns(len(layers[lvl]))
        for c, row in zip(cols, layers[lvl]):
            color = PERSPECTIVA_COLOR[row["Perspectiva"]]
            c.markdown(f"""<div class="layer-box" style="background-color:{color};">
                Obj. {row['Nº']} — {row['Perspectiva']}
                </div>""", unsafe_allow_html=True)
        if lvl > 1:
            st.markdown("<div style='text-align:center;font-size:20px;'>⬆️</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("##### Relações de causa-efeito detalhadas")
    obj_lookup = objetivos_data.set_index("Nº")["Perspectiva"].to_dict()
    causal_df = pd.DataFrame([
        {"De": f"Obj. {a} ({obj_lookup[int(a)]})", "Para": f"Obj. {b} ({obj_lookup[int(b)]})", "Racional": r}
        for a, b, r in CAUSAL_LINKS
    ])
    st.dataframe(causal_df, use_container_width=True, hide_index=True)
    st.caption("🔁 O laço Obj. 7 → Obj. 6 fecha um ciclo de retroalimentação: legitimidade institucional sustenta orçamento no ciclo seguinte.")

# ------------------------------------------------------------------
# TAB 5: PLANO DE AÇÃO
# ------------------------------------------------------------------
with tab5:
    st.subheader("📋 Plano de Ação por Objetivo")
    st.markdown("""
    <div class="note-card">
    📝 Ações em fase de validação/ajuste de prazos e responsáveis reais — os prazos abaixo são relativos
    ao início do plano (T1, T2...) e devem ser substituídos pelos períodos reais de execução.
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

# ------------------------------------------------------------------
# TAB 6: INDICADORES (KPI)
# ------------------------------------------------------------------
with tab6:
    st.subheader("📈 Indicadores por Objetivo (KPI)")

    obj_select = st.selectbox("Selecionar objetivo", options=objetivos_data["Nº"].tolist(),
                               format_func=lambda n: f"Objetivo {n} — {objetivos_data.set_index('Nº').loc[n, 'Perspectiva']}")

    kpis = INDICADORES[obj_select]
    kpi_df = pd.DataFrame(kpis, columns=["KPI", "Fórmula/Medição", "Meta", "Periodicidade"])
    st.dataframe(kpi_df, use_container_width=True, hide_index=True)

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
        m1.metric("Dias agilizados", f"{total_dias_salvos:,}")
        m2.metric("Horas revertidas", f"{total_horas_poupadas:,} h")
        m3.metric("Equivalente em FTEs", f"~{equivalente_servidores}")
        st.info(f"Redesenhando **{processos_ano} processos/ano**, o EPROC libera o equivalente a **{equivalente_servidores} servidores em tempo integral** para atendimento direto ao cidadão.")

# ------------------------------------------------------------------
# TAB 7: METODOLOGIA & FONTES
# ------------------------------------------------------------------
with tab7:
    st.subheader("ℹ️ Metodologia e Fontes dos Dados")

    st.markdown("""
    #### Como chegamos até aqui

    **Etapa 1 — Alinhamento Inicial:** definição do Plano de Projeto do Planejamento Estratégico (prazo de 1 mês),
    equipe responsável e as 8 perspectivas do Mapa Estratégico (Resultados, Processos Internos, Pessoas,
    Tecnologia, Orçamentária, Sustentabilidade, Inovação e Governança), seguindo a metodologia EPROC/SEPLAN
    versão 01/2026.

    **Etapa 2 — Análise dos Ambientes (SWOT):** coleta via formulário Google, com **57 respondentes** de
    múltiplos órgãos do Poder Executivo de SC, gerando cerca de **600 respostas brutas** (~150 por quadrante).
    Os dados foram higienizados e consolidados por agrupamento semântico, usando o modelo
    `paraphrase-multilingual-MiniLM-L12-v2` (Sentence Transformers), com agrupamento hierárquico por
    distância de cosseno, limiar de similaridade **0.72** e máximo de 15 conceitos por quadrante — resultando
    em 60 conceitos consolidados.

    **Etapa 3 — Formulação Estratégica:** os cruzamentos TOWS foram gerados a partir da matriz SWOT e
    priorizados **combinando recorrência quantitativa com validação qualitativa da equipe de planejamento** —
    o volume de menções por conceito não foi usado como critério único de decisão. Os 7 objetivos estratégicos
    foram redigidos no formato BSC (verbo no infinitivo) e distribuídos nas 8 perspectivas.

    **Etapa 4 — Desdobramento:** construção do Mapa Estratégico (relações de causa-efeito entre objetivos),
    Plano de Ação (responsáveis e prazos) e Indicadores (KPIs por objetivo).
    """)

    st.markdown("""
    <div class="note-card">
    ⚠️ <b>Nota de transparência sobre viés de amostragem:</b> o volume de respondentes por órgão não é
    proporcional, e o próprio processo de clusterização semântico envolve decisões técnicas (limiar de
    similaridade) que podem agrupar ou separar conceitos de forma diferente conforme o parâmetro escolhido.
    Por isso, a frequência de cada conceito deve ser lida como <b>sinal de atenção</b>, não como
    <b>determinação automática</b> de prioridade estratégica.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="source-card">
    ✅ <b>Missão, Visão e Valores</b> (referência de alinhamento para todos os objetivos):<br><br>
    <b>Missão:</b> Conectar pessoas e tecnologias, por meio da Gestão por Processos de Negócio, proporcionando
    a melhoria dos serviços prestados à sociedade catarinense.<br>
    <b>Visão:</b> Consolidar a cultura de Gestão por Processos, com foco na experiência do usuário, como
    estratégia para melhoria dos serviços prestados pelo Governo do Estado de SC.<br>
    <b>Valores:</b> Colaboração, Visão Sistêmica, Melhoria Contínua, Inovação, Empatia, Resiliência,
    Otimismo e Pioneirismo.
    </div>
    """, unsafe_allow_html=True)
