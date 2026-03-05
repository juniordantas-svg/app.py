# streamlit_app.py
import streamlit as st
import streamlit.components.v1 as components

# Título do app
st.set_page_config(page_title="Login - Cadeia de Custódia", page_icon="🔒", layout="centered")

# HTML + CSS do login
html_code = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      body {
        background-color: #f5f5f5;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        font-family: Arial, sans-serif;
      }
      .login-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        width: 350px;
        text-align: center;
      }
      h2 {
        color: #333333;
        margin-bottom: 20px;
      }
      input {
        width: 80%;
        padding: 10px;
        margin: 10px 0;
        border-radius: 6px;
        border: 1px solid #ccc;
        font-size: 14px;
      }
      button {
        width: 85%;
        padding: 12px;
        margin-top: 15px;
        border: none;
        border-radius: 6px;
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        cursor: pointer;
      }
      button:hover {
        background-color: #45a049;
      }
    </style>
  </head>
  <body>
    <div class="login-container">
      <h2>Login</h2>
      <input id="username" type="text" placeholder="Usuário"><br>
      <input id="password" type="password" placeholder="Senha"><br>
      <button onclick="login()">Entrar</button>
    </div>
    
    <script>
      function login() {
        const user = document.getElementById('username').value;
        const pass = document.getElementById('password').value;
        if(user && pass){
          alert('Bem-vindo, ' + user + '!');
        } else {
          alert('Por favor, preencha todos os campos.');
        }
      }
    </script>
  </body>
</html>
"""

# Exibir o HTML no Streamlit
components.html(html_code, height=500)
