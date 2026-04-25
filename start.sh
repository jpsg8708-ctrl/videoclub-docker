#!/usr/bin/env bash
set -e

echo ""
echo "======================================================"
echo "  Videoclub - arranque Docker"
echo "======================================================"

# --- 1. Verificar que Docker esta disponible ---------------------
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker no esta disponible en el PATH."
    exit 1
fi
echo "-> Docker detectado."

# --- 2. Detectar docker compose (plugin v2) o docker-compose (v1) -
if docker compose version &>/dev/null; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    echo "-> docker compose no esta disponible. Instalando docker-compose plugin..."
    sudo apt-get update -qq
    sudo apt-get install -y docker-compose-plugin -qq
    COMPOSE="docker compose"
fi
echo "-> Usando: ${COMPOSE}"

# --- 3. Construir y levantar -------------------------------------
echo ""
echo "-> Construyendo imagenes y levantando contenedores..."
${COMPOSE} up -d --build

# --- 4. Esperar a que el healthz responda ------------------------
echo ""
echo -n "-> Esperando a que la app este lista"
for i in $(seq 1 60); do
    if curl -fsS http://localhost:8080/healthz >/dev/null 2>&1; then
        echo " OK."
        break
    fi
    echo -n "."
    sleep 2
    if [ "$i" = "60" ]; then
        echo ""
        echo "AVISO: timeout esperando al healthcheck."
        echo "       Revisa 'docker compose logs app' para ver que pasa."
    fi
done

# --- 5. Estado final ---------------------------------------------
echo ""
${COMPOSE} ps

echo ""
echo "=============================================================="
echo "  Videoclub listo. Abre:  http://localhost:8080"
echo "=============================================================="
echo ""
echo "Para ver logs:   ${COMPOSE} logs -f"
echo "Para parar:      ${COMPOSE} down"
echo ""
