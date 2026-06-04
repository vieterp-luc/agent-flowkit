"""Generate caption.txt for each What-if video → output/whatif/<slug>/caption.txt.
Caption gồm: Title (Shorts) + Facebook Reels caption + TikTok caption + hashtag mỗi nền.
Run: python scripts/whatif_captions.py
"""
import os

FB_BASE = ["#whatif", "#khoahoc", "#vutru", "#traidat", "#kienthuc", "#khampha", "#WhatIfVN", "#science"]
TT_BASE = ["#fyp", "#xuhuong", "#foryou", "#whatif", "#khoahoc", "#kienthuc",
           "#vutru", "#WhatIfVN", "#LearnOnTikTok", "#khampha"]

# slug: (title, fb_caption, tiktok_caption, [topic_tags])
DATA = {
    "neu_mat_troi_bien_mat": (
        "Nếu Mặt Trời biến mất 24 giờ?",
        "Bạn sẽ chỉ còn đúng 8 phút cuối cùng được nhìn thấy ánh sáng. Sau một tuần, đại dương bắt đầu đóng băng. Điều gì xảy ra tiếp theo sẽ khiến bạn lạnh sống lưng.",
        "8 phút cuối cùng thấy ánh sáng… rồi cả Trái Đất hoá băng 🥶☀️",
        ["#mattroi", "#bangha"]),
    "neu_trong_luc_bien_mat": (
        "Nếu trọng lực biến mất 5 giây?",
        "Chỉ 5 giây thôi cũng đủ để mọi thứ không cố định bay lên trời, rồi rơi sầm xuống xoá sổ cả nền văn minh. Bạn có dám tưởng tượng?",
        "5 giây mất trọng lực = tận thế 😱🌍",
        ["#trongluc", "#vatly"]),
    "neu_dai_duong_can_kho": (
        "Nếu đại dương cạn khô?",
        "Lần đầu tiên bạn sẽ thấy đáy biển: hàng triệu xác tàu, những vực thẳm khổng lồ, và 70% hành tinh hoá thành nghĩa địa khô cằn.",
        "Đáy đại dương lộ ra trông như thế này… 🌊💀",
        ["#daiduong", "#bian"]),
    "neu_loai_nguoi_bien_mat": (
        "Nếu loài người biến mất ngày mai?",
        "Chỉ vài thế kỷ, thiên nhiên nuốt chửng mọi thành phố. Trái Đất không hề cần chúng ta — và nó sẽ xanh tươi trở lại như chưa từng có loài người.",
        "Trái Đất sau khi loài người biến mất 🌿🏙️",
        ["#loainguoi", "#thiennhien"]),
    "neu_trai_dat_ngung_quay": (
        "Nếu Trái Đất ngừng quay?",
        "Gió siêu bão hơn 1600 km/h quét sạch mọi thứ, một nửa hành tinh cháy nắng, nửa kia đóng băng vĩnh cửu. Một vòng quay là tất cả những gì giữ ta sống.",
        "Trái Đất ngừng quay và đây là điều xảy ra 🌍💨",
        ["#traidat", "#thienvanhoc"]),
    "neu_khong_bao_gio_ngu": (
        "Nếu bạn không bao giờ ngủ lại được?",
        "Đây là căn bệnh có thật: một khi khởi phát, bạn không bao giờ ngủ được nữa — tỉnh táo cho đến lúc chết. Giấc ngủ giữ bạn sống mà bạn không hề hay biết.",
        "Căn bệnh khiến bạn KHÔNG BAO GIỜ ngủ được nữa 😨🛌",
        ["#giacngu", "#suckhoe"]),
    "neu_mat_trang_roi": (
        "Nếu Mặt Trăng rơi xuống Trái Đất?",
        "Thuỷ triều nhấn chìm bờ biển, núi lửa bùng nổ, rồi Mặt Trăng vỡ thành mưa thiên thạch lửa. Người bạn 4 tỉ năm cũng là kẻ huỷ diệt.",
        "Mặt Trăng rơi xuống Trái Đất thì sao? 🌕🔥",
        ["#mattrang", "#vutru"]),
    "neu_oxy_bien_mat": (
        "Nếu oxy biến mất 5 giây?",
        "Mọi người ngất xỉu, các toà nhà bê tông vụn rã thành bụi, bầu trời tối sầm giữa ban ngày. Chỉ 5 giây đủ biến văn minh thành đống đổ nát.",
        "5 giây không oxy và bê tông tan thành bụi 😱",
        ["#oxy", "#khongkhi"]),
    "neu_mat_tu_truong": (
        "Nếu Trái Đất mất từ trường?",
        "Lá chắn vô hình bảo vệ ta tan biến, gió Mặt Trời bào mòn khí quyển y như đã xảy ra trên Sao Hoả. Cực quang đẹp đến chết người tràn khắp bầu trời.",
        "Mất từ trường, Trái Đất thành Sao Hoả thứ hai 🧲🔴",
        ["#tutruong", "#saohoa"]),
    "neu_nui_lua_phun": (
        "Nếu tất cả núi lửa phun cùng lúc?",
        "Bầu trời biến mất sau bức màn tro bụi, cả hành tinh chìm vào mùa đông núi lửa lạnh giá. Một khoảnh khắc Trái Đất nổi giận là đủ.",
        "Tất cả núi lửa phun cùng lúc = mùa đông tận thế 🌋",
        ["#nuilua", "#thamhoa"]),
    "neu_nuoc_bien_dang": (
        "Nếu nước biển dâng 100 mét?",
        "New York, Thượng Hải, Mumbai biến mất dưới làn nước — chỉ còn vài đỉnh toà nhà nhô lên. Bản đồ thế giới được vẽ lại hoàn toàn.",
        "Nước biển dâng 100m, thành phố chìm hết 🌊🏙️",
        ["#nuocbien", "#biendoikhihau"]),
    "neu_ho_den_bay_qua": (
        "Nếu một hố đen bay qua Hệ Mặt Trời?",
        "Ta sẽ không thấy nó cho đến khi quá muộn. Quỹ đạo các hành tinh vỡ tan, bầu trời méo mó kỳ dị. Một vị khách vô hình xoá sổ cả thế giới trong lặng lẽ.",
        "Hố đen lang thang ghé thăm Hệ Mặt Trời 🕳️🪐",
        ["#hoden", "#vutru"]),
    "neu_con_trung_bien_mat": (
        "Nếu loài côn trùng biến mất hoàn toàn?",
        "Sự sụp đổ bắt đầu âm thầm: cây ngừng kết trái, chuỗi thức ăn vỡ vụn, nạn đói quét qua các châu lục. Sinh vật bé nhỏ nhất lại giữ cả thế giới sống sót.",
        "Côn trùng biến mất và đây là hậu quả 🐝💀",
        ["#contrung", "#hesinhthai"]),
    "neu_mat_troi_phinh_to": (
        "Nếu Mặt Trời phình thành sao khổng lồ đỏ?",
        "Nó nuốt chửng Sao Thuỷ, Sao Kim, rồi đến Trái Đất — đại dương sôi cạn, lục địa hoá biển dung nham. Số phận này chờ ta sau 5 tỉ năm.",
        "Mặt Trời phình to nuốt chửng Trái Đất ☀️🔥",
        ["#mattroi", "#saodo"]),
}


def main():
    for slug, (title, fb, tt, topic) in DATA.items():
        fbh = " ".join(FB_BASE + topic)
        tth = " ".join(TT_BASE + topic)
        text = (
            f"=== {title} ===\n\n"
            f"TITLE (YouTube Shorts):\n{title} #Shorts\n\n"
            f"--- FACEBOOK REELS ---\n{fb}\n\nHashtag FB:\n{fbh}\n\n"
            f"--- TIKTOK ---\n{tt}\n\nHashtag TikTok:\n{tth}\n"
        )
        d = f"output/whatif/{slug}"
        if not os.path.isdir(d):
            print(f"skip (no folder): {slug}")
            continue
        open(f"{d}/caption.txt", "w").write(text)
        print(f"✓ {slug}/caption.txt")


if __name__ == "__main__":
    main()
