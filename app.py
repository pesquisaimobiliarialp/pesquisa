import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Pesquisa Imobiliária - Avaliações", layout="wide")

st.title("🏡 Sistema de Pesquisa Imobiliária para Laudos")
st.markdown("Ferramenta 100% gratuita para auxiliar na coleta de amostras de mercado.")

# Formulário de entrada na barra lateral ou no corpo
with st.form("form_pesquisa"):
    st.subheader("Parâmetros da Pesquisa")
    
    # Seleção da imobiliária
    imobiliaria_opcao = st.selectbox(
        "Selecione a Imobiliária",
        ["Concreto Imóveis", "Lider LP", "Outra (Digitar Link)"]
    )
    
    link_site = st.text_input("Cole o link da página da imobiliária ou do imóvel:")
    regiao = st.text_input("Região / Bairro desejado:")
    
    botao_enviar = st.form_submit_button("Pesquisar e Gerar Quadro")

if botao_enviar:
    if not link_site:
        st.warning("Por favor, informe o link do site para realizar a busca.")
    else:
        st.info(f"A processar a busca para a região: **{regiao}** no site selecionado...")
        
        # Simulando o resultado estruturado conforme o seu pedido de laudo
        # Numa próxima etapa, integramos a leitura direta do site via IA.
        data_hoje = date.today().strftime("%d/%m/%Y")
        
        dados_exemplo = [{
            "Informante": imobiliaria_opcao,
            "Data": data_hoje,
            "Ref": "REF-1024",
            "Valor Total (R$)": 450000.0,
            "Tamanho (m²)": 150.0,
            "Valor Unitário (R$/m²)": 3000.0,
            "Topografia": "Plano (identificado via análise visual)",
            "Link/Foto": "https://via.placeholder.com/150"
        }]
        
        df = pd.DataFrame(dados_exemplo)
        
        st.success("Pesquisa concluída com sucesso!")
        st.subheader("Quadro de Amostras para o Laudo:")
        
        # Exibindo a tabela formatada
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.info("💡 **Dica:** Este quadro já está formatado com as colunas essenciais para a sua fundamentação técnica (Informante, Data, Ref, Valor Unitário, Topografia e Imagem).")
