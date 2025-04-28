# Instalar imagen base
FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero en directorio de tabajo (Se cambia poco y optimiza la caché de Docker)
COPY pyproject.toml .

# Instalar dependencias
RUN pip install --no-cache-dir setuptools wheel

# Copiar el resto del código
COPY Casa_Monarca ./Casa_Monarca/
COPY app.py .

# Instalar la aplicación en modo editable (Por si hay cambios en el código y, consecuentemente, en el cache de Docker)
# Nota: Esto permite que los cambios en el código fuente se reflejen sin necesidad de reconstruir la imagen
RUN pip install --no-cache-dir -e .

# Crear directorio para los secretos
RUN mkdir -p /run/secrets

# Exponer el puerto que usa Flask
EXPOSE 5000

# Crear usuario no-root para mayor seguridad
RUN useradd -m appuser
# Ensure secrets directory is accessible
RUN chown -R appuser:appuser /run/secrets
USER appuser

# Configuración para asegurar que Flask escuche en todas las interfaces
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para ejecutar la aplicación
CMD python app.py