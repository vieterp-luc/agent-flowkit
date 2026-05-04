import asyncio
from pathlib import Path
from agent.services.flow_client import get_flow_client

async def main():
    client = get_flow_client()
    # Path from the log
    local_path = Path(r"C:\Users\tsundteo\Documents\Github-Projects\mz-flowkit\output\nhac_niem_phat_a_di_da\img\9c187dab-9416-4cb8-a1ca-75732bb313e8.jpg")
    if not local_path.exists():
        print("File does not exist locally.")
        return
        
    image_bytes = local_path.read_bytes()
    import base64
    image_b64 = base64.b64encode(image_bytes).decode()
    
    # We need a project ID, any valid one from DB is fine.
    # We'll use the one from the log if we know it, or just "test".
    print("Uploading...")
    result = await client.upload_image(image_b64, mime_type="image/jpeg", project_id="0", file_name=local_path.name)
    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
