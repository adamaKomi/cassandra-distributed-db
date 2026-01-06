"""
API REST FastAPI pour le monitoring de capteurs IoT
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from config import settings
from database import db
from models import (
    SensorReading,
    SensorInfo,
    SensorStats,
    SensorHistoryResponse,
    HealthResponse
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    # Démarrage
    logger.info("Démarrage de l'API...")
    try:
        db.connect()
        logger.info("Connexion à Cassandra établie")
    except Exception as e:
        logger.error(f"Impossible de se connecter à Cassandra: {e}")
    
    yield
    
    # Arrêt
    logger.info("Arrêt de l'API...")
    db.disconnect()


# Création de l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API REST pour consulter les données des capteurs IoT stockées dans Cassandra",
    lifespan=lifespan
)

# Configuration CORS pour permettre l'accès depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "IoT Sensor Monitoring API",
        "version": settings.app_version,
        "endpoints": {
            "health": "/health",
            "sensors": "/sensors",
            "sensor_latest": "/sensors/{sensor_id}/latest",
            "sensor_history": "/sensors/{sensor_id}/history"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Vérifier l'état de santé de l'API et de la connexion Cassandra"""
    try:
        cluster_status = db.get_cluster_status()
        
        return HealthResponse(
            status="healthy" if cluster_status["connected"] else "unhealthy",
            cassandra_connected=cluster_status["connected"],
            cassandra_nodes=[node["address"] for node in cluster_status.get("nodes", [])],
            message="API opérationnelle" if cluster_status["connected"] else "Cassandra non connecté"
        )
    except Exception as e:
        logger.error(f"Erreur lors du health check: {e}")
        return HealthResponse(
            status="unhealthy",
            cassandra_connected=False,
            cassandra_nodes=[],
            message=str(e)
        )


@app.get("/sensors", response_model=List[SensorInfo], tags=["Sensors"])
async def get_all_sensors():
    """
    Obtenir la liste de tous les capteurs avec leur dernière lecture
    """
    try:
        sensor_ids = db.get_all_sensors()
        
        if not sensor_ids:
            return []
        
        sensors_info = []
        for sensor_id in sensor_ids:
            latest = db.get_latest_reading(sensor_id)
            stats = db.get_sensor_stats(sensor_id)
            
            sensor_info = SensorInfo(
                sensor_id=sensor_id,
                last_reading=SensorReading(**latest) if latest else None,
                stats=SensorStats(**stats) if stats else None,
                total_readings=0  # Pourrait être calculé si nécessaire
            )
            sensors_info.append(sensor_info)
        
        return sensors_info
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des capteurs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensors/{sensor_id}", response_model=SensorInfo, tags=["Sensors"])
async def get_sensor_info(sensor_id: str):
    """
    Obtenir les informations et statistiques d'un capteur spécifique
    """
    try:
        # Vérifier si le capteur existe
        sensor_ids = db.get_all_sensors()
        if sensor_id not in sensor_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Capteur {sensor_id} non trouvé"
            )
            
        latest = db.get_latest_reading(sensor_id)
        stats = db.get_sensor_stats(sensor_id)
        
        return SensorInfo(
            sensor_id=sensor_id,
            last_reading=SensorReading(**latest) if latest else None,
            stats=SensorStats(**stats) if stats else None,
            total_readings=0
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des infos du capteur: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensors/{sensor_id}/latest", response_model=SensorReading, tags=["Sensors"])
async def get_sensor_latest(sensor_id: str):
    """
    Obtenir la dernière lecture d'un capteur spécifique
    
    - **sensor_id**: Identifiant du capteur (ex: sensor_01)
    """
    try:
        latest = db.get_latest_reading(sensor_id)
        
        if not latest:
            raise HTTPException(
                status_code=404, 
                detail=f"Aucune donnée trouvée pour le capteur {sensor_id}"
            )
        
        return SensorReading(**latest)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la dernière lecture: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sensors/{sensor_id}/history", response_model=SensorHistoryResponse, tags=["Sensors"])
async def get_sensor_history(
    sensor_id: str,
    limit: int = Query(default=100, ge=1, le=1000, description="Nombre maximum de lectures à retourner"),
    hours: Optional[int] = Query(default=None, ge=1, description="Nombre d'heures d'historique")
):
    """
    Obtenir l'historique des lectures d'un capteur
    
    - **sensor_id**: Identifiant du capteur (ex: sensor_01)
    - **limit**: Nombre maximum de lectures à retourner (1-1000, défaut: 100)
    - **hours**: Optionnel - Limiter aux N dernières heures
    """
    try:
        start_time = None
        end_time = None
        
        if hours:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
        
        readings = db.get_sensor_history(
            sensor_id=sensor_id,
            limit=limit,
            start_time=start_time,
            end_time=end_time
        )
        
        if not readings:
            # Vérifier si le capteur existe
            all_sensors = db.get_all_sensors()
            if sensor_id not in all_sensors:
                raise HTTPException(
                    status_code=404,
                    detail=f"Capteur {sensor_id} non trouvé"
                )
            
            # Le capteur existe mais n'a pas de données dans la période demandée
            return SensorHistoryResponse(
                sensor_id=sensor_id,
                readings=[],
                count=0
            )
        
        return SensorHistoryResponse(
            sensor_id=sensor_id,
            readings=[SensorReading(**r) for r in readings],
            count=len(readings)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'historique: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cluster/status", tags=["Cluster"])
async def get_cluster_status():
    """
    Obtenir le statut du cluster Cassandra
    """
    try:
        return db.get_cluster_status()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du cluster: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
