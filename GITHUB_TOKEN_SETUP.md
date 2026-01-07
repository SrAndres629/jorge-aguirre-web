# 🔑 Guía Rápida: Token de GitHub para Render

Para conectar tu repositorio privado o descargar paquetes, Render necesita un "Personal Access Token" (Classic).

## Paso 1: Generar el Token (El "Desarrollo")

1.  **Haz clic en este enlace mágico** (te lleva directo a la configuración correcta):
    👉 [Crear Token en GitHub](https://github.com/settings/tokens/new?scopes=repo,read:packages&description=Render+Deploy+Token)

2.  En la página que se abre:
    *   **Note**: Ya dirá "Render Deploy Token".
    *   **Expiration**: Cambia "30 days" a **"No expiration"** (para que no falle el mes que viene).
    *   **Select scopes**: Las casillas `repo` y `read:packages` ya deberían estar marcadas. (Si no, márcalas).

3.  Ve al final y dale al botón verde **"Generate token"**.

4.  ⚠️ **COPIA EL TOKEN AHORA**. Empieza por `ghp_...`. GitHub no te lo volverá a mostrar.

---

## Paso 2: Registrar en Render

1.  Ve a tu Dashboard de Render.
2.  Entra en tu servicio `jorge-aguirre-web`.
3.  Ve a **Settings** -> **Registry Credential**.
4.  Haz clic en **"Add Credential"**.
5.  Rellena así:
    *   **Registry**: `GitHub Container Registry` (o `Docker Hub` si es el caso, pero para este repo es GitHub).
    *   **Username**: Tu usuario de GitHub (ej: `SrAndres629`).
    *   **Token**: Pega el código `ghp_...` que acabas de copiar.

6.  Dale a **Save**.

¡Listo! Render ya tiene llaves para entrar a tu casa. 🏠🔑
