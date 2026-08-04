import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="App de Pesquisa Imobiliária", page_icon="🏢", layout="wide"
)

st.title("🏢 Sistema de Pesquisa e Avaliação Imobiliária")
st.write(
    "Cadastre imobiliárias, faça buscas direcionadas e gere o quadro de dados para suas avaliações."
)

# Criando abas para organizar o aplicativo
aba1, aba2, aba3 = st.tabs(
    ["📥 Cadastro de Imobiliárias", "🔍 Pesquisa de Imóveis", "📊 Quadro de Laudo"]
)

# Inicializando a "memória" do aplicativo para salvar os dados temporariamente
if "imobiliarias" not in st.session_state:
    st.session_state["imobiliarias"] = pd.DataFrame(
        {
            "Nome da Imobiliária": [
                "Exemplo Imóveis",
                "Imobiliária Central",
            ],
            "Site / Link": [
                "https://www.exemploimoveis.com.br",
                "https://www.centralimoveis.com",
            ],
            "Região Padrão": ["Centro", "Zona Sul"],
        }
    )

if "resultados_pesquisa" not in st.session_state:
    st.session_state["resultados_pesquisa"] = pd.DataFrame(
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

# --- ABA 1: CADASTRO DE IMOBILIÁRIAS ---
with aba1:
    st.header("Gerenciamento de Imobiliárias")
    st.write(
        "Cadastre os sites e fontes de pesquisa que o seu aplicativo vai consultar."
    )

    with st.form("form_imobiliaria"):
        novo_nome = st.text_input("Nome da Imobiliária")
        novo_site = st.text_input("Link ou Site da Imobiliária")
        regiao_padrao = st.text_input("Região Principal de Atuação")
        submit_cad = st.form_submit_button("Cadastrar Imobiliária")

        if submit_cad and novo_nome:
            nova_linha = pd.DataFrame(
                {
                    "Nome da Imobiliária": [novo_nome],
                    "Site / Link": [novo_site],
                    "Região Padrão": [regiao_padrao],
                }
            )
            st.session_state["imobiliarias"] = pd.concat(
                [st.session_state["imobiliarias"], nova_linha], ignore_index=True
            )
            st.success(f"Imobiliária '{novo_nome}' cadastrada com sucesso!")

    st.subheader("Imobiliárias Cadastradas Atualmente:")
    st.dataframe(st.session_state["imobiliarias"], use_container_width=True)

# --- ABA 2: PESQUISA DE IMÓVEIS ---
with aba2:
    st.header("Formulário de Pesquisa de Imóvel")
    st.write("Preencha os dados coletados do imóvel para adicionar ao quadro.")

    # Pega as imobiliárias cadastradas para o menu suspenso
    lista_nomes_imob = st.session_state["imobiliarias"][
        "Nome da Imobiliária"
    ].tolist()

    with st.form("form_pesquisa"):
        col1, col2 = st.columns(2)
        with col1:
            informante = st.selectbox("Informante (Imobiliária)", lista_nomes_imob)
            data_pesquisa = st.date_input("Data da Pesquisa")
            ref_imovel = st.text_input("Ref. (Número de Publicação / Código)")
            valor_total = st.number_input(
                "Valor Total (R$)", min_value=0.0, format="%.2f"
            )

        with col2:
            tamanho = st.number_input("Tamanho / Área (m²)", min_value=0.1)
            topografia = st.selectbox(
                "Topografia (Verificada na Imagem)",
                ["Plano", "Aclive", "Declive", "Irregular", "Não identificada"],
            )
            link_foto = st.text_input("Link da Imagem ou do Anúncio")

        submit_pesq = st.form_submit_button("Adicionar Imóvel ao Quadro")

        if submit_pesq:
            if tamanho > 0:
                valor_unitario = valor_total / tamanho
            else:
                valor_unitario = 0.0

            novo_registro = pd.DataFrame(
                {
                    "Informante": [informante],
                    "Data": [str(data_pesquisa)],
                    "Ref": [ref_imovel],
                    "Valor Total (R$)": [f"R$ {valor_total:,.2f}"],
                    "Tamanho (m²)": [f"{tamanho:,.2f}"],
                    "Valor Unitário (R$/m²)": [f"R$ {valor_unitario:,.2f}"],
                    "Topografia": [topografia],
                    "Link/Foto": [link_foto],
                }
            )

            st.session_state["resultados_pesquisa"] = pd.concat(
                [st.session_state["resultados_pesquisa"], novo_registro],
                ignore_index=True,
            )
            st.success("Imóvel adicionado com sucesso ao quadro de laudo!")

# --- ABA 3: QUADRO DE LAUDO ---
with aba3:
    st.header("Quadro de Dados para Avaliação Imobiliária")
    st.write(
        "Abaixo está consolidado o quadro formatado para embasar o seu laudo técnico."
    )

    if not st.session_state["resultados_pesquisa"].empty:
        st.dataframe(
            st.session_state["resultados_pesquisa"], use_container_width=True
        )

        # Botão para limpar dados se necessário
        if st.button("Limpar Quadro de Pesquisa"):
            st.session_state["resultados_pesquisa"] = pd.DataFrame(
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
        info = st.info(
            "Nenhum imóvel cadastrado na pesquisa ainda. Vá até a aba 'Pesquisa de Imóveis' para preencher os dados."
        )
