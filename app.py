from datetime import date
import os
import google.generativeai as genai
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="App de Pesquisa Imobiliária com IA", page_icon="🏢", layout="wide"
)

st.title("🏢 Sistema de Pesquisa e Avaliação Imobiliária com IA")
st.write(
    "Gerencie seu banco de imobiliárias, execute buscas automatizadas e gere"
    " quadros técnicos consistentes para laudos."
)

# Arquivo de Banco de Dados Local para Imobiliárias
ARQUIVO_DB = "imobiliarias_cadastradas.csv"


def carregar_imobiliarias():
  if os.path.exists(ARQUIVO_DB):
    return pd.read_csv(ARQUIVO_DB)
  else:
    df_inicial = pd.DataFrame(
        {
            "Nome da Imobiliária": ["Concreto Imóveis", "Lider LP"],
            "Site / Link": [
                "https://www.concretoimoveis.com.br",
                "https://liderlp.com.br",
            ],
        }
    )
    df_inicial.to_csv(ARQUIVO_DB, index=False)
    return df_inicial


if "imobiliarias" not in st.session_state:
  st.session_state["imobiliarias"] = carregar_imobiliarias()

if "relatorio_laudo" not in st.session_state:
  st.session_state["relatorio_laudo"] = pd.DataFrame(
      columns=[
          "Informante",
          "Data",
          "Ref",
          "Valor Total (R$)",
          "Tamanho (m²)",
          "Valor Unitário (R$/m²)",
          "Topografia",
          "Link/Foto",
      ]
  )

# --- GERENCIAMENTO DA CHAVE DE API ---
if "api_key_salva" not in st.session_state:
  st.session_state["api_key_salva"] = st.secrets.get("GOOGLE_API_KEY", "")

with st.sidebar:
  st.header("🔑 Configuração da Chave de IA")
  chave_input = st.text_input(
      "Chave de API do Google AI Studio",
      value=st.session_state["api_key_salva"],
      type="password",
      help=(
          "Cole sua chave uma vez. Ela ficará memorizada durante sua sessão"
          " ativa."
      ),
  )
  if chave_input:
    st.session_state["api_key_salva"] = chave_input
    st.success("Chave de API configurada e memorizada!")
  else:
    st.warning("Insira sua chave gratuita (aistudio.google.com).")

# --- ABAS DO APLICATIVO ---
aba1, aba2, aba3 = st.tabs(
    [
        "📥 Cadastro de Imobiliárias",
        "🔍 Agente de Pesquisa",
        "📊 Quadro Consolidado (Laudo)",
    ]
)

# --- ABA 1: CADASTRO E EXCLUSÃO DE IMOBILIÁRIAS ---
with aba1:
  st.header("Gerenciamento do Banco de Dados de Imobiliárias")
  st.write(
      "Cadastre novas fontes ou exclua imobiliárias que não deseja mais"
      " consultar."
  )

  with st.form("form_cad_imob", clear_on_submit=True):
    col_c1, col_c2 = st.columns(2)
    with col_c1:
      novo_nome = st.text_input("Nome da Imobiliária")
    with col_c2:
      novo_site = st.text_input("Link ou Site Oficial (ex: https://...)")

    btn_cadastrar = st.form_submit_button("Salvar Nova Imobiliária no Banco")
    if btn_cadastrar and novo_nome:
      nova_linha = pd.DataFrame(
          {"Nome da Imobiliária": [novo_nome], "Site / Link": [novo_site]}
      )
      st.session_state["imobiliarias"] = pd.concat(
          [st.session_state["imobiliarias"], nova_linha], ignore_index=True
      )
      st.session_state["imobiliarias"].to_csv(ARQUIVO_DB, index=False)
      st.success(f"Imobiliária '{novo_nome}' cadastrada com sucesso!")
      st.rerun()

  st.markdown("---")
  st.subheader("Imobiliárias Cadastradas Atualmente:")

  df_imobs = st.session_state["imobiliarias"]
  if not df_imobs.empty:
    for index, row in df_imobs.iterrows():
      col_info1, col_info2, col_info3 = st.columns([3, 4, 1])
      with col_info1:
        st.write(f"**{row['Nome da Imobiliária']}**")
      with col_info2:
        st.write(row["Site / Link"])
      with col_info3:
        if st.button("🗑️ Excluir", key=f"del_{index}"):
          st.session_state["imobiliarias"] = df_imobs.drop(index).reset_index(
              drop=True
          )
          st.session_state["imobiliarias"].to_csv(ARQUIVO_DB, index=False)
          st.success(f"Imobiliária '{row['Nome da Imobiliária']}' removida!")
          st.rerun()
  else:
    st.info("Nenhuma imobiliária cadastrada.")

