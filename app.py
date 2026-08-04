from datetime import date
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Sistema de Avaliação Imobiliária", page_icon="🏢", layout="wide"
)

st.title("🏢 Sistema de Organização e Quadro para Laudos Imobiliários")
st.write(
    "Gerencie suas fontes, consulte portais e consolide de forma limpa e"
    " estável as amostras para as suas avaliações."
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
          "Cidade",
          "Bairro",
          "Tipo",
          "Ref",
          "Valor Total (R$)",
          "Tamanho (m²)",
          "Valor Unitário (R$/m²)",
          "Topografia",
          "Link/Foto",
      ]
  )

# --- ABAS DO APLICATIVO ---
aba1, aba2, aba3 = st.tabs(
    [
        "📥 Cadastro de Imobiliárias",
        "🔍 Consulta e Registro de Amostras",
        "📊 Quadro Consolidado (Laudo)",
    ]
)

# --- ABA 1: CADASTRO E EXCLUSÃO DE IMOBILIÁRIAS ---
with aba1:
  st.header("Gerenciamento do Banco de Dados de Imobiliárias")
  st.write(
      "Cadastre novas fontes de pesquisa ou remova as que não utiliza mais."
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
      st.success(f"Imobiliária '{novo_nome}' cadastrada e salva com sucesso!")
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

# --- ABA 2: CONSULTA AOS PORTAIS E REGISTRO DE DADOS ---
with aba2:
  st.header("🔍 Acesso Rápido aos Portais e Registro de Amostras")
  st.write(
      "Abra os portais cadastrados para pesquisa visual e preencha os dados"
      " coletados para o laudo."
  )

  df_imobs = st.session_state["imobiliarias"]
  lista_nomes_imob = df_imobs["Nome da Imobiliária"].tolist()

  if not df_imobs.empty:
    st.subheader(
        "🌐 Atalhos para Consulta Direta nos Sites (Clique para abrir):"
    )
    for index, row in df_imobs.iterrows():
      link = row["Site / Link"]
      if link and not link.startswith("http"):
        link = "https://" + link
      st.markdown(
          f"- 🔗 **[{row['Nome da Imobiliária']}]({link})** — *Abrir portal"
          " para verificar ofertas.*"
      )

  st.markdown("---")
  st.subheader("📝 Registrar Amostra Encontrada na Pesquisa")

  with st.form("form_registro_amostra", clear_on_submit=False):
    col_r1, col_r2 = st.columns(2)

    with col_r1:
      informante = st.selectbox(
          "Informante (Imobiliária de Origem)",
          (
              lista_nomes_imob
              if lista_nomes_imob
              else ["Cadastre uma imobiliária na Aba 1"]
          ),
      )
      data_pesquisa = st.date_input("Data da Coleta")
      cidade = st.text_input("Cidade", value="Lençóis Paulista")
      bairro = st.text_input("Bairro")
      tipo_imovel = st.selectbox(
          "Tipo de Imóvel", ["Residencial", "Comercial", "Terreno", "Industrial"]
      )

    with col_r2:
      ref_imovel = st.text_input("Ref. (Código do imóvel no site)")
      valor_total = st.number_input(
          "Valor Total (R$)", min_value=0.0, format="%.2f"
      )
      tamanho = st.number_input(
          "Tamanho / Área (m²)", min_value=0.1, format="%.2f"
      )
      topografia = st.selectbox(
          "Topografia (Verificada na Imagem)",
          ["Plano", "Aclive", "Declive", "Irregular", "Não identificada"],
      )
      link_foto = st.text_input("Link da Imagem ou URL do Anúncio")

    btn_adicionar = st.form_submit_button(
        "➕ Adicionar Imóvel ao Quadro de Laudo"
    )

    if btn_adicionar:
      if informante == "Cadastre uma imobiliária na Aba 1":
        st.error(
            "Cadastre pelo menos uma imobiliária antes de registrar amostras."
        )
      else:
        # Cálculo técnico automático do Valor Unitário
        valor_unitario = (
            (valor_total / tamanho) if tamanho and tamanho > 0 else 0.0
        )

        nova_amostra = pd.DataFrame({
            "Informante": [informante],
            "Data": [str(data_pesquisa)],
            "Cidade": [cidade],
            "Bairro": [bairro],
            "Tipo": [tipo_imovel],
            "Ref": [ref_imovel],
            "Valor Total (R$)": [f"R$ {valor_total:,.2f}"],
            "Tamanho (m²)": [f"{tamanho:,.2f}"],
            "Valor Unitário (R$/m²)": [f"R$ {valor_unitario:,.2f}"],
            "Topografia": [topografia],
            "Link/Foto": [link_foto],
        })

        st.session_state["relatorio_laudo"] = pd.concat(
            [st.session_state["relatorio_laudo"], nova_amostra],
            ignore_index=True,
        )
        st.success("Imóvel adicionado com sucesso ao quadro de laudo!")

# --- ABA 3: QUADRO CONSOLIDADO PARA LAUDO ---
with aba3:
  st.header("📊 Quadro Consolidado de Amostras para Laudo")
  st.write(
      "Abaixo estão consolidados os dados estruturados para fundamentar a sua"
      " avaliação imobiliária."
  )

  if not st.session_state["relatorio_laudo"].empty:
    # Filtros visuais dinâmicos para facilitar a análise
    col_f1, col_f2 = st.columns(2)
    with col_f1:
      filtro_tipo = st.selectbox(
          "Filtrar por Tipo:",
          ["Todos", "Residencial", "Comercial", "Terreno", "Industrial"],
      )
    with col_f2:
      lista_infs = ["Todos"] + st.session_state["relatorio_laudo"][
          "Informante"
      ].unique().tolist()
      filtro_inf = st.selectbox("Filtrar por Imobiliária:", lista_infs)

    df_exibir = st.session_state["relatorio_laudo"]
    if filtro_tipo != "Todos":
      df_exibir = df_exibir[df_exibir["Tipo"] == filtro_tipo]
    if filtro_inf != "Todos":
      df_exibir = df_exibir[df_exibir["Informante"] == filtro_inf]

    st.dataframe(df_exibir, use_container_width=True)

    if st.button("Limpar Quadro Consolidado"):
      st.session_state["relatorio_laudo"] = pd.DataFrame(
          columns=[
              "Informante",
              "Data",
              "Cidade",
              "Bairro",
              "Tipo",
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
    st.info(
        "Nenhum imóvel registrado no quadro ainda. Vá até a Aba 2 para consultar"
        " os portais e registrar as amostras."
    )
