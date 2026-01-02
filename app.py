import streamlit as st
import math
import random

# --- Configuração da Página ---
st.set_page_config(
    page_title="Loteria: Análise Financeira",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Personalizado (Estilo Cyberpunk/Dark) ---
st.markdown("""
<style>
    /* Fundo Geral */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    /* Painéis e Caixas de Estatísticas */
    div[data-testid="stMetric"], div[data-testid="stMarkdownContainer"] p {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Botões da Grid (Tentativa de imitar as bolas) */
    div.stButton > button {
        background-color: #2a2a2a;
        color: #888;
        border: 2px solid #333;
        border-radius: 20px;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        border-color: #00bcd4;
        color: #00bcd4;
    }
    
    /* Botões de Ação Principais */
    .stButton button[kind="primary"] {
        background-color: #6200ea !important;
        color: white !important;
        border: none !important;
    }
    
    /* Inputs */
    .stNumberInput input, .stTextInput input {
        background-color: #2c2c2c;
        color: #00bcd4;
    }
    
    /* Títulos */
    h1, h2, h3 {
        color: #00bcd4 !important;
    }
    
    /* Cores de Texto Específicas */
    .neon-green { color: #69f0ae; font-weight: bold; }
    .neon-red { color: #ff5252; font-weight: bold; }
    .neon-yellow { color: #ffea00; font-weight: bold; }
    .neon-white { color: #ffffff; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- Inicialização de Estado (Session State) ---
if 'selected_balls' not in st.session_state:
    st.session_state.selected_balls = set()
if 'last_draw' not in st.session_state:
    st.session_state.last_draw = None
if 'simulation_msg' not in st.session_state:
    st.session_state.simulation_msg = ""
if 'simulation_style' not in st.session_state:
    st.session_state.simulation_style = ""

# --- Funções Auxiliares ---
def toggle_number(n):
    if n in st.session_state.selected_balls:
        st.session_state.selected_balls.remove(n)
    else:
        st.session_state.selected_balls.add(n)

def select_all():
    st.session_state.selected_balls = set(range(1, 61))

def clear_all():
    st.session_state.selected_balls = set()
    st.session_state.last_draw = None
    st.session_state.simulation_msg = ""

def parse_currency(text):
    try:
        # Remove R$, espaços e pontos de milhar, troca vírgula por ponto
        clean = text.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        return float(clean)
    except ValueError:
        return 0.0

def simulate_draw():
    if len(st.session_state.selected_balls) < 6:
        st.session_state.simulation_msg = "⚠️ Escolha pelo menos 6 números!"
        st.session_state.simulation_style = "color: #ff5252;"
        return

    drawn = set(random.sample(range(1, 61), 6))
    st.session_state.last_draw = drawn
    
    hits = len(drawn.intersection(st.session_state.selected_balls))
    
    # Monta mensagem
    nums_str = ", ".join(str(n) for n in sorted(list(drawn)))
    msg = f"Sorteio: {nums_str} | Acertos: {hits}"
    
    if hits == 6:
        st.session_state.simulation_msg = f"🎉 SENA! {msg}"
        st.session_state.simulation_style = "background-color: #ffff00; color: black; padding: 10px; border-radius: 5px;"
    elif hits == 5:
        st.session_state.simulation_msg = f"🌟 QUINA! {msg}"
        st.session_state.simulation_style = "background-color: #00e676; color: black; padding: 10px; border-radius: 5px;"
    elif hits == 4:
        st.session_state.simulation_msg = f"✨ QUADRA! {msg}"
        st.session_state.simulation_style = "background-color: #ffffff; color: black; padding: 10px; border-radius: 5px;"
    else:
        st.session_state.simulation_msg = msg
        st.session_state.simulation_style = "color: #ccc;"

# --- Sidebar (Inputs Financeiros) ---
with st.sidebar:
    st.header("💰 Configurações")
    
    unit_price = st.number_input("Valor Aposta Mínima (R$)", min_value=0.01, value=5.00, step=0.50, format="%.2f")
    
    prize_text = st.text_input("Prêmio Estimado (Texto)", value="2.000.000,00")
    prize_total = parse_currency(prize_text)
    
    winners = st.number_input("Número de Ganhadores", min_value=1, value=1)
    
    st.divider()
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Limpar Tudo"):
            clear_all()
            st.rerun()
    with col_btn2:
        if st.button("Marcar Tudo"):
            select_all()
            st.rerun()

# --- Lógica de Cálculos ---
k = len(st.session_state.selected_balls)
base_bet = 6
universe_combinations = math.comb(60, 6)

if k >= base_bet:
    equivalent_bets = math.comb(k, base_bet)
    total_cost = equivalent_bets * unit_price
    prize_individual = prize_total / winners
    net_profit = prize_individual - total_cost
    roi_pct = (net_profit / total_cost) * 100 if total_cost > 0 else 0
    chance = universe_combinations / equivalent_bets if equivalent_bets > 0 else 0
    
    # Strings formatadas
    n_str = f"{equivalent_bets:,}".replace(",", ".")
    unit_str = f"R$ {unit_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    total_cost_str = f"R$ {total_cost:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    cost_equation = f"{n_str} x {unit_str} = {total_cost_str}"
    
    profit_str = f"R$ {net_profit:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    profit_class = "neon-green" if net_profit >= 0 else "neon-red"
    prob_str = f"1 em {chance:,.0f}" if chance >= 1 else "Garantido"
else:
    equivalent_bets = 0
    cost_equation = "R$ 0,00"
    profit_str = "R$ 0,00"
    roi_pct = 0
    prob_str = "Selecione 6+"
    profit_class = "neon-white"

# --- Layout Principal ---
st.title("🎲 Loteria: Análise & Simulação")

# Dashboard Financeiro (Linha Superior)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"**Selecionados**<br><span class='neon-white' style='font-size:20px'>{k}</span>", unsafe_allow_html=True)
with col2:
    st.markdown(f"**Custo Total**<br><span class='neon-white' style='font-size:14px'>{cost_equation}</span>", unsafe_allow_html=True)
with col3:
    st.markdown(f"**Lucro Líquido**<br><span class='{profit_class}' style='font-size:18px'>{profit_str}</span>", unsafe_allow_html=True)
with col4:
    st.markdown(f"**Retorno**<br><span class='neon-white' style='font-size:18px'>{roi_pct:,.1f}%</span>", unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#888; margin-bottom: 20px;'>Probabilidade: {prob_str}</div>", unsafe_allow_html=True)

# Grid de Seleção
st.subheader("Selecione os Números")

# Criando a grid 6x10
for row in range(6):
    cols = st.columns(10)
    for col in range(10):
        num = row * 10 + col + 1
        
        # Define estilo visual baseado no estado
        label = str(num)
        is_selected = num in st.session_state.selected_balls
        is_drawn = st.session_state.last_draw and num in st.session_state.last_draw
        
        # Hack visual: emoji para indicar estado, já que não podemos mudar cor do botão facilmente sem CSS complexo
        if is_selected and is_drawn:
            display_label = f"★ {num}" # Acerto
        elif is_selected:
            display_label = f"✔ {num}" # Escolhido
        elif is_drawn:
            display_label = f"❌ {num}" # Sorteado (Erro)
        else:
            display_label = str(num)

        # Botão
        with cols[col]:
            # Se selecionado, usamos type="primary" para destacar (fica roxo/tema do streamlit)
            btn_type = "primary" if is_selected else "secondary"
            if st.button(display_label, key=f"btn_{num}", type=btn_type):
                toggle_number(num)
                st.rerun()

# --- Simulação ---
st.divider()
col_sim_btn, col_sim_res = st.columns([1, 3])

with col_sim_btn:
    if st.button("🚀 SIMULAR SORTEIO", type="primary", use_container_width=True):
        simulate_draw()
        st.rerun()

with col_sim_res:
    if st.session_state.simulation_msg:
        st.markdown(f"<div style='{st.session_state.simulation_style}; text-align:center; font-weight:bold; font-size:18px;'>{st.session_state.simulation_msg}</div>", unsafe_allow_html=True)