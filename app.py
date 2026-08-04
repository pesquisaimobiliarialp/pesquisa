from datetime import date
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="App de Pesquisa Imobiliária", page_icon="🏢", layout="wide"
)

st.title("🏢 Sistema de Pesquisa e Avaliação Imobiliária")
st.write(
    "Gerencie imobiliárias, filtre por bairros e tipo em Lençóis Paulista, e consolide o quadro técnico para laudos."
)

# Criando abas para organizar o aplicativo
aba1, aba2, aba3 = st.tabs(
    ["📥 Cadastro de Imobiliárias", "🔍 Pesquisa de Imóveis", "📊 Quadro de Laudo"]
)

# Inicializando a "memória" do aplicativo (banco de dados temporário)
if "imobiliarias" not in st.session_state:
    st.session_state["imobiliarias"] = pd.DataFrame(
        {
            "Nome da Imobiliária": ["Concreto Imóveis", "Lider LP"],
            "Site / Link": [
                "https://www.concretoimoveis.com.br",
                "https://liderlp.com.br",
            ],
        }
    )

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

# --- ABA 1: CADASTRO DE IMOBILIÁRIAS ---
with aba1:
    st.header("Gerenciamento de Imobiliárias")
    st.write(
        "Cadastre os sites e fontes de pesquisa que o seu aplicativo vai consultar."
    )

    with st.form("form_imobiliaria"):
        novo_nome = st.text_input("Nome da Imobiliária")
        novo_site = st.text_input("Link ou Site da Imobiliária")
        submit_cad = st.form_submit_button("Cadastrar Imobiliária")

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
            st.success(f"Imobiliária '{novo_nome}' cadastrada com sucesso!")

    st.subheader("Imobiliárias Cadastradas Atualmente:")
    st.dataframe(st.session_state["imobiliarias"], use_container_width=True)

# --- ABA 2: PESQUISA DE IMÓVEIS ---
with aba2:
    st.header("Filtros e Coleta de Imóveis")
    st.write(
        "Defina os filtros de busca e adicione os imóveis encontrados por imobiliária."
    )

    lista_nomes_imob = st.session_state["imobiliarias"][
        "Nome da Imobiliária"
    ].tolist()

    with st.form("form_pesquisa"):
        st.subheader("1. Critérios de Busca")
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            imobiliarias_selecionadas = st.multiselect(
                "Selecionar Imobiliárias para a Consulta", lista_nomes_imob
            )
            cidade = st.text_input("Cidade (Fixa)", value="Lençóis Paulista")

        with col_f2:
            bairros_opcoes = [
                "Centro",
                "Jardim Carolina",
                "Vila Irineu",
                "Jardim América",
                "Parque Residencial",
                "Vila Nova",
                "Outro",
            ]
            bairros_selecionados = st.multiselect(
                "Bairros (Selecione um ou mais)", bairros_opcoes
            )
            tipo_imovel = st.selectbox(
                "Tipo de Imóvel", ["Terreno", "Casa", "Comercial", "Industrial"]
            )

        st.markdown("---")
        st.subheader("2. Registrar Imóvel Encontrado")
        col1, col2 = st.columns(2)

        with col1:
            informante_atual = st.selectbox(
                "Imobiliária de Origem deste Imóvel",
                (
                    imobiliarias_selecionadas
                    if imobiliarias_selecionadas
                    else ["Selecione imobiliárias acima primeiro"]
                ),
            )
            data_pesquisa = st.date_input("Data da Pesquisa")
            bairro_especifico = st.text_input(
                "Bairro do Imóvel (ou confirme a seleção dos filtros)"
            )
            ref_imovel = st.text_input("Ref. (Número de Publicação / Código)")

        with col2:
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
            link_foto = st.text_input("Link da Imagem ou do Anúncio")

        submit_pesq = st.form_submit_button(
            "Adicionar Imóvel ao Quadro Consolidado"
        )

        if submit_pesq:
            if not imobiliarias_selecionadas:
                st.error(
                    "Selecione pelo menos uma imobiliária no topo da pesquisa."
                )
            elif (
                informante_atual
                == "Selecione imobiliárias acima primeiro"
            ):
                st.error("Escolha a imobiliária de origem válida para o imóvel.")
            else:
                if tamanho > 0:
                    valor_unitario = valor_total / tamanho
                else:
                    valor_unitario = 0.0

                bairro_final = (
                    bairro_especifico
                    if bairro_especifico
                    else (
                        ", ".join(bairros_selecionados)
                        if bairros_selecionados
                        else "Geral"
                    )
                )

                novo_registro = pd.DataFrame(
                    {
                        "Informante": [informante_atual],
                        "Data": [str(data_pesquisa)],
                        "Cidade": [cidade],
                        "Bairro": [bairro_final],
                        "Tipo": [tipo_imovel],
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
                st.success(
                    "Imóvel adicionado com sucesso ao quadro de laudo!"
                )

# --- ABA 3: QUADRO DE LAUDO ---
with aba3:
    st.header("📊 Quadro Consolidado para Avaliação Imobiliária")
    st.write(
        "Abaixo estão listados todos os imóveis cadastrados que atendem aos critérios das imobiliárias e filtros selecionados."
    )

    if not st.session_state["resultados_pesquisa"].empty:
        # Filtros interativos para visualização no quadro
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            filtro_tipo = st.selectbox(
                "Filtrar por Tipo no Quadro:",
                ["Todos", "Terreno", "Casa", "Comercial", "Industrial"],
            )
        with col_m2:
            imobs_disponiveis = [
                "Todas"
            ] + st.session_state["resultados_pesquisa"][
                "Informante"
            ].unique().tolist()
            filtro_imob = st.selectbox(
                "Filtrar por Imobiliária (Informante):", imobs_disponiveis
            )

        df_exibir = st.session_state["resultados_pesquisa"]

        if filtro_tipo != "Todos":
            df_exibir = df_exibir[df_exibir["Tipo"] == filtro_tipo]

        if filtro_imob != "Todas":
            df_exibir = df_exibir[df_exibir["Informante"] == filtro_imob]

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
            "Nenhum imóvel registrado ainda. Vá até a aba 'Pesquisa de Imóveis' para cadastrar os dados coletados."
        )
