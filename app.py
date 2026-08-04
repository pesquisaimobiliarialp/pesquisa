import os
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="App de Pesquisa Imobiliária", page_icon="🏢", layout="wide"
)

st.title("🏢 Sistema de Pesquisa e Avaliação Imobiliária")
st.write(
    "Gerencie imobiliárias com salvamento automático, filtre por bairros e tipologia em Lençóis Paulista e acesse os portais para o laudo."
)

# Criando abas para organizar o aplicativo
aba1, aba2, aba3 = st.tabs(
    [
        "📥 Cadastro de Imobiliárias",
        "🔍 Pesquisa nos Portais",
        "📊 Quadro de Laudo (Resultados)",
    ]
)

# Nome do arquivo para persistência (Banco de dados simples e gratuito)
ARQUIVO_DB = "imobiliarias_cadastradas.csv"


# Função para carregar imobiliárias salvas
def carregar_imobiliarias():
    if os.path.exists(ARQUIVO_DB):
        return pd.read_csv(ARQUIVO_DB)
    else:
        # Padrão inicial caso o arquivo não exista
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


# Inicializando banco de dados de imobiliárias
if "imobiliarias" not in st.session_state:
    st.session_state["imobiliarias"] = carregar_imobiliarias()

if "resultados_pesquisa" not in st.session_state:
    st.session_state["resultados_pesquisa"] = pd.DataFrame(
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

# --- ABA 1: CADASTRO DE IMOBILIÁRIAS (Com Banco de Dados) ---
with aba1:
    st.header("Gerenciamento e Banco de Dados de Imobiliárias")
    st.write(
        "As imobiliárias cadastradas aqui ficam salvas automaticamente para não perder as informações."
    )

    with st.form("form_imobiliaria", clear_on_submit=True):
        novo_nome = st.text_input("Nome da Imobiliária")
        novo_site = st.text_input(
            "Link ou Site da Imobiliária (ex: https://...)"
        )
        submit_cad = st.form_submit_button("Cadastrar e Salvar no Banco")

        if submit_cad and novo_nome:
            nova_linha = pd.DataFrame(
                {
                    "Nome da Imobiliária": [novo_nome],
                    "Site / Link": [novo_site],
                }
            )
            st.session_state["imobiliarias"] = pd.concat(
                [st.session_state["imobiliarias"], nova_linha], ignore_index=True
            )
            # Salva no arquivo CSV local do servidor/GitHub
            st.session_state["imobiliarias"].to_csv(ARQUIVO_DB, index=False)
            st.success(
                f"Imobiliária '{novo_nome}' salva com sucesso no banco de dados!"
            )

    st.subheader("Imobiliárias Cadastradas Atualmente:")
    st.dataframe(st.session_state["imobiliarias"], use_container_width=True)

# --- ABA 2: PESQUISA NOS PORTAIS ---
with aba2:
    st.header("🔍 Pesquisa Direta nos Sites das Imobiliárias")
    st.write(
        "Selecione as imobiliárias, informe a cidade, digite os bairros de interesse e escolha a tipologia do imóvel."
    )

    df_imobs = st.session_state["imobiliarias"]
    lista_nomes_imob = df_imobs["Nome da Imobiliária"].tolist()

    with st.form("form_pesquisa"):
        imobiliarias_selecionadas = st.multiselect(
            "1. Selecione a(s) Imobiliária(s) para Consulta", lista_nomes_imob
        )

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            cidade = st.text_input("Cidade", value="Lençóis Paulista")
            bairros_informados = st.text_input(
                "2. Bairros (Digite separados por vírgula, ex: Centro, Jardim América)"
            )

        with col_p2:
            tipo_imovel = st.selectbox(
                "3. Tipo de Imóvel",
                ["Residencial", "Comercial", "Terreno", "Industrial"],
            )
            data_pesquisa = st.date_input("Data da Pesquisa")

        st.markdown("---")
        # Botão de Start na Pesquisa
        submit_start = st.form_submit_button(
            "🚀 INICIAR PESQUISA NOS SITES SELECIONADOS"
        )

        if submit_start:
            if not imobiliarias_selecionadas:
                st.error(
                    "Por favor, selecione pelo menos uma imobiliária acima antes de iniciar."
                )
            else:
                st.success(
                    f"Parâmetros definidos para **{cidade}** ({bairros_informados or 'Geral'}) | Tipo: **{tipo_imovel}**."
                )

    # Exibição dos links rápidos dos sites selecionados para você navegar e coletar os dados para o laudo
    if imobiliarias_selecionadas:
        st.subheader(
            "🔗 Portais Prontos para Acesso (Clique para abrir o site e pesquisar):"
        )
        for nome_imob in imobiliarias_selecionadas:
            site_encontrado = df_imobs.loc[
                df_imobs["Nome da Imobiliária"] == nome_imob, "Site / Link"
            ].values
            if len(site_encontrado) > 0 and site_encontrado[0]:
                link = site_encontrado[0]
                if not link.startswith("http"):
                    link = "https://" + link
                st.markdown(
                    f"- 🌐 **[{nome_imob}]({link})** — *Abra o link para buscar imóveis do tipo {tipo_imovel} nos bairros informados.*"
                )
            else:
                st.warning(
                    f"A imobiliária '{nome_imob}' não possui um link cadastrado na aba de Cadastro."
                )

# --- ABA 3: QUADRO DE LAUDO ---
with aba3:
    st.header("📊 Quadro Consolidado para Laudo de Avaliação")
    st.write(
        "Visualize e gerencie os dados coletados durante as pesquisas nos portais para estruturar o seu laudo."
    )

    if not st.session_state["resultados_pesquisa"].empty:
        filtro_tipo_quadro = st.selectbox(
            "Filtrar por Tipo no Quadro:",
            ["Todos", "Residencial", "Comercial", "Terreno", "Industrial"],
        )

        df_exibir = st.session_state["resultados_pesquisa"]
        if filtro_tipo_quadro != "Todos":
            df_exibir = df_exibir[df_exibir["Tipo"] == filtro_tipo_quadro]

        st.dataframe(df_exibir, use_container_width=True)

        if st.button("Limpar Quadro Consolidado"):
            st.session_state["resultados_pesquisa"] = pd.DataFrame(
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
            "O quadro está vazio no momento. Utilize a aba de pesquisa para abrir os portais e estruturar sua coleta."
        )
