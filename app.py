# app.py ─────────────────────────────────────────────────────────
import streamlit as st
import json
from classifier import clasificar_tarea, clasificar_varias_tareas

# Diccionarios para mostrar etiquetas bonitas
CUADRANTE = {
    "I":  "🔴 Cuadrante I - Urgente e Importante",
    "II": "🟦 Cuadrante II - No urgente pero Importante",
    "III":"🟨 Cuadrante III - Urgente pero No importante",
    "IV": "⚫ Cuadrante IV - No urgente ni importante"
}
ENERGIA = {
    "Alta concentración":      "💡 Alta concentración",
    "Automática o repetitiva": "🔁 Repetitiva o automática",
    "Creativa o estratégica":  "🎨 Creativa o estratégica"
}

# ─── Configuración de página ───────────────────────────────────
st.set_page_config(page_title="Clasificador Eisenhower", page_icon="🧠")
st.title("🧠 Clasificador de Tareas")

# Selector para una o varias tareas
modo_multiple = st.toggle("Ingresar varias tareas (una por línea)")

# Campo de texto
texto = st.text_area("✍️ Escribe tu tarea(s):")

# ─── Botón único con key ───────────────────────────────────────
clicked = st.button("Clasificar", key="btn_clasificar")

if clicked:
    if not texto.strip():
        st.warning("⚠️ Escribe al menos una tarea.")
    else:
        with st.spinner("Analizando..."):
            if modo_multiple:
                resultados = clasificar_varias_tareas(texto)
            else:
                r = clasificar_tarea(texto)
                resultados = [{"tarea": texto, **r}]

        st.success("✅ Clasificación completada")

        for res in resultados:
            if "error" in res:
                st.error(f"❌ Error con «{res['tarea']}»: {res['error']}")
                continue

            st.markdown("---")
            # st.markdown(f"**📝 Tarea:** {res['tarea']}")
            st.markdown(f"**🧩 Cuadrante:** {CUADRANTE.get(res['cuadrante'], res['cuadrante'])}")
            st.markdown(f"**📌 Justificación:** {res['justificacion']}")
            st.markdown(f"**🛠️ Recomendación:** {res['recomendacion']}")
            st.markdown(f"**⚡ Energía:** {ENERGIA.get(res['energia'], res['energia'])}")
            st.markdown(f"**📆 Bloque:** `{res['bloque_sugerido']}`")
            st.markdown(f"**⏱️ Duración estimada:** {res['duracion_estimada']} min")
            # Mostrar subtareas si existen
            if res.get("subtareas"):
                st.markdown("**🪄 Subtareas sugeridas:**")
                for idx, sub in enumerate(res["subtareas"], 1):
                    st.markdown(f"- {idx}. {sub['descripcion']} — ⏱️ {sub['duracion']} min")



        # Botón de descarga del JSON de todos los resultados
        st.download_button(
            label="⬇️ Descargar resultados en JSON",
            data=json.dumps(resultados, ensure_ascii=False, indent=2),
            file_name="clasificacion_tareas.json",
            mime="application/json",
            key="btn_descarga"
        )
