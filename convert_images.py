"""
Utilidad de conversión automática de imágenes a WebP
Ejecutar después de subir nuevas imágenes al directorio static/images/

Uso: python convert_images.py
"""

import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Error: Pillow no está instalado. Ejecuta: pip install Pillow")
    exit(1)

IMAGES_DIR = Path("static/images")
QUALITY = 85
EXTENSIONS_TO_CONVERT = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}


def convert_to_webp(image_path: Path) -> bool:
    """Convierte una imagen a WebP y elimina el original."""
    try:
        webp_path = image_path.with_suffix('.webp')
        
        # Si ya existe la versión WebP, solo eliminar original
        if webp_path.exists():
            print(f"⚠️  WebP ya existe: {webp_path.name}")
            os.remove(image_path)
            print(f"🗑️  Eliminado original: {image_path.name}")
            return True
        
        # Convertir a WebP
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario (para PNG con transparencia)
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(webp_path, 'WEBP', quality=QUALITY)
        
        # Obtener tamaños para mostrar ahorro
        original_size = image_path.stat().st_size
        webp_size = webp_path.stat().st_size
        savings = (1 - webp_size / original_size) * 100
        
        print(f"✅ Convertido: {image_path.name} → {webp_path.name}")
        print(f"   📦 {original_size / 1024:.1f}KB → {webp_size / 1024:.1f}KB ({savings:.0f}% ahorro)")
        
        # Eliminar original
        os.remove(image_path)
        print(f"🗑️  Eliminado original: {image_path.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando {image_path.name}: {e}")
        return False


def main():
    """Escanea el directorio de imágenes y convierte las que no sean WebP."""
    if not IMAGES_DIR.exists():
        print(f"❌ Directorio no encontrado: {IMAGES_DIR}")
        return
    
    print(f"🔍 Escaneando: {IMAGES_DIR.absolute()}")
    print("-" * 50)
    
    converted = 0
    skipped = 0
    
    for file_path in IMAGES_DIR.iterdir():
        if file_path.is_file():
            ext = file_path.suffix.lower()
            
            if ext in EXTENSIONS_TO_CONVERT:
                if convert_to_webp(file_path):
                    converted += 1
            elif ext == '.webp':
                skipped += 1
    
    print("-" * 50)
    print(f"📊 Resumen: {converted} convertidos, {skipped} WebP existentes")
    print("✨ Proceso completado")


if __name__ == "__main__":
    main()
