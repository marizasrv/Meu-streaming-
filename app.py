if checkout_url:
    st.markdown(
        f"""
        <a href="{checkout_url}" target="_blank" rel="noopener noreferrer"
           style="
               display:flex;
               align-items:center;
               justify-content:center;
               width:100%;
               min-height:62px;
               box-sizing:border-box;
               padding:0.75rem 1rem;
               border-radius:16px;
               border:2px solid #f2d675;
               background:linear-gradient(90deg, #6d28d9, #8b5cf6);
               color:#ffffff;
               font-size:1.22rem;
               font-weight:800;
               text-decoration:none;
               text-align:center;
           ">
            💳 Assinar Premium — R$ 30/mês
        </a>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "A Kiwify abrirá em outra aba. "
        "Depois do pagamento, volte para esta aba e toque em "
        "'Já paguei — atualizar meu plano'."
    )
