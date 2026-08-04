from datetime import date
import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Gerador de Laudos - Pesquisa Imobiliária",
    page_icon="📋",
    layout="wide",
)

st.title("📋 Gerador de Relatórios de Pesquisa Imobiliária para Laudos")
st.write(
    "Organize suas fontes, consulte os portais de Lençóis Paulista e gere o"
    " quadro técnico idêntico ao seu modelo de laudo."
)

# Banco de dados local para persistência das imobiliárias
ARQUIVO_DB = "imobiliarias_cadastradas.csv"


def carregar_imobiliarias():
  if os.path.exists(ARQUIVO_DB):
    return pd.read_csv(ARQUIVO_DB)
  else:
    df_inicial = pd.DataFrame(
        {
            "Nome da Imobiliária": [
                "IMOBILIÁRIA TOLEDO",
                "LIDER IMOBILIÁRIA",
                "FARINA IMOBILIÁRIA",
            ],
            "Telefone": ["(14) 3263-0187", "(14) 3264-3343", "(14) 3263-0000"],
            "Site / Link": [
                "https://www.toledoimoveis.com.br",
                "https://liderlp.com.br",
                "https://www.farinaimobiliaria.com.br",
            ],
        }
    )
    df_inicial.to_csv(ARQUIVO_DB, index=False)
    return df_inicial


if "imobiliarias" not in st.session_state:
  st.session_state["imobiliarias"] = carregar_imobiliarias()

if "amostras_laudo" not in st.session_state:
  st.session_state["amostras_laudo"] = pd.DataFrame(
      columns=[
          "Amostra Nº",
          "Informante",
          "Telefone",
          "Data",
          "Bairro",
          "Tipo",
          "Ref",
          "Valor Total (R$)",
          "Área do Terreno (m²)",
          "Valor Unitário (R$/m²)",
          "Localização",
          "Topografia",
          "Link/Foto",
      ]
  )

# Abas do Aplicativo
aba1, aba2, aba3 = st.tabs(
    [
        "📥 1. Cadastro de Imobiliárias",
        "🔍 2. Painel de Pesquisa e Lançamento",
        "📄 3. Relatório Técnico (Quadro Final)",
    ]
)

