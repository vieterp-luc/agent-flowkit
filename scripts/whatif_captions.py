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
    # ── week 3 ──
    "neu_bao_mat_troi": (
        "Nếu siêu bão Mặt Trời đánh Trái Đất?",
        "Một cơn bão địa từ đủ mạnh có thể thổi bay lưới điện toàn cầu trong vài giờ — không điện, không internet, không nước máy. Sự kiện Carrington 1859 từng là lời cảnh báo.",
        "Bão Mặt Trời xoá sổ lưới điện cả hành tinh ☀️⚡",
        ["#baomattroi", "#diatu"]),
    "neu_sao_moc_bien_mat": (
        "Nếu Sao Mộc biến mất?",
        "Sao Mộc là 'lá chắn' hút thiên thạch thay Trái Đất. Mất nó, mưa sao băng tử thần đổ về phía ta nhiều gấp bội — và quỹ đạo cả Hệ Mặt Trời lung lay.",
        "Sao Mộc biến mất, Trái Đất mất lá chắn 🪐☄️",
        ["#saomoc", "#thaiduonghe"]),
    "neu_trai_dat_to_gap_doi": (
        "Nếu Trái Đất to gấp đôi?",
        "Trọng lực tăng vọt khiến mọi sinh vật nặng gấp đôi, núi non thấp lại, bầu khí quyển dày đặc hơn. Cơ thể bạn sẽ không chịu nổi sức nặng của chính mình.",
        "Trái Đất to gấp đôi, trọng lực nghiền nát bạn 🌍💪",
        ["#traidat", "#trongluc"]),
    "neu_sieu_nui_lua_yellowstone": (
        "Nếu siêu núi lửa Yellowstone thức giấc?",
        "Một vụ phun trào có thể chôn vùi nửa nước Mỹ dưới tro, đẩy cả hành tinh vào mùa đông núi lửa kéo dài nhiều năm. Quả bom hẹn giờ đang ngủ dưới chân chúng ta.",
        "Siêu núi lửa Yellowstone thức giấc 🌋❄️",
        ["#yellowstone", "#sieunuilua"]),
    "neu_hai_mat_troi": (
        "Nếu Trái Đất có hai Mặt Trời?",
        "Hoàng hôn đôi tuyệt đẹp, nhưng quỹ đạo Trái Đất trở nên hỗn loạn, nhiệt độ dao động cực đoan giữa thiêu đốt và đóng băng. Sự sống khó lòng tồn tại.",
        "Bầu trời hai Mặt Trời trông như thế này ☀️☀️",
        ["#haimattroi", "#thienvan"]),
    "neu_bang_tan_het": (
        "Nếu toàn bộ băng trên Trái Đất tan hết?",
        "Mực nước biển dâng 66 mét, nhấn chìm mọi thành phố ven biển. Bản đồ thế giới vẽ lại, hàng tỉ người mất nhà — và quá trình này đang diễn ra.",
        "Băng tan hết, nước biển dâng 66m 🧊🌊",
        ["#bangtan", "#biendoikhihau"]),
    "neu_tieu_hanh_tinh_dam": (
        "Nếu một tiểu hành tinh khổng lồ đâm Trái Đất?",
        "Một khối đá 10km như đã xoá sổ khủng long sẽ tạo sóng thần cao ngàn mét, hoả ngục bao trùm bầu trời, rồi mùa đông tăm tối. Lịch sử có thể lặp lại.",
        "Tiểu hành tinh đâm Trái Đất như xoá sổ khủng long ☄️🦖",
        ["#tieuhanhtinh", "#khunglong"]),
    # ── week 4 ──
    "neu_trai_dat_quay_nguoc": (
        "Nếu Trái Đất quay ngược?",
        "Gió đổi chiều, sa mạc Sahara hoá xanh tươi còn rừng Amazon thành cát bụi. Dòng hải lưu và khí hậu toàn cầu bị đảo lộn hoàn toàn.",
        "Trái Đất quay ngược, Sahara hoá rừng xanh 🌍🔄",
        ["#traidat", "#khihau"]),
    "neu_mat_troi_mo_di": (
        "Nếu Mặt Trời mờ đi một nửa?",
        "Chỉ cần Mặt Trời giảm một nửa độ sáng, Trái Đất lao vào kỷ băng hà sâu, đại dương đóng băng dần từ hai cực. Cây cối chết vì thiếu ánh sáng quang hợp.",
        "Mặt Trời mờ một nửa = kỷ băng hà 🌑❄️",
        ["#mattroi", "#bangha"]),
    "neu_ngay_dai_48h": (
        "Nếu một ngày dài 48 giờ?",
        "24 giờ nắng cháy rồi 24 giờ băng giá — nhiệt độ dao động khủng khiếp giữa ngày và đêm. Nhịp sinh học của mọi sinh vật sụp đổ.",
        "Một ngày dài 48 giờ, nửa thiêu nửa đóng băng ☀️🌙",
        ["#thoigian", "#traidat"]),
    "neu_khi_quyen_day_gap_doi": (
        "Nếu bầu khí quyển dày gấp đôi?",
        "Áp suất nghiền nát, hiệu ứng nhà kính tăng vọt biến Trái Đất thành lò nung. Nhưng bầu trời hoàng hôn sẽ rực rỡ hơn bao giờ hết.",
        "Khí quyển dày gấp đôi, Trái Đất hoá lò nung 🌫️🔥",
        ["#khiquyen", "#nhakinh"]),
    "neu_nuoc_ngot_bien_mat": (
        "Nếu toàn bộ nước ngọt biến mất?",
        "Chỉ 3% nước trên Trái Đất là nước ngọt — mất nó, cây cối héo úa, mùa màng thất bát, văn minh sụp đổ trong vài ngày. Khát là kẻ thù chết chóc nhất.",
        "Nước ngọt biến mất, văn minh sụp trong vài ngày 💧💀",
        ["#nuocngot", "#hanhan"]),
    "neu_trai_dat_khoa_thuy_trieu": (
        "Nếu Trái Đất bị khoá thuỷ triều với Mặt Trời?",
        "Một nửa hành tinh chìm trong ngày vĩnh cửu thiêu đốt, nửa kia là đêm băng giá bất tận. Sự sống chỉ còn cơ hội ở dải hoàng hôn mỏng manh.",
        "Nửa Trái Đất cháy nắng, nửa kia đóng băng mãi mãi 🌗",
        ["#thuytrieu", "#traidat"]),
    "neu_tu_truong_dao_cuc": (
        "Nếu từ trường Trái Đất đảo cực?",
        "La bàn chỉ ngược, lá chắn từ trường suy yếu cho bức xạ Mặt Trời lọt vào. Điều đáng sợ: chuyện này từng xảy ra nhiều lần và có thể sắp lặp lại.",
        "Từ trường đảo cực, la bàn chỉ ngược 🧭🔄",
        ["#tutruong", "#daocuc"]),
    # ── week 5-6 (bỏ loai_nguoi) ──
    "neu_mat_trang_bien_mat": (
        "Nếu Mặt Trăng biến mất?",
        "Mất Mặt Trăng, thuỷ triều biến mất và trục Trái Đất bắt đầu lảo đảo. Người bạn bốn tỉ năm ra đi kéo theo cả nhịp sống của hành tinh.",
        "Mặt Trăng biến mất, Trái Đất mất nhịp sống 🌑",
        ["#mattrang", "#thuytrieu"]),
    "neu_anh_sang_cham_lai": (
        "Nếu tốc độ ánh sáng chậm lại?",
        "Chỉ cần ánh sáng chậm đi, mọi định luật vật lý rạn nứt, Mặt Trời thất thường và thực tại tan rã trong lặng lẽ.",
        "Ánh sáng chậm lại = vũ trụ tan rã 💫",
        ["#anhsang", "#vatly"]),
    "neu_trai_dat_mat_nua_khoi_luong": (
        "Nếu Trái Đất mất một nửa khối lượng?",
        "Trọng lực yếu đi, khí quyển rò ra vũ trụ, đại dương bốc hơi. Một Trái Đất hao gầy là một Trái Đất đang hấp hối.",
        "Trái Đất nhẹ đi một nửa, khí quyển bay mất 🌍",
        ["#traidat", "#trongluc"]),
    "neu_bau_troi_khong_sao": (
        "Nếu bầu trời đêm không còn ngôi sao?",
        "Vũ trụ giãn nở kéo các thiên hà ra xa mãi mãi. Một ngày bầu trời đêm sẽ đen tuyệt đối, và ta cô độc giữa vũ trụ.",
        "Bầu trời đêm không còn một ngôi sao 🌌",
        ["#vutru", "#thienha"]),
    "neu_vi_khuan_bien_mat": (
        "Nếu mọi vi khuẩn biến mất?",
        "Phân huỷ ngừng, tiêu hoá tê liệt, chuỗi thức ăn vỡ vụn. Kẻ thù vô hình hoá ra là người bạn thầm lặng giữ ta sống.",
        "Vi khuẩn biến mất, thế giới chết dần 🦠",
        ["#vikhuan", "#sinhhoc"]),
    "neu_trai_dat_co_vanh_dai": (
        "Nếu Trái Đất có vành đai như Sao Thổ?",
        "Bầu trời đẹp nghẹt thở với dải sáng vắt ngang, nhưng bóng vành đai phủ giá lạnh và giam ta dưới chiếc lồng ánh sáng.",
        "Trái Đất đeo vành đai như Sao Thổ 🪐",
        ["#vanhdai", "#saotho"]),
    "neu_sieu_tan_tinh_no_gan": (
        "Nếu siêu tân tinh nổ gần Trái Đất?",
        "Ánh sáng chói loà tuyệt đẹp, rồi bức xạ gamma xé toạc tầng ozone. Cái chết của một ngôi sao đủ kết liễu cả hành tinh.",
        "Siêu tân tinh nổ gần, ozone bị xé toạc ☄️",
        ["#sieutantinh", "#buxa"]),
    "neu_trai_dat_roi_vao_mat_troi": (
        "Nếu Trái Đất rơi vào Mặt Trời?",
        "Đại dương sôi cạn, đất đá nóng chảy, khí quyển bị thổi bay. Ngôi nhà của ta trở về với ngọn lửa đã sinh ra nó.",
        "Trái Đất rơi vào Mặt Trời, hoá cầu lửa ☀️🔥",
        ["#mattroi", "#vutru"]),
    "neu_mat_troi_tat_1_nam": (
        "Nếu Mặt Trời tắt trong 1 năm?",
        "Sương giá phủ cả vùng nhiệt đới, đại dương đóng băng, quang hợp ngừng. Một năm không nắng dạy ta nắng là phép màu.",
        "Mặt Trời tắt 1 năm, Trái Đất hoá băng ❄️",
        ["#mattroi", "#bangha"]),
    "neu_toan_bo_cay_xanh_chet": (
        "Nếu toàn bộ cây xanh chết?",
        "Nguồn oxy ngừng, không khí ngột ngạt, chuỗi thức ăn sụp từ gốc rễ. Mỗi chiếc lá xanh là một hơi thở ta nhận miễn phí.",
        "Cây xanh chết hết, oxy cạn dần 🌳💀",
        ["#cayxanh", "#oxy"]),
    "neu_trong_luc_gap_doi": (
        "Nếu trọng lực mạnh gấp đôi?",
        "Xương oằn, tim quá tải, nhà cao tầng sập. Trọng lực dịu dàng bấy lâu mới là điều cho ta đứng thẳng.",
        "Trọng lực gấp đôi, mọi thứ bị nghiền 💪",
        ["#trongluc", "#vatly"]),
    "neu_trai_dat_hanh_tinh_bang": (
        "Nếu Trái Đất hoá hành tinh băng?",
        "Băng lan tới tận xích đạo, đại dương đóng cứng, sự sống co cụm quanh núi lửa. Snowball Earth từng xảy ra thật.",
        "Trái Đất hoá quả cầu tuyết khổng lồ 🧊",
        ["#bangha", "#snowballearth"]),
    "neu_sieu_song_than_toan_cau": (
        "Nếu một siêu sóng thần quét toàn cầu?",
        "Sườn núi lửa sụp xuống biển tạo sóng cao ngàn mét, nhấn chìm thành phố ven biển, vẽ lại bản đồ thế giới bằng nước.",
        "Siêu sóng thần ngàn mét quét toàn cầu 🌊",
        ["#songthan", "#thamhoa"]),
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