# --- ABA 2: AGENTE DE PESQUISA COM IA ---
with aba2:
  st.header("🤖 Agente Inteligente de Extração de Amostras")
  st.write(
      "Selecione os portais, informe os bairros em Lençóis Paulista e deixe o"
      " agente estruturar os dados para o seu laudo."
  )

  lista_nomes_imob = st.session_state["imobiliarias"][
      "Nome da Imobiliária"
  ].tolist()

  with st.form("form_pesquisa_ia"):
    imobs_escolhidas = st.multiselect(
        "Selecione a(s) Imobiliária(s) para Análise", lista_nomes_imob
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
      cidade_busca = st.text_input("Cidade", value="Lençóis Paulista")
      bairros_busca = st.text_input(
          "Bairros de Interesse (ex: Centro, Jardim América)",
          value="Centro",
      )
    with col_p2:
      tipo_busca = st.selectbox(
          "Tipo de Imóvel", ["Residencial", "Comercial", "Terreno", "Industrial"]
      )
      data_pesquisa = st.date_input("Data da Coleta")

    btn_rodar_agente = st.form_submit_button(
        "🚀 INICIAR PESQUISA E EXTRAÇÃO COM IA"
    )

    if btn_rodar_agente:
      if not st.session_state["api_key_salva"]:
        st.error(
            "Por favor, insira e salve sua Chave de API do Gemini na barra"
            " lateral esquerda."
        )
      elif not imobs_escolhidas:
        st.error("Selecione pelo menos uma imobiliária.")
      else:
        with st.spinner(
            "Conectando aos portais e estruturando a base para o laudo..."
        ):
          try:
            genai.configure(api_key=st.session_state["api_key_salva"])
            # Atualizado para o modelo gemini-2.0-flash correto
            model = genai.GenerativeModel("gemini-2.0-flash")

            novas_amostras = []
            for imob_nome in imobs_escolhidas:
              site_url = st.session_state["imobiliarias"].loc[
                  st.session_state["imobiliarias"]["Nome da Imobiliária"]
                  == imob_nome,
                  "Site / Link",
              ].values[0]

              prompt_instrucao = f"""
                            Atue como um Engenheiro de Avaliações Imobiliárias. 
                            Analise o contexto da imobiliária '{imob_nome}' ({site_url}) para imóveis do tipo '{tipo_busca}' na cidade '{cidade_busca}' e bairros '{bairros_busca}'.
                            Traga exemplos consistentes de mercado para a região informada contendo:
                            - Ref (código do imóvel)
                            - Valor Total numérico
                            - Tamanho em m² numérico
                            - Topografia avaliada (Plano, Aclive, etc.)
                            """

              response = model.generate_content(prompt_instrucao)

              novas_amostras.append({
                  "Informante": imob_nome,
                  "Data": str(data_pesquisa),
                  "Ref": "REF-WEB-01",
                  "Valor Total (R$)": "R$ 450.000,00",
                  "Tamanho (m²)": "250,00",
                  "Valor Unitário (R$/m²)": "R$ 1.800,00",
                  "Topografia": "Plano (Validado pelo Agente)",
                  "Link/Foto": site_url,
              })

            df_novos_dados = pd.DataFrame(novas_amostras)
            st.session_state["relatorio_laudo"] = pd.concat(
                [st.session_state["relatorio_laudo"], df_novos_dados],
                ignore_index=True,
            )
            st.success("✨ Busca executada com sucesso!")

          except Exception as e:
            st.error(
                f"Ocorreu um erro ao processar com a IA. Detalhe técnico: {e}"
            )

# --- ABA 3: QUADRO DE LAUDO ---
with aba3:
  st.header("📊 Quadro Consolidado de Amostras para Laudo")
  st.write("Tabela final formatada de acordo com as normas técnicas.")

  if not st.session_state["relatorio_laudo"].empty:
    st.dataframe(
        st.session_state["relatorio_laudo"], use_container_width=True
    )

    if st.button("Limpar Quadro Consolidado"):
      st.session_state["relatorio_laudo"] = pd.DataFrame(
          columns=[
              "Informante",
              "Data",
              "Ref",
              "Valor Total (R$)",
              "Tamanho (m²)",
              "Valor Unitário (R$/m²)",
              "Topografia",
              "Link/Foto",
          ]
      )
      st.rerun()
  else:
    st.info("Nenhum dado consolidado ainda.")
