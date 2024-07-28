import streamlit as st

def main():
    # Muestra un mensaje en la aplicación
    st.title("Detección de cierre del navegador")
    st.write("Cierra el navegador para ver el mensaje de cierre.")

    # Variable de entrada para detectar cambios
    key = st.empty()

    # Verifica si se ha cerrado el navegador
    if key.button("Detectar cierre"):
        st.success("El navegador se ha cerrado.")

    # Ejecuta la función nuevamente para detectar cambios en la variable de entrada
    st.experimental_rerun()

if __name__ == "__main__":
    main()