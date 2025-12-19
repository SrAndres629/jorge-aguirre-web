"""
CONVERT_IMAGES.PY
=================
Script para convertir todas las imágenes JPG/PNG a formato WebP.
WebP es hasta 90% más liviano que JPG con la misma calidad.

USO:
    python convert_images.py

REQUISITOS:
    pip install pillow
"""

from PIL import Image
import os
from pathlib import Path

# Carpeta donde están las imágenes
IMAGES_FOLDER = Path("static/images")

# Calidad de compresión (80-90 es óptimo para web)
QUALITY = 85

def convert_to_webp():
    """Convierte todas las imágenes JPG/PNG a WebP"""
    
    if not IMAGES_FOLDER.exists():
        print(f"❌ Error: La carpeta {IMAGES_FOLDER} no existe")
        return
    
    # Extensiones a convertir
    extensions = ('.jpg', '.jpeg', '.png')
    
    converted = 0
    saved_kb = 0
    
    print("🔄 Buscando imágenes para convertir...")
    print("-" * 50)
    
    for image_path in IMAGES_FOLDER.iterdir():
        if image_path.suffix.lower() in extensions:
            # Tamaño original
            original_size = image_path.stat().st_size / 1024  # KB
            
            # Nombre del archivo WebP
            webp_path = image_path.with_suffix('.webp')
            
            try:
                # Abrir y convertir
                with Image.open(image_path) as img:
                    # Convertir a RGB si es necesario (PNG con transparencia)
                    if img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')
                    
                    # Guardar como WebP
                    img.save(webp_path, 'WEBP', quality=QUALITY, optimize=True)
                
                # Tamaño nuevo
                new_size = webp_path.stat().st_size / 1024  # KB
                savings = original_size - new_size
                
                print(f"✅ {image_path.name}")
                print(f"   {original_size:.1f} KB → {new_size:.1f} KB (ahorro: {savings:.1f} KB)")
                
                converted += 1
                saved_kb += savings
                
            except Exception as e:
                print(f"❌ Error con {image_path.name}: {e}")
    
    print("-" * 50)
    if converted > 0:
        print(f"🎉 ¡Listo! Convertidas {converted} imágenes")
        print(f"💾 Ahorro total: {saved_kb:.1f} KB ({saved_kb/1024:.2f} MB)")
        print("\n📝 Ahora actualiza tu HTML para usar las versiones .webp")
    else:
        print("ℹ️  No se encontraron imágenes JPG/PNG para convertir")

if __name__ == "__main__":
    convert_to_webp()
