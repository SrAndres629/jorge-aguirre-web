"""
Utilidad de optimización de imágenes (Resize + WebP)
Redimensiona a 1024px ancho máximo y comprime a WebP q=80.
"""

import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("❌ Error: Pillow no está instalado. Ejecuta: pip install Pillow")
    exit(1)

IMAGES_DIR = Path("static/images")
MAX_WIDTH = 1024
QUALITY = 80
EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}

def optimize_image(image_path: Path) -> bool:
    """Redimensiona y convierte/optimiza a WebP."""
    try:
        # Calcular tamaño original
        original_size = image_path.stat().st_size
        
        with Image.open(image_path) as img:
            # 1. Convertir a RGB (manejo de transparencia)
            if img.mode in ('P', 'LA'):
                img = img.convert('RGBA')
            
            # Guardar referencia original para comparar después
            original_img = img.copy()

            # 2. Resize si es muy grande
            width, height = img.size
            if width > MAX_WIDTH:
                ratio = MAX_WIDTH / width
                new_height = int(height * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                print(f"   📏 Resize: {width}x{height} → {MAX_WIDTH}x{new_height}")

            # 3. Guardar como WebP
            # Si el input no es webp, el output cambia de extensión
            target_path = image_path.with_suffix('.webp')
            
            img.save(target_path, 'WEBP', quality=QUALITY)

        # 4. Verificar ahorro
        new_size = target_path.stat().st_size
        savings = (1 - new_size / original_size) * 100

        print(f"✅ Procesado: {image_path.name}")
        print(f"   📦 {original_size / 1024:.1f}KB → {new_size / 1024:.1f}KB ({savings:.0f}% ahorro)")

        # 5. Limpieza: si era JPG/PNG y ahora tenemos WebP, borrar original
        if image_path.suffix.lower() != '.webp' and target_path != image_path:
            os.remove(image_path)
            print(f"   🗑️  Eliminado original: {image_path.name}")
            
        return True

    except Exception as e:
        print(f"❌ Error procesando {image_path.name}: {e}")
        return False


def main():
    if not IMAGES_DIR.exists():
        print(f"❌ Directorio no encontrado: {IMAGES_DIR}")
        return
    
    print(f"🔍 Optimizando imágenes en: {IMAGES_DIR.absolute()}")
    print("-" * 50)
    
    count = 0
    
    for file_path in IMAGES_DIR.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in EXTENSIONS:
            if optimize_image(file_path):
                count += 1
    
    print("-" * 50)
    print(f"✨ Completado. {count} imágenes procesadas.")

if __name__ == "__main__":
    main()
