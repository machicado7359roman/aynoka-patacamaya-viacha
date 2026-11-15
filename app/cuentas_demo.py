"""Cuentas locales de demostración; sin correo verificado ni vínculo con el APK."""
import hashlib
import hmac
import os
import re
import sqlite3
import time
from pathlib import Path
import streamlit as st

RUTA = Path(__file__).resolve().parents[1] / ".local" / "cuentas_demo.sqlite3"

def conexion(ruta=RUTA):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(ruta, timeout=10)
    db.execute("CREATE TABLE IF NOT EXISTS cuentas (correo TEXT PRIMARY KEY, nombre TEXT NOT NULL, sal BLOB NOT NULL, clave BLOB NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS intentos (correo TEXT PRIMARY KEY, fallos INTEGER NOT NULL, bloqueo REAL NOT NULL)")
    return db

def derivar(clave, sal):
    return hashlib.scrypt(clave.encode(),salt=sal,n=16384,r=8,p=1,dklen=32)

def registrar(nombre, correo, clave, ruta=RUTA):
    nombre=nombre.strip();correo=correo.strip().lower()
    if not 2 <= len(nombre) <= 80:
        raise ValueError("Escribe un nombre de 2 a 80 caracteres.")
    if len(correo)>254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",correo):
        raise ValueError("Revisa el formato del correo.")
    if not 10 <= len(clave) <= 128:
        raise ValueError("Usa una contraseña de 10 a 128 caracteres para esta demo.")
    sal=os.urandom(16)
    db=conexion(ruta)
    try:
        with db:
            db.execute("INSERT INTO cuentas VALUES (?,?,?,?)",(correo,nombre,sal,derivar(clave,sal)))
    except sqlite3.IntegrityError:
        raise ValueError("Ese correo ya tiene una cuenta local. Prueba Iniciar sesión.") from None
    finally:
        db.close()

def autenticar(correo, clave, ruta=RUTA):
    correo=correo.strip().lower()
    if len(correo)>254 or len(clave)>128:
        raise ValueError("Correo o contraseña incorrectos.")
    db=conexion(ruta)
    try:
        intento=db.execute("SELECT fallos,bloqueo FROM intentos WHERE correo=?",(correo,)).fetchone()
        if intento and intento[1]>time.time():
            raise ValueError("Demasiados intentos. Espera cinco minutos antes de volver a probar.")
        cuenta=db.execute("SELECT nombre,sal,clave FROM cuentas WHERE correo=?",(correo,)).fetchone()
        calculada=derivar(clave,cuenta[1] if cuenta else bytes(16))
        if not cuenta or not hmac.compare_digest(calculada,cuenta[2]):
            fallos=(intento[0] if intento and intento[1]==0 else 0)+1
            with db:
                db.execute("INSERT OR REPLACE INTO intentos VALUES (?,?,?)",(correo,fallos,time.time()+300 if fallos>=5 else 0))
            raise ValueError("Correo o contraseña incorrectos.")
        with db: db.execute("DELETE FROM intentos WHERE correo=?",(correo,))
        return {"nombre":cuenta[0],"correo":correo}
    finally:
        db.close()

def mostrar_cuentas_demo():
    st.caption("CUENTA DE PRUEBA · Correo sin verificar · Cuenta independiente del APK")
    st.write("Crea una cuenta de prueba para entrar en esta web. Usa una contraseña exclusiva para la demo. Los datos se guardan en el servidor y pueden perderse si se reinicia.")
    usuario=st.session_state.get("usuario_demo")
    if usuario:
        st.success("Sesión iniciada: "+usuario["nombre"])
        st.caption(usuario["correo"]+" · Cuenta local de demostración")
        if st.button("Cerrar sesión",key="salir_demo"):
            st.session_state.pop("usuario_demo",None);st.rerun()
        return
    registro, acceso=st.tabs(["Crear cuenta", "Iniciar sesión"])
    with registro:
        if st.session_state.pop("alta_demo_ok",False):
            st.success("Cuenta creada. Ya puedes iniciar sesión con tus datos.")
        with st.form("alta_demo",clear_on_submit=True):
            nombre=st.text_input("Nombre",max_chars=80)
            correo=st.text_input("Correo de la cuenta",max_chars=254)
            clave=st.text_input("Contraseña para la demo",type="password",max_chars=128)
            confirmar=st.text_input("Repetir contraseña",type="password",max_chars=128)
            acepta=st.checkbox("Entiendo que es una cuenta local de prueba, sin verificación de correo.")
            enviar=st.form_submit_button("Crear mi cuenta de prueba")
        if enviar:
            try:
                if not acepta: raise ValueError("Confirma que entiendes el alcance de la demo.")
                if clave!=confirmar: raise ValueError("Las contraseñas no coinciden.")
                registrar(nombre,correo,clave)
            except ValueError as error: st.error(str(error))
            else:
                st.session_state.alta_demo_ok=True;st.rerun()
    with acceso:
        with st.form("acceso_demo",clear_on_submit=True):
            correo=st.text_input("Correo",max_chars=254)
            clave=st.text_input("Contraseña",type="password",max_chars=128)
            entrar=st.form_submit_button("Iniciar sesión")
        if entrar:
            try: usuario=autenticar(correo,clave)
            except ValueError as error: st.error(str(error))
            else:
                st.session_state.usuario_demo=usuario;st.rerun()
    st.caption("Sin recuperación de contraseña por correo en esta demo. La cuenta no guarda todavía parcelas ni recomendaciones.")
