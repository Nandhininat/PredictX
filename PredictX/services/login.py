import streamlit as st
from services.auth_service import register_user, login_user


def show_login():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">🏭 PredictX</div>
        <div class="login-subtitle">
            Intelligent Predictive Maintenance & Asset Health Monitoring
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])

    with center:
        login_tab, register_tab = st.tabs(["🔐 Login", "📝 Register"])

        with login_tab:
            st.subheader("Welcome Back")

            email = st.text_input("Email", key="login_email")
            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button(
                "🔐 Login",
                use_container_width=True,
                key="login_button"
            ):
                if not email.strip() or not password:
                    st.warning("Please enter email and password.")
                else:
                    user = login_user(email, password)

                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user[0]
                        st.session_state.user_name = user[1]
                        st.session_state.user_role = user[3]
                        st.session_state.page = "Dashboard"
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with register_tab:
            st.subheader("Create Account")

            name = st.text_input("Name", key="register_name")
            email = st.text_input("Email", key="register_email")
            password = st.text_input(
                "Password",
                type="password",
                key="register_password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                key="register_confirm_password"
            )

            if st.button(
                "📝 Create Account",
                use_container_width=True,
                key="register_button"
            ):
                if not name.strip() or not email.strip() or not password:
                    st.warning("Please fill all fields.")
                elif password != confirm_password:
                    st.warning("Passwords do not match.")
                elif len(password) < 6:
                    st.warning("Password must contain at least 6 characters.")
                else:
                    result = register_user(name, email, password)

                    if result:
                        # DO NOT reset register_name/register_email/etc.
                        # after creating the widgets. Streamlit owns widget keys.
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Email already exists.")
