# app/Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# Cria usuário não‑root
RUN useradd -m -s /bin/bash appuser && chown -R appuser:appuser /app

# Copia dependências do builder
COPY --from=builder /root/.local /home/appuser/.local

# Copia código da aplicação
COPY . .

# Ajusta permissões e PATH
ENV PATH=/home/appuser/.local/bin:$PATH
USER appuser

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]