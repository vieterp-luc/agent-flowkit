"""Setup 'Nếu Mặt Trời biến mất 24 giờ?' — What-if Day 1 (7 ROOT scenes).
Video via Meta AI. Run: python scripts/whatif_d1_setup.py → prints project/video/scene IDs.
"""
import json
import urllib.request

BASE = "http://127.0.0.1:8100"
STYLE = ("cinematic, hyper-realistic, photorealistic, dramatic atmospheric lighting, "
         "epic scale, vertical 9:16, no text")

# narrator VN (~20 từ) | image prompt EN | motion prompt EN
SCENES = [
    ("Nếu ngay bây giờ Mặt Trời đột ngột biến mất, bạn sẽ có đúng tám phút cuối cùng được nhìn thấy ánh sáng.",
     "the Sun vanishing from a bright daytime sky, sunlight draining away, Earth beginning to plunge toward darkness, cosmic view",
     "the Sun fading out of a daytime sky, light draining away as the scene slowly darkens, slow cosmic push-in"),
    ("Tám phút sau, bầu trời tắt lịm hoàn toàn, cả hành tinh chìm trong bóng tối vĩnh viễn giữa ban ngày.",
     "a busy city street at noon suddenly plunged into pitch black darkness, people frozen in shock, eerie",
     "a noon city street going pitch black in an instant, people freezing in place, lights flickering, eerie"),
    ("Chỉ trong một tuần, nhiệt độ rơi xuống âm mười tám độ, đại dương bắt đầu đóng băng dần từ trên bề mặt xuống.",
     "a vast ocean surface freezing over, ice spreading across dark waves, cold blue desolate seascape",
     "an ocean surface slowly freezing, ice crystals spreading across the waves, cold desolate, slow drift"),
    ("Cây cối chết hàng loạt vì không còn quang hợp, chuỗi thức ăn toàn cầu sụp đổ chỉ sau vài tháng ngắn ngủi.",
     "a vast forest withering and freezing under faint starlight, dead frozen trees, bleak dark atmosphere",
     "a frozen dying forest under starlight, frost creeping over dead trees, bleak, slow pan"),
    ("Các thành phố hoá thành nghĩa địa băng giá, ánh đèn cuối cùng vụt tắt khi toàn bộ lưới điện ngừng hoạt động.",
     "a frozen metropolis buried in ice and snow under a black starless sky, the last city lights dying out, epic desolate",
     "a frozen ice-covered city under a black sky, the last lights flickering out, epic desolate, slow aerial drift"),
    ("Một số ít người sống sót co cụm quanh lò phản ứng và miệng núi lửa, nơi duy nhất trên Trái Đất còn hơi ấm.",
     "a small group of survivors huddled around a glowing geothermal vent in total darkness, faint warm orange light, grim",
     "survivors huddled around a glowing geothermal vent in darkness, faint warm light flickering on their figures, grim, slow push-in"),
    ("Trái Đất trở thành một quả cầu băng trôi lặng lẽ trong vũ trụ, không còn một ai nhìn thấy bình minh nữa.",
     "planet Earth as a dark frozen ice sphere drifting silently in deep space, no sunlight, haunting cosmic",
     "Earth as a dark frozen sphere drifting silently in space, no sunlight, stars behind, haunting, very slow zoom out"),
]


def post(path, payload):
    req = urllib.request.Request(BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    proj = post("/api/projects", {
        "name": "Nếu Mặt Trời Biến Mất",
        "description": "What-if short: Mặt Trời biến mất 24 giờ",
        "story": "Viễn cảnh science-horror: nếu Mặt Trời đột ngột biến mất, Trái Đất chìm vào bóng tối và băng giá.",
        "material": "realistic"})
    pid = proj["id"]; print("project_id:", pid)
    vid = post("/api/videos", {"project_id": pid, "title": "Nếu Mặt Trời biến mất 24h",
        "video_story": "7 scene what-if", "display_order": 0, "orientation": "VERTICAL"})
    vid_id = vid["id"]; print("video_id:", vid_id)
    for i, (narr, img_p, vid_p) in enumerate(SCENES):
        s = post("/api/scenes", {"video_id": vid_id, "display_order": i,
            "prompt": f"{img_p}. {STYLE}.", "video_prompt": vid_p,
            "narrator_text": narr, "character_names": [], "chain_type": "ROOT"})
        # narrator_text not persisted on POST → PATCH it
        req = urllib.request.Request(f"{BASE}/api/scenes/{s['id']}",
            data=json.dumps({"narrator_text": narr}, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="PATCH")
        urllib.request.urlopen(req, timeout=20)
        print(f"scene_{i:02d}: {s['id']}")
    print("\nSUMMARY", json.dumps({"project_id": pid, "video_id": vid_id}))


if __name__ == "__main__":
    main()
