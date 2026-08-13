import streamlit as st
import pandas as pd
import plotly.express as px

# ══════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA & ESTILOS CUSTOMIZADOS
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="EPROC/SEPLAN - Planejamento Estratégico",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para visual moderno e corporativo
st.markdown("""
    <style>
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 16px;
        color: #64748B;
        margin-bottom: 25px;
    }
    .card-box {
        background-color: #F8FAFC;
        padding: 18px;
        border-radius: 10px;
        border-left: 6px solid #1E3A8A;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .boundary-card {
        background-color: #EFF6FF;
        border: 2px dashed #3B82F6;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-badge {
        background-color: #DBEAFE;
        color: #1E40AF;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# CABEÇALHO & SIDEBAR
# ══════════════════════════════════════════════════════════════════
st.markdown('<div class="main-title">🎯 Escritório de Gestão e Desburocratização de Processos (EPROC/SEPLAN)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plano Estratégico Consolidado — Posicionamento de Consultoria Interna de Negócios</div>', unsafe_allow_html=True)

with st.sidebar:
    st.image("https://img.icons8.com/color/96/strategy.png", width=70)
    st.title("EPROC/SEPLAN")
    st.markdown("**Missão Central:**")
    st.caption("Mapear, simplificar e redesenhar processos do Estado, entregando requisitos de negócio otimizados para a sociedade e para a TI.")
    
    st.divider()
    st.markdown("### 📌 Fronteira de Atuação")
    st.success("✅ **O EPROC faz:** Mapeamento, otimização, desburocratização e levantamento de requisitos de negócio.")
    st.error("❌ **O EPROC NÃO faz:** Codificação de sistemas ou desenvolvimento de software (papel da TI / SCTI).")
    
    st.divider()
    st.caption("⚡ *Painel Executivo Interativo — SC 2026*")

# ══════════════════════════════════════════════════════════════════
# DADOS DA MATRIZ SWOT HIGIENIZADA
# ══════════════════════════════════════════════════════════════════
swot_data = pd.DataFrame([
    # FORÇAS
    {"Dimensão": "Força", "Conceito": "Equipe Técnica Multidisciplinar", "Frequência": 18, "Detalhe": "Corpo técnico qualificado com conhecimento prático em processos públicos."},
    {"Dimensão": "Força", "Conceito": "Metodologia BPM Estruturada", "Frequência": 15, "Detalhe": "Padronização metodológica sólida e domínio de notação BPMN."},
    {"Dimensão": "Força", "Conceito": "Capilaridade e Rede NUPROCs", "Frequência": 12, "Detalhe": "Presença em diversos órgãos através dos Núcleos de Processos."},
    {"Dimensão": "Força", "Conceito": "Dominio de Ferramental Tecnológico", "Frequência": 9, "Detalhe": "Uso estratégico de ferramentas como Camunda, Taiga e Power BI."},
    
    # FRAQUEZAS
    {"Dimensão": "Fraqueza", "Conceito": "Sem Desenvolvimento Próprio (Dependência de TI)", "Frequência": 16, "Detalhe": "Dependência de órgãos externos de TI para codificar as automações mapeadas."},
    {"Dimensão": "Fraqueza", "Conceito": "Gargalos Operacionais e Morosidade", "Frequência": 14, "Detalhe": "Lentidão nas validações internas por parte das secretarias atendidas."},
    {"Dimensão": "Fraqueza", "Conceito": "Déficit de Pessoal e Rotatividade", "Frequência": 11, "Detalhe": "Ausência de quadro efetivo próprio e perda frequente de talentos."},
    {"Dimensão": "Fraqueza", "Conceito": "Maturidade Variável nos Clientes", "Frequência": 8, "Detalhe": "Baixa cultura de processos em determinadas áreas do Executivo."},

    # OPORTUNIDADES
    {"Dimensão": "Oportunidade", "Conceito": "Demanda Estadual por Desburocratização", "Frequência": 20, "Detalhe": "Pressão por serviços governamentais mais ágeis e menos burocráticos."},
    {"Dimensão": "Oportunidade", "Conceito": "Agenda de Transformação Digital", "Frequência": 17, "Detalhe": "Aumento dos projetos de automação no Estado demandando análise de requisitos."},
    {"Dimensão": "Oportunidade", "Conceito": "Alinhamento com Marcos Legais / Avança SC", "Frequência": 10, "Detalhe": "Apoio governamental para modernização da gestão pública."},

    # AMEAÇAS
    {"Dimensão": "Ameaça", "Conceito": "Expectativa Incorreta ('Achar que EPROC programa')", "Frequência": 15, "Detalhe": "Clientes achando que o EPROC é fábrica de software e deve construir o sistema."},
    {"Dimensão": "Ameaça", "Conceito": "Descontinuidade e Mudanças Políticas", "Frequência": 13, "Detalhe": "Risco de perda de alinhamento estratégico a cada troca de gestão."},
    {"Dimensão": "Ameaça", "Conceito": "Resistência Cultural à Mudança", "Frequência": 10, "Detalhe": "Aversão de servidores e gestores a novos fluxos de trabalho desburocratizados."}
])

# ══════════════════════════════════════════════════════════════════
# ABAS DA APLICAÇÃO
# ══════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. Diagnóstico SWOT", 
    "🎯 2. Objetivos & TOWS", 
    "🗺️ 3. Mapa Estratégico", 
    "📋 4. Plano de Ação Interativo", 
    "⚡ 5. Simulador de Impacto"
])

# ------------------------------------------------------------------
# TAB 1: DIAGNÓSTICO SWOT
# ------------------------------------------------------------------
with tab1:
    st.subheader("📊 Diagnóstico Consolidado (Resultado da NLP)")
    st.caption("Consolidação semântica de ~600 respostas brutas reduzidas a 14 conceitos-chave da realidade do EPROC.")
    
    # Gráfico de Visão Geral
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        fig_forcas = px.bar(
            swot_data[swot_data["Dimensão"] == "Força"].sort_values("Frequência", ascending=True),
            x="Frequência", y="Conceito", orientation="h",
            title="💪 Forças Internas",
            color_discrete_sequence=["#2E8B3A"]
        )
        fig_forcas.update_layout(height=280, margin=dict(l=0, r=10, t=35, b=0))
        st.plotly_chart(fig_forcas, use_container_width=True)
        
        fig_fraq = px.bar(
            swot_data[swot_data["Dimensão"] == "Fraqueza"].sort_values("Frequência", ascending=True),
            x="Frequência", y="Conceito", orientation="h",
            title="⚠️ Fraquezas Internas",
            color_discrete_sequence=["#E67E22"]
        )
        fig_fraq.update_layout(height=280, margin=dict(l=0, r=10, t=35, b=0))
        st.plotly_chart(fig_fraq, use_container_width=True)

    with col_chart2:
        fig_oport = px.bar(
            swot_data[swot_data["Dimensão"] == "Oportunidade"].sort_values("Frequência", ascending=True),
            x="Frequência", y="Conceito", orientation="h",
            title="🚀 Oportunidades Externas",
            color_discrete_sequence=["#2980B9"]
        )
        fig_oport.update_layout(height=280, margin=dict(l=0, r=10, t=35, b=0))
        st.plotly_chart(fig_oport, use_container_width=True)

        fig_ameaca = px.bar(
            swot_data[swot_data["Dimensão"] == "Ameaça"].sort_values("Frequência", ascending=True),
            x="Frequência", y="Conceito", orientation="h",
            title="🔴 Ameaças Externas",
            color_discrete_sequence=["#C0392B"]
        )
        fig_ameaca.update_layout(height=280, margin=dict(l=0, r=10, t=35, b=0))
        st.plotly_chart(fig_ameaca, use_container_width=True)

    with st.expander("🔍 Explorar Detalhes de Cada Conceito"):
        st.dataframe(
            swot_data[["Dimensão", "Conceito", "Frequência", "Detalhe"]],
            use_container_width=True,
            hide_index=True
        )

# ------------------------------------------------------------------
# TAB 2: OBJETIVOS ESTRATÉGICOS & TOWS
# ------------------------------------------------------------------
with tab2:
    st.subheader("🎯 Objetivos Estratégicos Oficiais (Formato BSC)")
    
    st.markdown("""
    <div class="boundary-card">
        <b>💡 ALINHAMENTO DE ESCOPO INSTITUCIONAL:</b><br>
        O EPROC posiciona-se como <b>Consultoria Interna de Negócios e Desburocratização</b>. O escritório é o especialista que analisa o processo, elimina o excesso de papelada, reduz etapas inúteis e entrega o <b>especificação de requisitos pronta</b>. A codificação e o desenvolvimento tecnológico continuam sob responsabilidade dos times de TI/SCTI.
    </div>
    """, unsafe_allow_html=True)
    
    tows_matrix = [
        {
            "Perspectiva": "1. Governança",
            "Objetivo": "Institucionalizar o EPROC via Decreto",
            "Descrição": "Garantir mandate formal para participação obrigatória do EPROC em reestruturações organizacionais e grandes projetos de desburocratização no Executivo.",
            "Cruzamento TOWS": "ST (Confronto): Usar a expertise técnica (Força) para blindar a atuação contra trocas de gestão (Ameaça)."
        },
        {
            "Perspectiva": "2. Processos Internos",
            "Objetivo": "Consolidar a Consultoria de Requisitos de Negócio",
            "Descrição": "Padronizar o modelo de atuação na tradução de necessidades de negócio antes da automação, entregando especificações limpas e enxutas para os times de TI.",
            "Cruzamento TOWS": "WO (Reforço): Usar a onda de Transformação Digital (Oportunidade) para suprir a ausência de desenvolvimento próprio (Fraqueza)."
        },
        {
            "Perspectiva": "3. Inovação",
            "Objetivo": "Atualizar a Metodologia e atuar como Ponte de Negócio/TI",
            "Descrição": "Manter a metodologia EPROC atualizada com benchmarking e práticas ágeis, facilitando o diálogo entre as áreas finalísticas do Estado e as equipes de TI.",
            "Cruzamento TOWS": "SO (Ofensiva): Usar o domínio metodológico (Força) para liderar a agenda de simplificação estadual (Oportunidade)."
        },
        {
            "Perspectiva": "4. Resultados",
            "Objetivo": "Guiar Oportunidades de Desburocratização por Dados",
            "Descrição": "Transformar as informações dos processos mapeados em dados estratégicos para identificar e eliminar os maiores gargalos governamentais.",
            "Cruzamento TOWS": "WT (Defensiva): Criar indicadores claros de impacto para combater a morosidade e alinhar expectativas de clientes (Ameaça)."
        },
        {
            "Perspectiva": "5. Capilaridade",
            "Objetivo": "Ampliar a Rede NUPROCs e a Cultura de Processos",
            "Descrição": "Engajar secretarias e capacitar equipes locais (NUPROCs) para multiplicar a cultura de simplificação e gestão por processos em todo o Estado.",
            "Cruzamento TOWS": "SO (Ofensiva): Alavancar a rede NUPROCs para escalar o atendimento sem sobrecarregar a equipe central."
        }
    ]
    
    for item in tows_matrix:
        st.markdown(f"""
        <div class="card-box">
            <span class="metric-badge">{item['Perspectiva']}</span>
            <h4 style="margin-top: 8px; margin-bottom: 5px; color: #1E3A8A;">{item['Objetivo']}</h4>
            <p style="margin-bottom: 8px; color: #334155;">{item['Descrição']}</p>
            <small style="color: #64748B;"><b>Cruzamento TOWS:</b> {item['Cruzamento TOWS']}</small>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 3: MAPA ESTRATÉGICO
# ------------------------------------------------------------------
with tab3:
    st.subheader("🗺️ Mapa Estratégico (Cadeia de Causa e Efeito)")
    st.markdown("Como a atuação do EPROC se transforma em valor para o cidadão catarinense:")
    
    st.markdown("""
    <div style="background-color: #F8FAFC; padding: 25px; border-radius: 12px; border: 1px solid #CBD5E1; text-align: center;">
        
        <!-- Nível 4: Impacto -->
        <div style="background-color: #1E3A8A; color: white; padding: 14px; border-radius: 8px; font-weight: bold; font-size: 16px;">
            🏆 RESULTADO FINAL: Serviços Públicos Mais Ágeis & Geração de Valor ao Cidadão
        </div>
        <div style="font-size: 22px; color: #1E3A8A; margin: 6px 0;">⬆️</div>
        
        <!-- Nível 3: Proposta de Valor -->
        <div style="background-color: #2563EB; color: white; padding: 14px; border-radius: 8px; font-weight: bold; font-size: 15px;">
            ✂️ PROPOSTA DE VALOR: Desburocratização, Simplificação & Eliminação de Gargalos
        </div>
        <div style="font-size: 22px; color: #2563EB; margin: 6px 0;">⬆️</div>
        
        <!-- Nível 2: Operação e Pessoas -->
        <div style="display: flex; gap: 12px; justify-content: center;">
            <div style="background-color: #0284C7; color: white; padding: 14px; border-radius: 8px; flex: 1; font-weight: bold;">
                ⚙️ CONSULTORIA DE NEGÓCIO<br>
                <small style="font-weight: normal;">Mapeamento, Redesenho & Requisitos p/ TI</small>
            </div>
            <div style="background-color: #0284C7; color: white; padding: 14px; border-radius: 8px; flex: 1; font-weight: bold;">
                🌐 CAPILARIDADE E PESSOAS<br>
                <small style="font-weight: normal;">Rede NUPROCs & Cultura de Eficiência</small>
            </div>
        </div>
        <div style="font-size: 22px; color: #0284C7; margin: 6px 0;">⬆️</div>
        
        <!-- Nível 1: Fundações -->
        <div style="display: flex; gap: 12px; justify-content: center;">
            <div style="background-color: #0F766E; color: white; padding: 14px; border-radius: 8px; flex: 1; font-weight: bold;">
                💡 INOVAÇÃO METODOLÓGICA<br>
                <small style="font-weight: normal;">Ponte entre Necessidade de Negócio e Soluções de TI</small>
            </div>
            <div style="background-color: #0F766E; color: white; padding: 14px; border-radius: 8px; flex: 1; font-weight: bold;">
                🏛️ GOVERNANÇA INSTITUCIONAL<br>
                <small style="font-weight: normal;">Mandato Formal via Decreto & Atuação Top-Down</small>
            </div>
        </div>
        
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
# TAB 4: PLANO DE AÇÃO INTERATIVO
# ------------------------------------------------------------------
with tab4:
    st.subheader("📋 Plano de Ação & Iniciativas Estratégicas")
    st.markdown("Acompanhe e simule a execução das iniciativas prioritárias do EPROC:")
    
    # Checkbox interativos com barra de progresso em tempo real
    toda_iniciativas = [
        ("Gov1", "Minuta do Decreto de Governança", "Elaborar minuta de Decreto instituindo a participação do EPROC em reestruturações estaduais.", "🏛️ Governança"),
        ("Gov2", "Alteração Oficial da Denominação", "Formalizar a alteração do nome para 'Escritório de Gestão e Desburocratização de Processos'.", "🏛️ Governança"),
        ("Proc1", "Guia de Levantamento de Requisitos", "Criar o Protocolo de Tradução de Negócio e Requisitos para repasse padronizado às equipes de TI.", "⚙️ Processos"),
        ("Proc2", "Playbook de Desburocratização", "Lançar o guia rápido de simplificação e eliminação de etapas burocráticas.", "⚙️ Processos"),
        ("Inov1", "Metodologia EPROC 2.0 (Ágil)", "Atualizar a metodologia de mapeamento incorporando práticas ágeis e benchmarking.", "💡 Inovação"),
        ("Capi1", "Plano de Expansão da Rede NUPROCs", "Estruturar trilha de capacitação e engajamento para os Núcleos de Processos nas secretarias.", "🌐 Capilaridade")
    ]
    
    if "status_acoes" not in st.session_state:
        st.session_state["status_acoes"] = {item[0]: False for item in toda_iniciativas}
        # Deixar as duas primeiras marcadas por padrão como exemplo
        st.session_state["status_acoes"]["Gov1"] = True
        st.session_state["status_acoes"]["Proc2"] = True

    # Progresso Geral
    concluidos = sum(st.session_state["status_acoes"].values())
    total = len(toda_iniciativas)
    percentual = int((concluidos / total) * 100)
    
    st.progress(concluidos / total)
    st.caption(f"**Progresso de Execução do Plano:** {concluidos} de {total} iniciativas concluídas ({percentual}%)")
    st.divider()

    col_act1, col_act2 = st.columns(2)
    
    for idx, (code, title, desc, tag) in enumerate(toda_iniciativas):
        target_col = col_act1 if idx % 2 == 0 else col_act2
        with target_col:
            is_checked = st.checkbox(
                f"**{title}** ({tag})", 
                value=st.session_state["status_acoes"][code],
                key=f"chk_{code}"
            )
            st.session_state["status_acoes"][code] = is_checked
            st.caption(desc)
            st.markdown("---")

# ------------------------------------------------------------------
# TAB 5: SIMULADOR DE IMPACTO E KPIS
# ------------------------------------------------------------------
with tab5:
    st.subheader("⚡ Simulador de Impacto da Desburocratização")
    st.markdown("Ajuste os controles abaixo para projetar o impacto das consultorias do EPROC no Estado:")
    
    sim_col1, sim_col2 = st.columns([1, 2])
    
    with sim_col1:
        st.markdown("##### 🎛️ Parâmetros da Simulação")
        processos_ano = st.slider("Processos Redesenhados / Ano", min_value=5, max_value=50, value=20, step=5)
        reducao_dias = st.slider("Redução Média no Tempo de Tramitação (dias)", min_value=5, max_value=60, value=25, step=5)
        horas_servidor = st.slider("Horas Economizadas por Processo/Ano", min_value=50, max_value=500, value=180, step=10)
        
    with sim_col2:
        st.markdown("##### 📈 Estimativa de Retorno em Eficiência Público")
        
        total_dias_salvos = processos_ano * reducao_dias
        total_horas_poupadas = processos_ano * horas_servidor
        equivalente_servidores = round(total_horas_poupadas / 1920, 1) # 1920h é a carga anual média
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Dias Agilizados na Sociedade", f"{total_dias_salvos:,} dias", delta="Ganho de Agilidade")
        m2.metric("Horas de Trabalho Revertidas", f"{total_horas_poupadas:,} h", delta="Eficiência Interna")
        m3.metric("Capacidade Operacional Liberta", f"~{equivalente_servidores} FTEs", delta="Produtividade")
        
        st.info(f"""
        💡 **O que estes números significam?**  
        Ao redesenhar **{processos_ano} processos críticos** por ano, o EPROC não apenas elimina papéis: ele libera o equivalente ao trabalho em tempo integral de **{equivalente_servidores} servidores públicos** para focar no atendimento direto ao cidadão catarinense, economizando **{total_dias_salvos:,} dias** de espera da sociedade.
        """)