# --- ABA 1: CADASTRO DE IMOBILIÁRIAS ---
with aba1:
  st.header("Cadastro Prévio de Imobiliárias")
  st.write(
      "Cadastre o nome, telefone e site das imobiliárias da cidade para ficarem"
      " salvas permanentemente."
  )

  with st.form("form_cad", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      nome_imob = st.text_input("Nome da Imobiliária (ex: IMOBILIÁRIA TOLEDO)")
    with col2:
      tel_imob = st.text_input("Telefone (ex: (14) 3263-0187)")
    with col3:
      site_imob = st.text_input("Link do Site ou Portal")

    btn_salvar_imob = st.form_submit_button("Salvar Imobiliária no Banco")
    if btn_salvar_imob and nome_imob:
      nova_linha = pd.DataFrame({
          "Nome da Imobiliária": [nome_imob.upper()],
          "Telefone": [tel_imob],
          "Site / Link": [site_imob],
      })
      st.session_state["imobiliarias"] = pd.concat(
          [st.session_state["imobiliarias"], nova_linha], ignore_index=True
      )
      st.session_state["imobiliarias"].to_csv(ARQUIVO_DB, index=False)
      st.success(f"Imobiliária '{nome_imob}' cadastrada com sucesso!")
      st.rerun()

  st.markdown("---")
  st.subheader("Imobiliárias Cadastradas Atualmente:")
  df_imobs = st.session_state["imobiliarias"]

  if not df_imobs.empty:
    for idx, row in df_imobs.iterrows():
      c_a, c_b, c_c, c_d = st.columns([3, 2, 4, 1])
      with c_a:
        st.write(f"**{row['Nome da Imobiliária']}**")
      with c_b:
        st.write(row["Telefone"])
      with c_c:
        st.write(row["Site / Link"])
      with c_d:
        if st.button("🗑️ Excluir", key=f"del_imob_{idx}"):
          st.session_state["imobiliarias"] = df_imobs.drop(idx).reset_index(
              drop=True
          )
          st.session_state["imobiliarias"].to_csv(ARQUIVO_DB, index=False)
          st.rerun()
  else:
    st.info("Nenhuma imobiliária cadastrada.")

# --- ABA 2: PAINEL DE PESQUISA E LANÇAMENTO ---
with aba2:
  st.header("🔍 Painel de Triagem e Lançamento de Amostras")
  st.write(
      "1º Escolha os parâmetros da pesquisa. O app abre os portais para você"
      " olhar e preenche o relatório abaixo com cálculo automático."
  )

  df_imobs = st.session_state["imobiliarias"]
  nomes_imobs_lista = (
      df_imobs["Nome da Imobiliária"].tolist()
      if not df_imobs.empty
      else ["Cadastre imobiliárias na Aba 1"]
  )

  # Seção de Atalhos de Consulta Rápida
  if not df_imobs.empty:
    st.markdown("### 🌐 Atalhos Rápidos para Acessar os Portais:")
    cols_links = st.columns(len(df_imobs))
    for i, row in df_imobs.iterrows():
      link = row["Site / Link"]
      if link and not link.startswith("http"):
        link = "https://" + link
      with cols_links[i % len(cols_links)]:
        st.markdown(f"👉 **[{row['Nome da Imobiliária']}]({link})**")

  st.markdown("---")
  st.subheader("📝 Lançamento da Amostra Encontrada")

  with st.form("form_amostra", clear_on_submit=False):
    col_f1, col_f2 = st.columns(2)

    with col_f1:
      # Número automático da amostra sequencial
      num_amostra = len(st.session_state["amostras_laudo"]) + 1
      st.markdown(f"### 📍 Amostra Número: **{num_amostra}**")

      informante_escolhido = st.selectbox(
          "Informante (Imobiliária)", nomes_imobs_lista
      )
      data_pesq = st.date_input("Data da Pesquisa")
      bairro_informado = st.text_input(
          "Bairro / Região (ex: Jardim Europa)", value="Jardim Europa"
      )
      tipo_uso = st.selectbox(
          "Tipo de Imóvel", ["Terreno", "Residencial", "Comercial", "Industrial"]
      )
      ref_pub = st.text_input("Ref. (Nº de publicação no site, ex: 14538)")

    with col_f2:
      valor_total_in = st.number_input(
          "Valor Total (R$)", min_value=0.0, format="%.2f", value=210000.00
      )
      area_terreno_in = st.number_input(
          "Área do Terreno / Imóvel (m²)",
          min_value=0.1,
          format="%.2f",
          value=200.00,
      )
      localizacao_det = st.text_input(
          "Localização (ex: Esquina, Meio de quadra)"
      )
      topografia_in = st.selectbox(
          "Topografia", ["Plana", "Aclive", "Declive", "Irregular"]
      )
      link_foto_in = st.text_input("Link da Imagem ou URL do Anúncio")

    btn_adicionar_amostra = st.form_submit_button(
        "➕ Adicionar Amostra ao Relatório do Laudo"
    )

    if btn_adicionar_amostra:
      if informante_escolhido == "Cadastre imobiliárias na Aba 1":
        st.error("Cadastre uma imobiliária antes de registrar.")
      else:
        # Busca o telefone correspondente no banco de dados cadastrado
        tel_encontrado = ""
        if not df_imobs.empty:
          match_tel = df_imobs.loc[
              df_imobs["Nome da Imobiliária"] == informante_escolhido,
              "Telefone",
          ]
          if not match_tel.empty:
            tel_encontrado = match_tel.values[0]

        # Cálculo automático exato do Valor Unitário exigido pelo laudo
        val_unitario = (
            (valor_total_in / area_terreno_in)
            if area_terreno_in and area_terreno_in > 0
            else 0.0
        )

        nova_amostra_df = pd.DataFrame({
            "Amostra Nº": [num_amostra],
            "Informante": [informante_escolhido],
            "Telefone": [tel_encontrado],
            "Data": [str(data_pesq)],
            "Bairro": [bairro_informado],
            "Tipo": [tipo_uso],
            "Ref": [ref_pub],
            "Valor Total (R$)": [f"R$ {valor_total_in:,.2f}"],
            "Área do Terreno (m²)": [f"{area_terreno_in:,.2f}"],
            "Valor Unitário (R$/m²)": [f"R$ {val_unitario:,.2f}"],
            "Localização": [localizacao_det],
            "Topografia": [topografia_in],
            "Link/Foto": [link_foto_in],
        })

        st.session_state["amostras_laudo"] = pd.concat(
            [st.session_state["amostras_laudo"], nova_amostra_df],
            ignore_index=True,
        )
        st.success(
            f"Amostra {num_amostra} adicionada com sucesso ao relatório técnico!"
        )

# --- ABA 3: RELATÓRIO TÉCNICO (QUADRO FINAL IDÊNTICO AO PDF) ---
with aba3:
  st.header("📄 Quadro Técnico Consolidado para Impressão no Laudo")
  st.write(
      "Abaixo está o relatório estruturado exatamente com os campos exigidos"
      " em suas avaliações imobiliárias."
  )

  df_relatorio = st.session_state["amostras_laudo"]

  if not df_relatorio.empty:
    st.dataframe(df_relatorio, use_container_width=True)

    st.markdown("---")
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
      if st.button("🗑️ Limpar Todas as Amostras"):
        st.session_state["amostras_laudo"] = pd.DataFrame(
            columns=[
                "Amostra Nº",
                "Informante",
                "Telefone",
                "Data",
                "Bairro",
                "Tipo",
                "Ref",
                "Valor Total (R$)",
                "Área do Terreno (m²)",
                "Valor Unitário (R$/m²)",
                "Localização",
                "Topografia",
                "Link/Foto",
            ]
        )
        st.rerun()
    with col_opt2:
      st.info(
          "💡 **Dica:** Você pode selecionar a tabela acima, copiar e colar"
          " direto no seu editor de texto ou imprimir a página para anexar ao"
          " laudo."
      )
  else:
    st.info(
        "Nenhuma amostra lançada ainda. Utilize a **Aba 2** para consultar os"
        " portais e registrar as amostras de mercado."
    )
