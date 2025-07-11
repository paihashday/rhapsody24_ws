from fastapi import FastAPI
from database import config
from routes import project_routes, switchboard_routes, switch_routes, audioboard_routes, audiotrack_routes, dht_routes, color_routes

config.Base.metadata.create_all(bind=config.engine)
app = FastAPI(
    title="Rhapsody24 Server -  API",
    summary="Rhapsody server's control API",
    version="0.0.1"
)

app.include_router(project_routes.router, tags=["Projects"], prefix="/projects")
app.include_router(switchboard_routes.router, tags=["Switchboards"], prefix="/switchboards")
app.include_router(switch_routes.router, tags=["Switchs"], prefix="/switchs")
app.include_router(audioboard_routes.router, tags=["Audioboards"], prefix="/audioboards")
app.include_router(audiotrack_routes.router, tags=["Audiotracks"], prefix="/audiotracks")
app.include_router(dht_routes.router, tags=["DHT sensors"], prefix="/dht")
app.include_router(color_routes.router, tags=["Colors"], prefix="/color")