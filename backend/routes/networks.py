from fastapi import APIRouter

router = APIRouter()


@router.get("/networks")
async def get_networks(limit: int = 50):
    return [{"ssid": f"ZeusNet-{i}", "rssi": -30 - i} for i in range(limit)]
